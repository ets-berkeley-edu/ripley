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
import time

import pytest
from teena.config.teena_test_config import TeenaTestConfig
from teena.test_utils import ripley_utils, utils

test = TeenaTestConfig()
test.add_user()


@pytest.mark.usefixtures('page_objects')
class TestCustomizationsAndAddUser:

    def test_setup(self):
        self.canvas_page.log_in(self.cal_net_page, test.admin.username, utils.get_admin_password())
        self.canvas_page.configure_single_site(test)
        self.create_course_site_page.provision_course_site(test.course_site)
        self.canvas_page.publish_course_site(test.course_site)
        self.canvas_page.load_homepage()


@pytest.mark.usefixtures('page_objects')
class TestFooterCustomizations:

    def test_link_about(self):
        self.canvas_page.scroll_to_bottom()
        title = 'bCourses | Research, Teaching, & Learning'
        assert self.canvas_page.is_external_link_valid(self.canvas_page.ABOUT_LINK, title)

    def test_link_privacy_policy(self):
        title = 'Product Privacy | Policy'
        assert self.canvas_page.is_external_link_valid(self.canvas_page.PRIVACY_POLICY_LINK, title)

    def test_link_terms_of_service(self):
        title = 'Acceptable Use | Policy | Instructure'
        assert self.canvas_page.is_external_link_valid(self.canvas_page.TERMS_OF_SERVICE_LINK, title)

    def test_link_data_use_and_analytics(self):
        title = 'bCourses Data Use and Analytics | Research, Teaching, & Learning'
        assert self.canvas_page.is_external_link_valid(self.canvas_page.DATA_USE_LINK, title)

    def test_link_uc_berkeley_honor_code(self):
        title = 'Berkeley Honor Code | Center for Teaching & Learning'
        assert self.canvas_page.is_external_link_valid(self.canvas_page.HONOR_CODE_LINK, title)

    def test_link_student_resources(self):
        title = 'Resources | ASUC'
        assert self.canvas_page.is_external_link_valid(self.canvas_page.STUDENT_RESOURCES_LINK, title)

    def test_link_accessibility(self):
        title = 'Accessible bCourses Sites | Research, Teaching, & Learning'
        assert self.canvas_page.is_external_link_valid(self.canvas_page.ACCESSIBILITY_LINK, title)

    def test_link_nondiscrimination(self):
        title = 'Nondiscrimination Policy Statement | Office for the Prevention of Harassment & Discrimination'
        assert self.canvas_page.is_external_link_valid(self.canvas_page.NONDISCRIMINATION_LINK, title)


@pytest.mark.usefixtures('page_objects')
class TestCourseRetentionPolicyBanner:

    def test_no_archiving_status(self):
        self.canvas_page.load_course_site(test.course_site)
        time.sleep(1)
        assert not self.canvas_page.is_present(self.canvas_page.COURSE_RETENTION_POLICY_BANNER)
        self.canvas_page.load_users_page(test.course_site)
        time.sleep(1)
        assert not self.canvas_page.is_present(self.canvas_page.COURSE_RETENTION_POLICY_BANNER)

    def test_set_archiving_status(self):
        ripley_utils.set_canvas_site_archival_status(test.course_site.site_id, '2027', False)
        self.canvas_page.load_course_site(test.course_site)
        time.sleep(1)
        assert self.canvas_page.is_present(self.canvas_page.COURSE_RETENTION_POLICY_BANNER)
        self.canvas_page.load_users_page(test.course_site)
        time.sleep(1)
        assert self.canvas_page.is_present(self.canvas_page.COURSE_RETENTION_POLICY_BANNER)
        ripley_utils.set_canvas_site_archival_status(test.course_site.site_id, None, True)


@pytest.mark.usefixtures('page_objects')
class TestProfileCustomizations:

    def test_pronouns_section_and_customization(self):
        self.canvas_page.load_user_profile()

        # Verify the pronoun feature is enabled
        assert self.canvas_page.is_pronouns_section_present(), "The 'pronouns' ID was not found on the page."

        # Verify our custom text appears
        expected_text = (
            "The pronouns that you have provided will appear after your name. "
            "Follow the instructions on How do I change my name or pronouns in bCourses? "
            "to change or remove. Changes will be reflected in bCourses in 24 hours."
        )
        actual_text = self.canvas_page.get_description_text()

        utils.assert_equivalence(actual_text, expected_text)

    def test_pronouns_help_link(self):
        partial_title = 'IT Public KB - How do I change my name or pronouns in bCourses?'
        assert self.canvas_page.is_external_link_valid(self.canvas_page.PRONOUNS_HELP_LINK, partial_title)


