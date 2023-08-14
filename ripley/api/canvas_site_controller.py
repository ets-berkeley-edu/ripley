"""
Copyright ©2023. The Regents of the University of California (Regents). All Rights Reserved.

Permission to use, copy, modify, and distribute this software and its documentation
for educational, research, and not-for-profit purposes, without fee and without a
signed licensing agreement, is hereby granted, provided that the above copyright
notice, this paragraph and the following two paragraphs appear in all copies,
modifications, and distributions.

Contact The Office of Technology Licensing, UC Berkeley, 2150 Shattuck Avenue,
Suite 510, Berkeley, CA 94720-1620, (510) 643-7201, otl@berkeley.edu,
http://ipira.berkeley.edu/industry-info for commercial licensing opportunities.

IN NO EVENT SHALL REGENTS BE LIABLE TO ANY PARTY FOR DIRECT, INDIRECT, SPECIAL,
INCIDENTAL, OR CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF
THE USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF REGENTS HAS BEEN ADVISED
OF THE POSSIBILITY OF SUCH DAMAGE.

REGENTS SPECIFICALLY DISCLAIMS ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. THE
SOFTWARE AND ACCOMPANYING DOCUMENTATION, IF ANY, PROVIDED HEREUNDER IS PROVIDED
"AS IS". REGENTS HAS NO OBLIGATION TO PROVIDE MAINTENANCE, SUPPORT, UPDATES,
ENHANCEMENTS, OR MODIFICATIONS.
"""

from itertools import groupby

from flask import current_app as app, redirect, request
from flask_login import current_user, login_required
from ripley.api.errors import BadRequestError, InternalServerError, ResourceNotFoundError
from ripley.api.util import canvas_role_required, csv_download_response
from ripley.externals import canvas, data_loch
from ripley.externals.data_loch import get_basic_profile_and_grades_per_enrollments
from ripley.externals.redis import enqueue, get_job
from ripley.lib.berkeley_course import course_to_api_json, section_to_api_json, sort_course_sections
from ripley.lib.berkeley_term import BerkeleyTerm
from ripley.lib.canvas_utils import canvas_section_to_api_json, canvas_site_to_api_json, prepare_egrade_export, \
    update_canvas_sections
from ripley.lib.http import tolerant_jsonify
from ripley.lib.util import to_bool_or_none
from ripley.merged.grade_distributions import get_grade_distribution_with_demographics, get_grade_distribution_with_enrollments
from ripley.merged.roster import canvas_site_roster, canvas_site_roster_csv
from ripley.models.job_history import JobHistory


@app.route('/api/canvas_site/provision')
def canvas_site_provision():
    return tolerant_jsonify([])


@app.route('/api/canvas_site/<canvas_site_id>')
def get_canvas_site(canvas_site_id):
    course = canvas.get_course(canvas_site_id)
    if course:
        api_json = canvas_site_to_api_json(course)
        include_users = to_bool_or_none(request.args.get('includeUsers', False))
        if include_users:
            users = []
            for user in course.get_users(include=('email', 'enrollments')):
                users.append({
                    'id': user.id,
                    'enrollments': user.enrollments,
                    'name': user.name,
                    'sortableName': user.sortable_name,
                    'uid': user.login_id if hasattr(user, 'login_id') else None,
                    'url': f"{app.config['CANVAS_API_URL']}/courses/{canvas_site_id}/users/{user.id}",
                })
            api_json['users'] = sorted(users, key=lambda u: u['sortableName'])
        return tolerant_jsonify(api_json)
    else:
        raise ResourceNotFoundError(f'No Canvas course site found with ID {canvas_site_id}')


