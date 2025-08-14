"""
Copyright ©2025. The Regents of the University of California (Regents). All Rights Reserved.

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
            assert len(demographics_distribution) == 2
            assert demographics_distribution[0] == {
                'athleteStatus': {
                    'false': {
                        'meanGradePoints': 2.233,
                        'count': 3,
                        'medianGradePoints': 2,
                        'errorGradePoints': 0.788,
                    },
                    'true': {
                        'meanGradePoints': 0,
                        'count': 0,
                        'medianGradePoints': 0,
                        'errorGradePoints': 0,
                    },
                },
                'meanGradePoints': 2.233,
                'count': 3,
                'courseName': 'ASTRON 218',
                'errorGradePoints': 0.788,
                'genders': {
                    'female': {
                        'meanGradePoints': 2.233,
                        'count': 3,
                        'medianGradePoints': 2,
                        'errorGradePoints': 0.788,
                    },
                },
                'internationalStatus': {
                    'false': {
                        'meanGradePoints': 2.233,
                        'count': 3,
                        'errorGradePoints': 0.788,
                        'medianGradePoints': 2,
                    },
                    'true': {
                        'meanGradePoints': 0,
                        'count': 0,
                        'medianGradePoints': 0,
                        'errorGradePoints': 0,
                    },
                },
               'majors': {
                    'Bioresource Sciences BS': {
                       'count': 1,
                       'errorGradePoints': 0,
                       'meanGradePoints': 2,
                       'medianGradePoints': 2,
                    },
                },
                'medianGradePoints': 2,
                'termId': '2225',
                'termName': 'Summer 2022',
                'transferStatus': {
                    'false': {
                        'meanGradePoints': 2.233,
                        'count': 3,
                        'medianGradePoints': 2,
                        'errorGradePoints': 0.788,
                    },
                    'true': {
                        'meanGradePoints': 0,
                        'count': 0,
                        'medianGradePoints': 0,
                        'errorGradePoints': 0,
                    },
                },
                'underrepresentedMinorityStatus': {
                    'false': {
                        'meanGradePoints': 0,
                        'count': 0,
                        'medianGradePoints': 0,
                        'errorGradePoints': 0,
                    },
                    'true': {
                        'meanGradePoints': 2.233,
                        'errorGradePoints': 0.788,
                        'count': 3,
                        'medianGradePoints': 2,
                    },
                },
            }
            assert demographics_distribution[1] == {
                'athleteStatus': {
                    'false': {
                        'meanGradePoints': 3.86,
                        'count': 81,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.056,
                    },
                    'true': {
                        'meanGradePoints': 3.85,
                        'count': 2,
                        'medianGradePoints': 3.85,
                        'errorGradePoints': 0.15,
                    },
                },
                'meanGradePoints': 3.86,
                'count': 83,
                'courseName': 'ASTRON 218',
                'errorGradePoints': 0.055,
                'genders': {
                    'female': {
                        'meanGradePoints': 3.932,
                        'count': 63,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.023,
                    },
                    'male': {
                        'meanGradePoints': 3.616,
                        'count': 19,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.222,
                    },
                    'other': {
                        'meanGradePoints': 4.0,
                        'count': 1,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0,
                    },
                },
                'internationalStatus': {
                    'false': {
                        'meanGradePoints': 3.912,
                        'count': 67,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.032,
                    },
                    'true': {
                        'meanGradePoints': 3.644,
                        'count': 16,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.25,
                    },
                },
               'majors': {
                   'Bioresource Sciences BS': {
                       'count': 1,
                       'errorGradePoints': 0,
                       'meanGradePoints': 3.7,
                       'medianGradePoints': 3.7,
                   },
                   'English BA': {
                       'count': 2,
                       'errorGradePoints': 0.0,
                       'meanGradePoints': 4,
                       'medianGradePoints': 4.0,
                   },
                   'Forestry BS': {
                       'count': 3,
                       'errorGradePoints': 0.0,
                       'meanGradePoints': 4,
                       'medianGradePoints': 4,
                    },
                },
                'medianGradePoints': 4,
                'termId': '2228',
                'termName': 'Fall 2022',
                'transferStatus': {
                    'false': {
                        'meanGradePoints': 3.875,
                        'count': 79,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.054,
                    },
                    'true': {
                        'meanGradePoints': 3.575,
                        'count': 4,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.425,
                    },
                },
                'underrepresentedMinorityStatus': {
                    'false': {
                        'meanGradePoints': 3.823,
                        'count': 30,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.134,
                    },
                    'true': {
                        'meanGradePoints': 3.881,
                        'count': 53,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.041,
                    },
                },
            }
            assert grade_distribution == {
                '2225': [
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'A+',
                        'percentage': 0,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'A',
                        'percentage': 0,
                    },
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'A-',
                        'percentage': 16.7,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'B+',
                        'percentage': 0,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'B',
                        'percentage': 0,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'B-',
                        'percentage': 0,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'C+',
                        'percentage': 0,
                    },
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'C',
                        'percentage': 16.7,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'C-',
                        'percentage': 0,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'D+',
                        'percentage': 0,
                    },
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'D',
                        'percentage': 16.7,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'D-',
                        'percentage': 0,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'F',
                        'percentage': 0,
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
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'B',
                        'percentage': 0,
                    },
                    {
                        'classSize': 91,
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'B-',
                        'percentage': 0,
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
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'C',
                        'percentage': 0,
                    },
                    {
                        'classSize': 91,
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'C-',
                        'percentage': 0,
                    },
                    {
                        'classSize': 91,
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'D+',
                        'percentage': 0,
                    },
                    {
                        'classSize': 91,
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'D',
                        'percentage': 0,
                    },
                    {
                        'classSize': 91,
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'D-',
                        'percentage': 0,
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
            assert len(demographics_distribution) == 2
            assert demographics_distribution[0] == {
                'athleteStatus': {
                    'true': None,
                    'false': None,
                },
                'meanGradePoints': 2.233,
                'genders': {
                    'female': None,
                },
                'internationalStatus': {
                    'true': None,
                    'false': None,
                },
                'majors': {
                   'Bioresource Sciences BS': None,
                },
                'transferStatus': {
                    'true': None,
                    'false': None,
                },
                'underrepresentedMinorityStatus': {
                    'true': None,
                    'false': None,
                },
                'count': 3,
                'courseName': 'ASTRON 218',
                'errorGradePoints': 0.788,
                'medianGradePoints': 2,
                'termId': '2225',
                'termName': 'Summer 2022',
            }
            assert demographics_distribution[1] == {
                'athleteStatus': {
                    'true': None,
                    'false': {
                        'meanGradePoints': 3.86,
                        'count': 81,
                        'medianGradePoints': 4,
                        'errorGradePoints': 0.056,
                    },
                },
                'meanGradePoints': 3.86,
                'count': 83,
                'courseName': 'ASTRON 218',
                'errorGradePoints': 0.055,
                'genders': {
                    'female': {
                        'meanGradePoints': 3.932,
                        'count': 63,
                        'medianGradePoints': 4,
                        'errorGradePoints': 0.023,
                    },
                    'male': {
                        'meanGradePoints': 3.616,
                        'count': 19,
                        'medianGradePoints': 4,
                        'errorGradePoints': 0.222,
                    },
                    'other': None,
                },
                'internationalStatus': {
                    'false': {
                        'meanGradePoints': 3.912,
                        'count': 67,
                        'medianGradePoints': 4,
                        'errorGradePoints': 0.032,
                    },
                    'true': {
                        'meanGradePoints': 3.644,
                        'count': 16,
                        'medianGradePoints': 4,
                        'errorGradePoints': 0.25,
                    },
                },
               'majors': {
                   'Bioresource Sciences BS': None,
                   'English BA': None,
                   'Forestry BS': None,
                },
                'medianGradePoints': 4,
                'termId': '2228',
                'termName': 'Fall 2022',
                'transferStatus': {
                    'false': {
                        'meanGradePoints': 3.875,
                        'count': 79,
                        'medianGradePoints': 4,
                        'errorGradePoints': 0.054,
                    },
                    'true': None,
                },
                'underrepresentedMinorityStatus': {
                    'false': {
                        'meanGradePoints': 3.823,
                        'count': 30,
                        'medianGradePoints': 4,
                        'errorGradePoints': 0.134,
                    },
                    'true': {
                        'meanGradePoints': 3.881,
                        'count': 53,
                        'medianGradePoints': 4,
                        'errorGradePoints': 0.041,
                    },
                },
            }
            assert grade_distribution == {
                '2225': [
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'A+',
                        'percentage': 0,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'A',
                        'percentage': 0,
                    },
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'A-',
                        'percentage': 16.7,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'B+',
                        'percentage': 0,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'B',
                        'percentage': 0,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'B-',
                        'percentage': 0,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'C+',
                        'percentage': 0,
                    },
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'C',
                        'percentage': 16.7,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'C-',
                        'percentage': 0,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'D+',
                        'percentage': 0,
                    },
                    {
                        'count': 1,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'D',
                        'percentage': 16.7,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'D-',
                        'percentage': 0,
                    },
                    {
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'classSize': 6,
                        'grade': 'F',
                        'percentage': 0,
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
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'B',
                        'percentage': 0,
                    },
                    {
                        'classSize': 91,
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'B-',
                        'percentage': 0,
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
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'C',
                        'percentage': 0,
                    },
                    {
                        'classSize': 91,
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'C-',
                        'percentage': 0,
                    },
                    {
                        'classSize': 91,
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'D+',
                        'percentage': 0,
                    },
                    {
                        'classSize': 91,
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'D',
                        'percentage': 0,
                    },
                    {
                        'classSize': 91,
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'D-',
                        'percentage': 0,
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
            assert len(demographics_distribution) == 1
            assert demographics_distribution[0] == {
                'athleteStatus': {
                    'false': {
                        'meanGradePoints': 3.86,
                        'count': 81,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.056,
                    },
                    'true': {
                        'meanGradePoints': 3.85,
                        'count': 2,
                        'medianGradePoints': 3.85,
                        'errorGradePoints': 0.15,
                    },
                },
                'meanGradePoints': 3.86,
                'count': 83,
                'courseName': 'ASTRON 218',
                'errorGradePoints': 0.055,
                'genders': {
                    'female': {
                        'meanGradePoints': 3.932,
                        'count': 63,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.023,
                    },
                    'male': {
                        'meanGradePoints': 3.616,
                        'count': 19,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.222,
                    },
                    'other': {
                        'meanGradePoints': 4.0,
                        'count': 1,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0,
                    },
                },
                'internationalStatus': {
                    'false': {
                        'meanGradePoints': 3.912,
                        'count': 67,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.032,
                    },
                    'true': {
                        'meanGradePoints': 3.644,
                        'count': 16,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.25,
                    },
                },
               'majors': {
                   'English BA': {
                       'count': 2,
                       'errorGradePoints': 0.0,
                       'meanGradePoints': 4,
                       'medianGradePoints': 4.0,
                   },
                   'Forestry BS': {
                       'count': 3,
                       'errorGradePoints': 0.0,
                       'meanGradePoints': 4,
                       'medianGradePoints': 4,
                   },
                   'Geography BA': {
                       'count': 1,
                       'errorGradePoints': 0,
                       'meanGradePoints': 4,
                       'medianGradePoints': 4,
                    },
                },
                'medianGradePoints': 4,
                'termId': '2228',
                'termName': 'Fall 2022',
                'transferStatus': {
                    'false': {
                        'meanGradePoints': 3.875,
                        'count': 79,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.054,
                    },
                    'true': {
                        'meanGradePoints': 3.575,
                        'count': 4,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.425,
                    },
                },
                'underrepresentedMinorityStatus': {
                    'false': {
                        'meanGradePoints': 3.823,
                        'count': 30,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.134,
                    },
                    'true': {
                        'meanGradePoints': 3.881,
                        'count': 53,
                        'medianGradePoints': 4.0,
                        'errorGradePoints': 0.041,
                    },
                },
            }
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
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'B',
                        'percentage': 0,
                    },
                    {
                        'classSize': 91,
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'B-',
                        'percentage': 0,
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
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'C',
                        'percentage': 0,
                    },
                    {
                        'classSize': 91,
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'C-',
                        'percentage': 0,
                    },
                    {
                        'classSize': 91,
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'D+',
                        'percentage': 0,
                    },
                    {
                        'classSize': 91,
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'D',
                        'percentage': 0,
                    },
                    {
                        'classSize': 91,
                        'count': 0,
                        'courseName': 'ASTRON 218',
                        'grade': 'D-',
                        'percentage': 0,
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