@pytest.mark.usefixtures('page_objects')
class TestAddPeopleCustomizations:

    def test_search_by_email_address(self):
        self.canvas_page.load_users_page(test.course_site)
        self.canvas_page.click_add_people()
        self.canvas_page.wait_for_text_in_element(self.canvas_page.ADD_USER_BY_EMAIL_LABEL, 'Email Address')
        self.canvas_page.click_add_by_email()
        expected_text = 'student@berkeley.edu, guest@example.com, gsi@berkeley.edu'
        utils.assert_equivalence(self.canvas_page.add_user_placeholder(), expected_text)

    def test_search_by_berkeley_uid(self):
        self.canvas_page.wait_for_text_in_element(self.canvas_page.ADD_USER_BY_UID_LABEL, 'Berkeley UID')
        self.canvas_page.click_add_by_uid()
        expected_text = '1032343, 11203443'
        utils.assert_equivalence(self.canvas_page.add_user_placeholder(), expected_text)

    def test_search_by_student_id(self):
        self.canvas_page.wait_for_text_in_element(self.canvas_page.ADD_USER_BY_SID_LABEL, 'Student ID')
        self.canvas_page.click_add_by_sid()
        expected_text = '25738808, UID:11203443'
        utils.assert_equivalence(self.canvas_page.add_user_placeholder(), expected_text)

    def test_how_to_link(self):
        title = 'IT Public KB - How do I add users to my course site?'
        assert self.canvas_page.is_external_link_valid(self.canvas_page.ADD_USER_HELP_LINK, title)

    def test_cal_net_gues_acct_instructions(self):
        title = 'IT Public KB - How can I access bCourses without a CalNet Account?'
        self.canvas_page.hit_escape()
        self.canvas_page.add_invalid_uid()
        assert self.canvas_page.is_external_link_valid(self.canvas_page.INVALID_USER_INFO_LINK, title)


@pytest.mark.usefixtures('page_objects')
class TestFindAPerson:

    def test_search_term_required(self):
        self.canvas_page.load_users_page(test.course_site)
        self.canvas_page.click_find_person_to_add()
        self.add_user_page.when_present(self.add_user_page.SEARCH_BUTTON, utils.get_short_timeout())
        assert not self.add_user_page.element(self.add_user_page.SEARCH_BUTTON).is_enabled()

    def test_search_by_name(self):
        self.add_user_page.search('Bear', 'Last Name, First Name')
        self.add_user_page.wait_for_uid_result(utils.get_oski_uid())

    def test_search_by_name_no_results(self):
        self.add_user_page.search('zyxwvu', 'Last Name, First Name')
        self.add_user_page.wait_for_no_results()

    def test_results_limited_to_20(self):
        self.add_user_page.search('Smith', 'Last Name, First Name')
        self.add_user_page.wait_for_name_results()
        assert len(self.add_user_page.name_results()) == 20
        self.add_user_page.wait_for_too_many_results()

    def test_search_by_email_results_limited_to_20(self):
        self.add_user_page.search('smith@berkeley', 'Email')
        self.add_user_page.wait_for_email_results()
        assert len(self.add_user_page.email_results()) == 20
        self.add_user_page.wait_for_too_many_results()

    def test_search_by_email_no_results(self):
        self.add_user_page.search('foo@bar', 'Email')
        self.add_user_page.wait_for_no_results()

    def test_search_by_uid(self):
        self.add_user_page.search(utils.get_oski_uid(), 'CalNet UID')
        self.add_user_page.wait_for_uid_result(utils.get_oski_uid())

    def test_search_by_uid_no_results(self):
        self.add_user_page.search('12324', 'CalNet UID')
        self.add_user_page.wait_for_no_results()

    def test_search_result_course_site_sections(self):
        self.add_user_page.search(utils.get_oski_uid(), 'CalNet UID')
        self.add_user_page.wait_for_uid_result(utils.get_oski_uid())
        assert len(self.add_user_page.visible_section_options()) == len(test.course_site.sections)