@app.route('/api/canvas_site/<canvas_site_id>/provision/sections', methods=['POST'])
@canvas_role_required('TeacherEnrollment', 'Lead TA')
def edit_sections(canvas_site_id):
    course = canvas.get_course(canvas_site_id)
    if not course:
        raise ResourceNotFoundError(f'No Canvas course site found with ID {canvas_site_id}')
    params = request.get_json()
    section_ids_to_add = params.get('sectionIdsToAdd', [])
    section_ids_to_remove = params.get('sectionIdsToRemove', [])
    section_ids_to_update = params.get('sectionIdsToUpdate', [])
    all_section_ids = section_ids_to_add + section_ids_to_remove + section_ids_to_update
    if not len(all_section_ids):
        raise BadRequestError('Required parameters are missing.')
    job = enqueue(func=update_canvas_sections, args=(course, all_section_ids, section_ids_to_remove))
    if not job:
        raise InternalServerError('Updates cannot be completed at this time.')
    return tolerant_jsonify(
        {
            'jobId': job.id,
            'jobStatus': 'sendingRequest',
        },
    )


@app.route('/api/canvas_site/<canvas_site_id>/grade_distribution')
@canvas_role_required('TeacherEnrollment', 'Lead TA')
def get_grade_distribution(canvas_site_id):
    course = canvas.get_course(canvas_site_id)
    canvas_sections = canvas.get_course_sections(canvas_site_id)
    sis_sections = [canvas_section_to_api_json(cs) for cs in canvas_sections if cs.sis_section_id]
    distribution = {
        'canvasSite': canvas_site_to_api_json(course),
        'officialSections': sis_sections,
    }
    if sis_sections:
        term_id = sis_sections[0]['termId']
        section_ids = [s['id'] for s in sis_sections]
        demographics = get_grade_distribution_with_demographics(term_id, section_ids)
        distribution['demographics'] = demographics
        grades = {d['grade']: {
            'classSize': d['classSize'],
            'count': d['count'],
            'percentage': d['percentage'],
        } for d in demographics}
        distribution['enrollments'] = get_grade_distribution_with_enrollments(term_id, section_ids, grades)
    else:
        distribution['demographics'] = []
        distribution['enrollments'] = {}
    return tolerant_jsonify(distribution)


@app.route('/api/canvas_site/<canvas_site_id>/provision/sections')
@canvas_role_required('DesignerEnrollment', 'TeacherEnrollment', 'TaEnrollment', 'Lead TA', 'Reader')
def get_official_sections(canvas_site_id):
    can_edit = bool(next((role for role in current_user.canvas_site_user_roles if role in ['TeacherEnrollment', 'Lead TA']), None))
    course = canvas.get_course(canvas_site_id)
    if not course:
        raise ResourceNotFoundError(f'No Canvas course site found with ID {canvas_site_id}')
    canvas_sis_term_id = course.term['sis_term_id']
    term = BerkeleyTerm.from_canvas_sis_term_id(canvas_sis_term_id)
    official_sections, section_ids, sections = _get_official_sections(canvas_site_id)
    teaching_terms = [] if not len(section_ids) else _get_teaching_terms(section_ids, sections)
    return tolerant_jsonify({
        'canvasSite': {
            'canEdit': can_edit,
            'officialSections': official_sections,
            'term': term.to_api_json(),
        },
        'teachingTerms': teaching_terms,
    })


@app.route('/api/canvas_site/provision/status')
@canvas_role_required('TeacherEnrollment')
def get_provision_status():
    job_id = request.args.get('jobId', None)
    if not job_id:
        raise BadRequestError('Required parameters are missing.')

    job = get_job(job_id)
    job_status = job.get_status(refresh=True)
    job_data = job.get_meta(refresh=True)
    if 'enrollment_update_job_id' in job_data:
        enrollment_update_job = JobHistory.get_by_id(job_data['enrollment_update_job_id'])
        if enrollment_update_job.failed:
            job_status = 'failed'
        elif enrollment_update_job.finished_at:
            job_status = 'finished'
        else:
            job_status = 'started'
    if 'sis_import_id' in job_data:
        sis_import = canvas.get_sis_import(job_data['sis_import_id'])
        if not sis_import:
            raise ResourceNotFoundError(f'No SIS import with {job_data} was found.')
        return tolerant_jsonify({
            'jobStatus': job_status,
            'workflowState': sis_import.workflow_state,
            'messages': getattr(sis_import, 'processing_warnings', []),
        })
    return tolerant_jsonify({
        'jobStatus': job_status,
    })


