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

from flask import current_app as app
from ripley.api.errors import ResourceNotFoundError
from ripley.api.util import canvas_role_required
from ripley.externals import canvas
from ripley.lib.canvas_utils import canvas_site_to_api_json
from ripley.lib.http import tolerant_jsonify
from ripley.merged.roster import canvas_course_roster


@app.route('/api/canvas_site/provision')
def canvas_course_provision():
    return tolerant_jsonify([])


@app.route('/api/canvas_site/<canvas_site_id>')
def get_canvas_course_site(canvas_site_id):
    course = canvas.get_course(canvas_site_id)
    if course:
        return tolerant_jsonify(canvas_site_to_api_json(course))
    else:
        raise ResourceNotFoundError(f'No Canvas course site found with ID {canvas_site_id}')


@app.route('/api/canvas_site/<canvas_site_id>/provision/sections_feed')
def canvas_course_provision_sections_feed(canvas_site_id):
    return tolerant_jsonify([])


@app.route('/api/canvas_site/provision/status')
def canvas_course_provision_status():
    # TODO: ?jobId=${jobId}
    return tolerant_jsonify([])


@app.route('/api/canvas_site/<canvas_site_id>/egrade_export/options')
def canvas_egrade_export(canvas_site_id):
    return tolerant_jsonify([])


@app.route('/api/canvas_site/<canvas_site_id>/egrade_export/status')
def canvas_egrade_export_status(canvas_site_id):
    # TODO: ?jobId=${jobId}
    return tolerant_jsonify([])


@app.route('/api/canvas_site/<canvas_course_id>/roster')
@canvas_role_required('TeacherEnrollment', 'TaEnrollment', 'Lead TA', 'Reader')
def get_roster(canvas_course_id):
    course = canvas.get_course(canvas_course_id)
    if course:
        roster = canvas_course_roster(canvas_course_id)
        return tolerant_jsonify(roster if roster else None)
    else:
        raise ResourceNotFoundError(f'No bCourses site with ID "{canvas_course_id}" was found.')