@pytest.mark.usefixtures('page_objects')
class TestAddAPerson:

    def test_load_tool(self):
        self.canvas_page.load_users_page(test.course_site)
        self.canvas_page.click_find_person_to_add()

    @pytest.mark.parametrize(argnames='user',
                             argvalues=[test.lead_ta, test.ta, test.designer, test.reader, test.observer,
                                        test.student, test.wait_list_student],
                             ids=[user.role for user in [test.lead_ta, test.ta, test.designer, test.reader,
                                                         test.observer, test.student, test.wait_list_student]],
                             scope='function')
    def test_add_users(self, user):
        self.add_user_page.search(user.uid, 'CalNet UID')
        self.add_user_page.add_user_by_uid(user, test.course_site.sections[0])

    def test_load_canvas_site_users(self):
        self.canvas_page.load_users_page(test.course_site)
        self.canvas_page.load_all_students(test.course_site)

    @pytest.mark.parametrize(argnames='user',
                             argvalues=[test.lead_ta, test.ta, test.designer, test.reader, test.observer,
                                        test.student, test.wait_list_student],
                             ids=[user.role for user in [test.lead_ta, test.ta, test.designer, test.reader,
                                                         test.observer, test.student, test.wait_list_student]],
                             scope='function')
    def test_verify_users_added(self, user):
        section = test.course_site.sections[0]
        self.canvas_page.search_user_by_canvas_id(user)
        self.canvas_page.wait_for_user(user)
        time.sleep(1)
        if user == test.observer:
            assert 'Observing: nobody' in self.canvas_page.roster_user_roles(user)
        else:
            assert user.role in self.canvas_page.roster_user_roles(user)
            assert f'{section.course} {section.label}' in self.canvas_page.roster_user_sections(user)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='user',
                         argvalues=[test.canvas_admin, test.lead_ta, test.ta],
                         ids=[user.role for user in [test.canvas_admin, test.lead_ta, test.ta]],
                         scope='class')
class TestUserRolesAdminTALeadTA:

    def test_tool_available_with_limited_roles(self, user):
        self.canvas_page.masquerade_as(user, test.course_site)
        self.canvas_page.load_users_page(test.course_site)
        self.canvas_page.click_find_person_to_add()
        self.add_user_page.search('Bear', 'Last Name, First Name')
        if user == test.canvas_admin:
            opts = ['Student', 'Waitlist Student', 'Teacher', 'TA', 'Lead TA', 'Reader', 'Designer', 'Observer']
        elif user == test.lead_ta:
            opts = ['Student', 'Waitlist Student', 'TA', 'Lead TA', 'Reader', 'Observer']
        else:
            opts = ['Student', 'Waitlist Student', 'Observer']
        assert self.add_user_page.visible_user_role_options() == opts

    def test_academic_policies_link_present(self, user):
        self.canvas_page.switch_to_default_content()
        assert self.canvas_page.is_present(self.canvas_page.POLICIES_LINK)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='user',
                         argvalues=[test.designer, test.reader],
                         ids=[user.role for user in [test.designer, test.reader]],
                         scope='class')
class TestUserRolesDesignerReader:

    def test_tool_inaccessible(self, user):
        self.canvas_page.masquerade_as(user, test.course_site)
        self.add_user_page.load_embedded_tool(test.course_site)
        self.add_user_page.wait_for_unauthorized_msg()

    def test_academic_policies_link_present(self, user):
        self.canvas_page.switch_to_default_content()
        assert self.canvas_page.is_present(self.canvas_page.POLICIES_LINK)


@pytest.mark.usefixtures('page_objects')
@pytest.mark.parametrize(argnames='user',
                         argvalues=[test.observer, test.student, test.wait_list_student],
                         ids=[user.role for user in [test.observer, test.student, test.wait_list_student]],
                         scope='class')
class TestUserRolesObserverStudents:
    POLICIES_HEADING = 'Academic Accommodations Hub | Executive Vice Chancellor and Provost'
    MENTAL_HEALTH_HEADING = 'Student Mental Health | University Health Services'

    def test_tool_inaccessible(self, user):
        self.canvas_page.maximize_window()
        self.canvas_page.masquerade_as(user, test.course_site)
        self.add_user_page.load_embedded_tool(test.course_site)
        self.add_user_page.wait_for_unauthorized_msg()

    def test_academic_policies_link_works_large_viewport(self, user):
        self.canvas_page.switch_to_default_content()
        assert self.canvas_page.is_external_link_valid(self.canvas_page.POLICIES_LINK, self.POLICIES_HEADING)

    def test_mental_health_resources_link_works_large_viewport(self, user):
        assert self.canvas_page.is_external_link_valid(self.canvas_page.MENTAL_HEALTH_LINK, self.MENTAL_HEALTH_HEADING)

    def test_academic_policies_link_works_small_viewport(self, user):
        self.canvas_page.reduce_window()
        self.canvas_page.expand_mobile_menu()
        assert self.canvas_page.is_external_link_valid(self.canvas_page.POLICIES_RESPONSIVE_LINK, self.POLICIES_HEADING)

    def test_mental_health_resources_link_works_small_viewport(self, user):
        assert self.canvas_page.is_external_link_valid(self.canvas_page.MENTAL_HEALTH_RESPONSIVE_LINK,
                                                       self.MENTAL_HEALTH_HEADING)