@app.route('/api/canvas_site/egrade_export/options')
@canvas_role_required('TeacherEnrollment')
def egrade_export_options():
    course_settings = canvas.get_course_settings(current_user.canvas_site_id)
    official_sections, section_ids, sections = _get_official_sections(current_user.canvas_site_id)
    return tolerant_jsonify({
        'gradingStandardEnabled': course_settings['grading_standard_enabled'],
        'officialSections': [s for s in official_sections if s['id']],
        'sectionTerms': [] if not len(section_ids) else _get_teaching_terms(section_ids, sections),
    })


@app.route('/api/canvas_site/<canvas_site_id>/egrade_export/prepare', methods=['POST'])
def egrade_export_prepare(canvas_site_id):
    course = canvas.get_course(canvas_site_id)
    if not course:
        raise ResourceNotFoundError(f'No Canvas course site found with ID {canvas_site_id}')
    job = enqueue(func=prepare_egrade_export, args=[canvas_site_id])
    if not job:
        raise InternalServerError('Updates cannot be completed at this time.')
    return tolerant_jsonify(
        {
            'jobId': job.id,
            'jobRequestStatus': 'Success',
        },
    )


@app.route('/api/canvas_site/egrade_export/download')
def egrade_export_download():
    params = request.args
    grade_type = params.get('gradeType', None)
    pnp_cutoff = params.get('pnpCutoff', None)
    section_id = params.get('sectionId', None)
    term_id = params.get('termId', None)

    if None in [grade_type, pnp_cutoff, section_id, term_id]:
        raise BadRequestError('Required parameter(s) are missing')
    if grade_type not in ['current', 'final']:
        raise BadRequestError(f'Invalid gradeType value: {grade_type}')
    letter_grades = ['A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F']
    if pnp_cutoff not in letter_grades and pnp_cutoff != 'ignore':
        raise BadRequestError(f'Invalid pnpCutoff value: {pnp_cutoff}')

    rows = []
    for row in get_basic_profile_and_grades_per_enrollments(term_id=term_id, section_ids=[section_id]):
        grading_basis = (row['grading_basis'] or '').upper()
        comment = None
        if grading_basis in ['CPN', 'DPN', 'EPN', 'PNP']:
            comment = 'P/NP grade'
        elif grading_basis in ['ESU', 'SUS']:
            comment = 'S/U grade'
        elif grading_basis == 'CNC':
            comment = 'C/NC grade'
        rows.append({
            'ID': row['sid'],
            'Name': row['name'],
            'Grade': row['grade'],
            'Grading Basis': grading_basis,
            'Comments': comment or '',
        })
    term = BerkeleyTerm.from_sis_term_id(term_id)
    return csv_download_response(
        rows=rows,
        filename=f'egrades-{grade_type}-{section_id}-#{term.season}-{term.year}-{current_user.canvas_site_id}.csv',
        fieldnames=['ID', 'Name', 'Grade', 'Grading Basis', 'Comments'],
    )


@app.route('/api/canvas_site/egrade_export/status', methods=['POST'])
def canvas_egrade_export_status():
    job_id = request.get_json().get('jobId', None)
    job = get_job(job_id)
    job_status = job.get_status(refresh=True)
    return tolerant_jsonify({
        'jobStatus': job_status,
        'percentComplete': 0.5,  # TODO: Can we deduce 'percentComplete' value?
    })


@app.route('/api/canvas_site/<canvas_site_id>/roster')
@canvas_role_required('TeacherEnrollment', 'TaEnrollment', 'Lead TA')
def get_roster(canvas_site_id):
    return tolerant_jsonify(canvas_site_roster(canvas_site_id))


