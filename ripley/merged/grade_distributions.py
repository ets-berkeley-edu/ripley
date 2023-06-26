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

from copy import deepcopy
from itertools import groupby

from flask import current_app as app
from ripley.externals.data_loch import get_grades_with_demographics, get_grades_with_enrollments
from ripley.lib.util import to_percentage


COLLAPSE_ETHNICITIES = {
    'Chinese / Chinese-American': 'Asian / Asian American',
    'East Indian / Pakistani': 'Asian / Asian American',
    'Filipino / Filipino-American': 'Asian / Asian American',
    'Japanese / Japanese American': 'Asian / Asian American',
    'Korean / Korean-American': 'Asian / Asian American',
    'Mexican / Mexican-American / Chicano': 'Hispanic / Latinx',
    'Other Asian': 'Asian / Asian American',
    'Other Spanish-American / Latino': 'Hispanic / Latinx',
    'Puerto Rican': 'Hispanic / Latinx',
    'Thai': 'Asian / Asian American',
    'Vietnamese': 'Asian / Asian American',
}


EMPTY_DISTRIBUTION = {
    'ethnicities': {},
    'genders': {},
    'termsInAttendance': {},
    'transferStatus': {
        'true': 0,
        'false': 0,
    },
    'underrepresentedMinorityStatus': {
        'true': 0,
        'false': 0,
    },
    'visaTypes': {},
    'total': 0,
}


def get_grade_distribution_with_demographics(term_id, section_ids):  # noqa
    distribution = {}
    class_size = 0
    totals = deepcopy(EMPTY_DISTRIBUTION)

    for row in get_grades_with_demographics(term_id, section_ids):
        if not row['grade']:
            continue
        if row['grade'] not in distribution:
            distribution[row['grade']] = deepcopy(EMPTY_DISTRIBUTION)
        distribution[row['grade']]['total'] += 1
        class_size += 1

        def _count_boolean_value(column, distribution_key):
            if row[column]:
                distribution[row['grade']][distribution_key]['true'] += 1
                totals[distribution_key]['true'] += 1
            else:
                distribution[row['grade']][distribution_key]['false'] += 1
                totals[distribution_key]['false'] += 1

        _count_boolean_value('transfer', 'transferStatus')
        _count_boolean_value('minority', 'underrepresentedMinorityStatus')

        def _count_string_value(value, distribution_key):
            value = str(value) if value else 'none'
            if value not in distribution[row['grade']][distribution_key]:
                distribution[row['grade']][distribution_key][value] = 0
            if value not in totals[distribution_key]:
                totals[distribution_key][value] = 0
                totals[distribution_key][value] = 0
            distribution[row['grade']][distribution_key][value] += 1
            totals[distribution_key][value] += 1

        _count_string_value(row['gender'], 'genders')
        _count_string_value(row['terms_in_attendance'], 'termsInAttendance')
        _count_string_value(row['visa_type'], 'visaTypes')

        collapsed_ethnicities = set(COLLAPSE_ETHNICITIES.get(e) or e for e in row['ethnicities'])
        for ethnicity in collapsed_ethnicities:
            _count_string_value(ethnicity, 'ethnicities')

    sorted_distribution = []
    for grade in sorted(distribution.keys(), key=_grade_ordering_index):
        for distribution_key, values in distribution[grade].items():
            if distribution_key == 'total':
                continue
            for distribution_value, count in values.items():
                distribution[grade][distribution_key][distribution_value] = {
                    'count': count,
                    'percentage': to_percentage(count, totals[distribution_key][distribution_value]),
                }
        distribution[grade].update({'grade': grade})
        distribution[grade].update({'percentage': to_percentage(distribution[grade]['total'], class_size)})
        sorted_distribution.append(distribution[grade])

    return sorted_distribution


def get_grade_distribution_with_enrollments(term_id, section_ids):
    grades_by_course_name = {}
    for course_name, rows in groupby(get_grades_with_enrollments(term_id, section_ids), key=lambda x: x['sis_course_name']):
        grades_by_course_name[course_name] = [r for r in rows if r['grade']]

    courses_by_popularity = sorted(grades_by_course_name.items(), key=lambda r: len(r[1]), reverse=True)
    courses_by_popularity = courses_by_popularity[0:app.config['GRADE_DISTRIBUTION_MAX_DISTINCT_COURSES']]

    distribution = {}
    for course_name, course_rows in courses_by_popularity:
        distribution[course_name] = {'total': 0}
        for r in course_rows:
            if r['grade'] not in distribution[course_name]:
                distribution[course_name][r['grade']] = 1
            else:
                distribution[course_name][r['grade']] += 1
            distribution[course_name]['total'] += 1

    for course_name, course_distribution in distribution.items():
        sorted_distribution = []
        for grade in sorted(course_distribution.keys(), key=_grade_ordering_index):
            if grade == 'total':
                continue
            sorted_distribution.append({
                'grade': grade,
                'count': course_distribution[grade],
                'percentage': round(course_distribution[grade] * 100 / float(course_distribution['total']), 1),
            })
        distribution[course_name] = sorted_distribution

    return distribution


GRADE_ORDERING = ('A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D', 'D-', 'F', 'P', 'NP', 'I')


def _grade_ordering_index(grade):
    try:
        return GRADE_ORDERING.index(grade)
    except ValueError:
        return len(GRADE_ORDERING)