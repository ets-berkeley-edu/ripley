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

from ripley.merged.grade_distributions import get_grade_distribution_with_prior_enrollments, get_grade_distributions
from tests.util import override_config


class TestGradeDistributions:

    def test_get_grade_distributions(self, app):
        with override_config(app, 'NEWT_SMALL_CELL_THRESHOLD', 0), override_config(app, 'NEWT_MINIMUM_CLASS_SIZE', 0):
            demographics_distribution, grade_distribution = get_grade_distributions('2228', ['99999'])
            assert demographics_distribution == [
                {
                    'averageGradePoints': 2.2333333333333334,
                    'count': 3,
                    'courseName': 'ASTRON 218',
                    'genders': {
                        'female': {
                            'averageGradePoints': 2.2333333333333334,
                            'count': 3,
                        },
                    },
                    'internationalStatus': {
                        'false': {
                            'averageGradePoints': 2.2333333333333334,
                            'count': 3,
                        },
                        'true': {
                            'averageGradePoints': 0,
                            'count': 0,
                        },
                    },
                    'termId': '2225',
                    'termName': 'Summer 2022',
                    'transferStatus': {
                        'false': {
                            'averageGradePoints': 2.2333333333333334,
                            'count': 3,
                        },
                        'true': {
                            'averageGradePoints': 0,
                            'count': 0,
                        },
                    },
                    'underrepresentedMinorityStatus': {
                        'false': {
                            'averageGradePoints': 0,
                            'count': 0,
                        },
                        'true': {
                            'averageGradePoints': 2.2333333333333334,
                            'count': 3,
                        },
                    },
                },
                {
                    'averageGradePoints': 3.8602409638554214,
                    'count': 83,
                    'courseName': 'ASTRON 218',
                    'genders': {
                        'female': {
                            'averageGradePoints': 3.9317460317460315,
                            'count': 63,
                        },
                        'male': {
                            'averageGradePoints': 3.615789473684211,
                            'count': 19,
                        },
                        'other': {
                            'averageGradePoints': 4.0,
                            'count': 1,
                        },
                    },
                    'internationalStatus': {
                        'false': {
                            'averageGradePoints': 3.9119402985074623,
                            'count': 67,
                        },
                        'true': {
                            'averageGradePoints': 3.64375,
                            'count': 16,
                        },
                    },
                    'termId': '2228',
                    'termName': 'Fall 2022',
                    'transferStatus': {
                        'false': {
                            'averageGradePoints': 3.8746835443037972,
                            'count': 79,
                        },
                        'true': {
                            'averageGradePoints': 3.575,
                            'count': 4,
                        },
                    },
                    'underrepresentedMinorityStatus': {
                        'false': {
                            'averageGradePoints': 3.8233333333333333,
                            'count': 30,
                        },
                        'true': {
                            'averageGradePoints': 3.881132075471698,
                            'count': 53,
                        },
                    },
                },
            ]
            assert grade_distribution == {
                '2225': [
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'A-',
                        'percentage': 16.7,
                    },
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'C',
                        'percentage': 16.7,
                    },
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'D',
                        'percentage': 16.7,
                    },
                    {
                        'count': 3,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'P',
                        'percentage': 50.0,
                    },
                ],
                '2228': [
                    {
                        'classSize': 91,
                        'count': 16,
                        'courseName': 'ASTRON 218',
                        'grade': 'A+',
                        'percentage': 17.6,
                    },
                    {
                        'classSize': 91,
                        'count': 52,
                        'courseName': 'ASTRON 218',
                        'grade': 'A',
                        'percentage': 57.1,
                    },
                    {
                        'classSize': 91,
                        'count': 8,
                        'courseName': 'ASTRON 218',
                        'grade': 'A-',
                        'percentage': 8.8,
                    },
                    {
                        'classSize': 91,
                        'count': 5,
                        'courseName': 'ASTRON 218',
                        'grade': 'B+',
                        'percentage': 5.5,
                    },
                    {
                        'classSize': 91,
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'grade': 'C+',
                        'percentage': 1.1,
                    },
                    {
                        'classSize': 91,
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'grade': 'F',
                        'percentage': 1.1,
                    },
                    {
                        'classSize': 91,
                        'count': 8,
                        'courseName': 'ASTRON 218',
                        'grade': 'P',
                        'percentage': 8.8,
                    },
                ],
            }

    def test_get_grade_distributions_small_cell_suppression(self, app):
        with override_config(app, 'NEWT_SMALL_CELL_THRESHOLD', 5), override_config(app, 'NEWT_MINIMUM_CLASS_SIZE', 0):
            demographics_distribution, grade_distribution = get_grade_distributions('2228', ['99999'])
            assert demographics_distribution == [
                {
                    'averageGradePoints': 2.2333333333333334,
                    'genders': {
                        'female': {
                            'averageGradePoints': 2.2333333333333334,
                            'count': None,
                        },
                    },
                    'internationalStatus': {
                        'true': {
                            'averageGradePoints': 0,
                            'count': 0,
                        },
                        'false': {
                            'averageGradePoints': 2.2333333333333334,
                            'count': None,
                        },
                    },
                    'transferStatus': {
                        'true': {
                            'averageGradePoints': 0,
                            'count': 0,
                        },
                        'false': {
                            'averageGradePoints': 2.2333333333333334,
                            'count': None,
                        },
                    },
                    'underrepresentedMinorityStatus': {
                        'true': {
                            'averageGradePoints': 2.2333333333333334,
                            'count': None,
                        },
                        'false': {
                            'averageGradePoints': 0,
                            'count': 0,
                        },
                    },
                    'count': 3,
                    'courseName': 'ASTRON 218',
                    'termId': '2225',
                    'termName': 'Summer 2022',
                },
                {
                    'averageGradePoints': 3.8602409638554214,
                    'count': 83,
                    'courseName': 'ASTRON 218',
                    'genders': {
                        'female': {
                            'averageGradePoints': 3.9317460317460315,
                            'count': 63,
                        },
                        'male': {
                            'averageGradePoints': 3.615789473684211,
                            'count': 19,
                        },
                        'other': {
                            'averageGradePoints': 4.0,
                            'count': None,
                        },
                    },
                    'internationalStatus': {
                        'false': {
                            'averageGradePoints': 3.9119402985074623,
                            'count': 67,
                        },
                        'true': {
                            'averageGradePoints': 3.64375,
                            'count': 16,
                        },
                    },
                    'termId': '2228',
                    'termName': 'Fall 2022',
                    'transferStatus': {
                        'false': {
                            'averageGradePoints': 3.8746835443037972,
                            'count': 79,
                        },
                        'true': {
                            'averageGradePoints': 3.575,
                            'count': None,
                        },
                    },
                    'underrepresentedMinorityStatus': {
                        'false': {
                            'averageGradePoints': 3.8233333333333333,
                            'count': 30,
                        },
                        'true': {
                            'averageGradePoints': 3.881132075471698,
                            'count': 53,
                        },
                    },
                },
            ]
            assert grade_distribution == {
                '2225': [
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'A-',
                        'percentage': 16.7,
                    },
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'C',
                        'percentage': 16.7,
                    },
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'D',
                        'percentage': 16.7,
                    },
                    {
                        'count': 3,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'P',
                        'percentage': 50.0,
                    },
                ],
                '2228': [
                    {
                        'classSize': 91,
                        'count': 16,
                        'courseName': 'ASTRON 218',
                        'grade': 'A+',
                        'percentage': 17.6,
                    },
                    {
                        'classSize': 91,
                        'count': 52,
                        'courseName': 'ASTRON 218',
                        'grade': 'A',
                        'percentage': 57.1,
                    },
                    {
                        'classSize': 91,
                        'count': 8,
                        'courseName': 'ASTRON 218',
                        'grade': 'A-',
                        'percentage': 8.8,
                    },
                    {
                        'classSize': 91,
                        'count': 5,
                        'courseName': 'ASTRON 218',
                        'grade': 'B+',
                        'percentage': 5.5,
                    },
                    {
                        'classSize': 91,
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'grade': 'C+',
                        'percentage': 1.1,
                    },
                    {
                        'classSize': 91,
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'grade': 'F',
                        'percentage': 1.1,
                    },
                    {
                        'classSize': 91,
                        'count': 8,
                        'courseName': 'ASTRON 218',
                        'grade': 'P',
                        'percentage': 8.8,
                    },
                ],
            }

    def test_get_grade_distributions_min_class_size(self, app):
        with override_config(app, 'NEWT_SMALL_CELL_THRESHOLD', 0), override_config(app, 'NEWT_MINIMUM_CLASS_SIZE', 50):
            demographics_distribution, grade_distribution = get_grade_distributions('2228', ['99999'])
            assert demographics_distribution == [
                {
                    'averageGradePoints': 3.8602409638554214,
                    'count': 83,
                    'courseName': 'ASTRON 218',
                    'genders': {
                        'female': {
                            'averageGradePoints': 3.9317460317460315,
                            'count': 63,
                        },
                        'male': {
                            'averageGradePoints': 3.615789473684211,
                            'count': 19,
                        },
                        'other': {
                            'averageGradePoints': 4.0,
                            'count': 1,
                        },
                    },
                    'internationalStatus': {
                        'false': {
                            'averageGradePoints': 3.9119402985074623,
                            'count': 67,
                        },
                        'true': {
                            'averageGradePoints': 3.64375,
                            'count': 16,
                        },
                    },
                    'termId': '2228',
                    'termName': 'Fall 2022',
                    'transferStatus': {
                        'false': {
                            'averageGradePoints': 3.8746835443037972,
                            'count': 79,
                        },
                        'true': {
                            'averageGradePoints': 3.575,
                            'count': 4,
                        },
                    },
                    'underrepresentedMinorityStatus': {
                        'false': {
                            'averageGradePoints': 3.8233333333333333,
                            'count': 30,
                        },
                        'true': {
                            'averageGradePoints': 3.881132075471698,
                            'count': 53,
                        },
                    },
                },
            ]
            assert grade_distribution == {
                '2228': [
                    {
                        'classSize': 91,
                        'count': 16,
                        'courseName': 'ASTRON 218',
                        'grade': 'A+',
                        'percentage': 17.6,
                    },
                    {
                        'classSize': 91,
                        'count': 52,
                        'courseName': 'ASTRON 218',
                        'grade': 'A',
                        'percentage': 57.1,
                    },
                    {
                        'classSize': 91,
                        'count': 8,
                        'courseName': 'ASTRON 218',
                        'grade': 'A-',
                        'percentage': 8.8,
                    },
                    {
                        'classSize': 91,
                        'count': 5,
                        'courseName': 'ASTRON 218',
                        'grade': 'B+',
                        'percentage': 5.5,
                    },
                    {
                        'classSize': 91,
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'grade': 'C+',
                        'percentage': 1.1,
                    },
                    {
                        'classSize': 91,
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'grade': 'F',
                        'percentage': 1.1,
                    },
                    {
                        'classSize': 91,
                        'count': 8,
                        'courseName': 'ASTRON 218',
                        'grade': 'P',
                        'percentage': 8.8,
                    },
                ],
            }

    def test_enrollment_distribution(self, app):
        d = get_grade_distribution_with_prior_enrollments(
            term_id='2232',
            course_name='ANTHRO 189',
            prior_course_name='ASTRON 218',
        )
        assert d == {
            '2232': [
                {
                    'classSize': 7,
                    'courseName': 'ASTRON 218',
                    'grade': 'A+',
                    'noPriorEnrollCount': 0,
                    'noPriorEnrollPercentage': 0.0,
                    'priorEnrollCount': 1,
                    'priorEnrollPercentage': 16.7,
                    'termName': 'Spring 2023',
                    'totalCount': 1,
                    'totalPercentage': 14.3,
                },
                {
                    'classSize': 7,
                    'courseName': 'ASTRON 218',
                    'grade': 'A',
                    'noPriorEnrollCount': 1,
                    'noPriorEnrollPercentage': 100.0,
                    'priorEnrollCount': 1,
                    'priorEnrollPercentage': 16.7,
                    'termName': 'Spring 2023',
                    'totalCount': 2,
                    'totalPercentage': 28.6,
                },
                {
                    'classSize': 7,
                    'courseName': 'ASTRON 218',
                    'grade': 'A-',
                    'noPriorEnrollCount': 0,
                    'noPriorEnrollPercentage': 0.0,
                    'priorEnrollCount': 1,
                    'priorEnrollPercentage': 16.7,
                    'termName': 'Spring 2023',
                    'totalCount': 1,
                    'totalPercentage': 14.3,
                },
                {
                    'classSize': 7,
                    'courseName': 'ASTRON 218',
                    'grade': 'B+',
                    'noPriorEnrollCount': 0,
                    'noPriorEnrollPercentage': 0,
                    'priorEnrollCount': 2,
                    'priorEnrollPercentage': 33.3,
                    'termName': 'Spring 2023',
                    'totalCount': 2,
                    'totalPercentage': 28.6,
                },
                {
                    'classSize': 7,
                    'courseName': 'ASTRON 218',
                    'grade': 'B',
                    'noPriorEnrollCount': 0,
                    'noPriorEnrollPercentage': 0.0,
                    'priorEnrollCount': 1,
                    'priorEnrollPercentage': 16.7,
                    'termName': 'Spring 2023',
                    'totalCount': 1,
                    'totalPercentage': 14.3,
                },
            ],
        }
