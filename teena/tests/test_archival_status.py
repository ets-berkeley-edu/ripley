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

import pytest
from teena.config.teena_test_config import TeenaTestConfig
from teena.test_utils import ripley_utils, utils

test = TeenaTestConfig()
test.archival_status()


def _load_archival_status_view(test_instance, user):
    test_instance.canvas_page.masquerade_as(user)
    test_instance.site_creation_page.load_embedded_tool(user)
    test_instance.site_creation_page.click_view_retention_status()
    test_instance.archival_status_page.wait_for_page_to_load()


@pytest.mark.usefixtures('page_objects')
class TestSetup:

    def test_setup(self):
        self.canvas_page.log_in(self.cal_net_page, test.admin.username, utils.get_admin_password())
        self.canvas_page.configure_single_site(test)
        self.create_course_site_page.provision_course_site(test.course_site)
        self.canvas_page.publish_course_site(test.course_site)
        self.canvas_page.load_users_page(test.course_site)
        self.canvas_page.click_find_person_to_add()
        for user in [test.manual_teacher, test.lead_ta, test.ta]:
            self.add_user_page.search(user.uid, 'CalNet UID')
            self.add_user_page.add_user_by_uid(user, test.course_site.sections[0])
        self.canvas_page.set_canvas_ids([test.manual_teacher, test.lead_ta, test.ta])
        site_ids_to_clear = set()
        for user in [test.manual_teacher, test.lead_ta, test.ta]:
            self.canvas_page.masquerade_as(user)
            self.site_creation_page.load_embedded_tool(user)
            for item in self.archival_status_page.get_archival_status_api_feed():
                site_ids_to_clear.add(item['canvasSiteId'])
        ripley_utils.clear_archival_statuses_for_site_ids(site_ids_to_clear)


@pytest.mark.usefixtures('page_objects')
class TestNoCourses:

    def test_no_courses_message(self):
        # No archival_status record exists for the course site yet, so the feed is empty.
        _load_archival_status_view(self, test.manual_teacher)
        assert self.archival_status_page.has_no_courses_message()


@pytest.mark.usefixtures('page_objects')
class TestSetArchivalStatus:

    def test_set_archival_status(self):
        ripley_utils.set_canvas_site_archival_status(test.course_site.site_id, '2028', False)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(
    argnames=('user', 'expected_role'),
    argvalues=[
        (test.manual_teacher, 'Teacher'),
        (test.lead_ta, 'Lead TA'),
        (test.ta, 'TA'),
    ],
    ids=['Teacher', 'Lead TA', 'TA'],
    scope='class',
)
class TestUserRoles:

    def test_site_in_table(self, user, expected_role):
        _load_archival_status_view(self, user)
        assert test.course_site.site_id in self.archival_status_page.visible_site_ids()

    def test_role_displayed(self, user, expected_role):
        utils.assert_equivalence(
            self.archival_status_page.role_for_site(test.course_site.site_id),
            expected_role,
        )

    def test_removal_date(self, user, expected_role):
        utils.assert_equivalence(
            self.archival_status_page.removal_date_for_site(test.course_site.site_id),
            'June 2028',
        )


@pytest.mark.usefixtures('page_objects')
class TestOptedOut:

    def test_opt_out_via_switch(self):
        # _load_archival_status_view masquerades as the user, so the admin-only opt-out toggle is available.
        _load_archival_status_view(self, test.manual_teacher)
        assert self.archival_status_page.opt_out_switch_present(test.course_site.site_id) is True
        assert self.archival_status_page.is_opted_out(test.course_site.site_id) is False
        self.archival_status_page.click_opt_out_switch(test.course_site.site_id)
        assert self.archival_status_page.is_opted_out(test.course_site.site_id) is True

    def test_removal_date_exempt(self):
        utils.assert_equivalence(
            self.archival_status_page.removal_date_for_site(test.course_site.site_id),
            'Exempt',
        )

    def test_opt_back_in_via_switch(self):
        self.archival_status_page.click_opt_out_switch(test.course_site.site_id)
        assert self.archival_status_page.is_opted_out(test.course_site.site_id) is False

    def test_removal_date_restored(self):
        utils.assert_equivalence(
            self.archival_status_page.removal_date_for_site(test.course_site.site_id),
            'June 2028',
        )


@pytest.mark.usefixtures('page_objects')
class TestCleanup:

    def test_cleanup(self):
        ripley_utils.set_canvas_site_archival_status(test.course_site.site_id, None, False)
