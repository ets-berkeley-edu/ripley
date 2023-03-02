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

import pytest
import requests_mock
from ripley.models.mailing_list import MailingList
from tests.util import register_canvas_uris


class TestMailingList:

    def test_initialize(self, app):
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id']}, m)
            mailing_list = MailingList.find_or_initialize('1234567')
            feed = mailing_list.to_api_json()

            assert feed['canvasSite']['canvasCourseId'] == '1234567'
            assert feed['canvasSite']['sisCourseId'] == 'CRS:ASTRON-218-2023-B'
            assert feed['canvasSite']['name'] == 'ASTRON 218: Stellar Dynamics and Galactic Structure'
            assert feed['canvasSite']['courseCode'] == 'ASTRON 218'
            assert feed['canvasSite']['url'] == 'https://hard_knocks_api.instructure.com/courses/1234567'
            assert feed['canvasSite']['term'] == {'term_yr': '2023', 'term_cd': 'B', 'name': 'Spring 2023'}

            assert feed['mailingList']['name'] == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'
            assert feed['mailingList']['welcomeEmailActive'] is False
            assert feed['mailingList']['welcomeEmailBody'] is None
            assert feed['mailingList']['welcomeEmailSubject'] is None
            assert feed['mailingList']['state'] == 'unregistered'

    def test_create(self, app):
        with requests_mock.Mocker() as m:
            register_canvas_uris(app, {'course': ['get_by_id']}, m)

            mailing_list = MailingList.create('1234567')
            feed = mailing_list.to_api_json()

            assert feed['canvasSite']['name'] == 'ASTRON 218: Stellar Dynamics and Galactic Structure'
            assert feed['mailingList']['name'] == 'astron-218-stellar-dynamics-and-galactic-stru-sp23'
            assert feed['mailingList']['state'] == 'created'

            with pytest.raises(ValueError, match='List with id 1234567 already exists'):
                mailing_list = MailingList.create('1234567')