@app.route('/api/canvas_site/<canvas_site_id>/export_roster')
@canvas_role_required('TeacherEnrollment', 'TaEnrollment', 'Lead TA')
def get_roster_csv(canvas_site_id):
    return csv_download_response(**canvas_site_roster_csv(canvas_site_id))


@app.route('/redirect/canvas/<canvas_site_id>/user/<uid>')
@login_required
def redirect_to_canvas_profile(canvas_site_id, uid):
    users = canvas.get_course(canvas_site_id, api_call=False).get_users(enrollment_type='student')
    user = next((user for user in users if getattr(user, 'login_id', None) == uid), None)
    if user:
        base_url = app.config['CANVAS_API_URL']
        return redirect(f'{base_url}/courses/{canvas_site_id}/users/{user.id}')
    else:
        raise ResourceNotFoundError(f'No bCourses site with ID "{canvas_site_id}" was found.')


def _get_official_sections(canvas_site_id):
    canvas_sections = canvas.get_course_sections(canvas_site_id)
    canvas_sections = [canvas_section_to_api_json(cs) for cs in canvas_sections if cs.sis_section_id]
    canvas_sections_by_id = {cs['id']: cs for cs in canvas_sections if cs['id']}
    section_ids = list(canvas_sections_by_id.keys())
    term_id = canvas_sections[0]['termId']
    sis_sections = sort_course_sections(
        data_loch.get_sections(term_id, section_ids) or [],
    )
    if len(sis_sections) != len(section_ids):
        app.logger.warn(f'Canvas site ID {canvas_site_id} has {len(section_ids)} sections, but SIS has {len(sis_sections)} sections.')

    def _section(section_id, rows):
        canvas_section = canvas_sections_by_id[section_id]
        return {
            **canvas_section,
            **section_to_api_json(rows[0], rows[1:]),
        }
    official_sections = []
    for section_id, rows in groupby(sis_sections, lambda s: s['section_id']):
        official_sections.append(_section(section_id, list(rows)))
    return official_sections, section_ids, sis_sections


def _get_teaching_terms(section_ids, sections):
    berkeley_terms = BerkeleyTerm.get_current_terms()
    canvas_terms = [term.sis_term_id for term in canvas.get_terms() if term.sis_term_id]
    terms = []
    for key, term in berkeley_terms.items():
        if term.to_canvas_sis_term_id() not in canvas_terms:
            continue
        if key != 'future' or term.season == 'D':
            terms.append(term)

    teaching_sections = []
    if (current_user.is_teaching or current_user.canvas_masquerading_user_id):
        instructor_uid = current_user.uid
        teaching_sections = sort_course_sections(
            data_loch.get_instructing_sections(instructor_uid, [t.to_sis_term_id() for t in terms]) or [],
        )
    if not len(teaching_sections):
        teaching_sections = sections
    courses_by_term = {}
    for section_id, sections in groupby(teaching_sections, lambda s: s['section_id']):
        sections = list(sections)
        section = next((s for s in sections if s.get('is_co_instructor', False) is False), None)
        co_instructor_sections = [s for s in sections if s.get('is_co_instructor', True) is True]
        course_id = section['course_id']
        term_id = section['term_id']
        if term_id not in courses_by_term:
            courses_by_term[term_id] = {}
        if course_id not in courses_by_term[term_id]:
            term = BerkeleyTerm.from_sis_term_id(term_id)
            courses_by_term[term_id][course_id] = course_to_api_json(term, section)
        courses_by_term[term_id][course_id]['sections'].append({
            **section_to_api_json(section, co_instructor_sections),
            'isCourseSection': section_id in section_ids,
        })

    def _term_courses(term_id, courses_by_id):
        term = BerkeleyTerm.from_sis_term_id(term_id)
        return {
            'classes': list(courses_by_id.values()),
            'name': term.to_english(),
            'slug': term.to_slug(),
            'termId': term_id,
            'termYear': term.year,
        }
    return [_term_courses(term_id, courses_by_id) for term_id, courses_by_id in courses_by_term.items()]
