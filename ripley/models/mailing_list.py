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

import re

from flask import current_app as app
from ripley import db, std_commit
from ripley.externals import canvas, data_loch
from ripley.lib.berkeley_term import BerkeleyTerm
from ripley.lib.canvas_user_utils import has_instructing_role, is_project_maintainer, is_project_owner
from ripley.lib.mailing_list_utils import send_welcome_emails
from ripley.lib.util import to_isoformat, utc_now
from ripley.models.base import Base
from ripley.models.mailing_list_members import MailingListMembers
from unidecode import unidecode


class MailingList(Base):
    __tablename__ = 'canvas_site_mailing_lists'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    canvas_site_id = db.Column(db.Integer, nullable=False)
    canvas_site_name = db.Column(db.String(255))
    list_name = db.Column(db.String(255))
    members_count = db.Column(db.Integer)
    populate_add_errors = db.Column(db.Integer)
    populated_at = db.Column(db.DateTime)
    populate_remove_errors = db.Column(db.Integer)
    welcome_email_active = db.Column(db.Boolean, nullable=False)
    welcome_email_body = db.Column(db.Text)
    welcome_email_subject = db.Column(db.Text)
    # Members
    mailing_list_members = db.relationship(
        'MailingListMembers',
        back_populates='mailing_list',
        cascade='all, delete-orphan',
    )

    def __init__(self, canvas_site_id):
        self.canvas_site_id = canvas_site_id
        self.welcome_email_active = False

    @classmethod
    def find_by_canvas_site_id(cls, canvas_site_id):
        mailing_list = cls.query.filter_by(canvas_site_id=canvas_site_id).first()
        if mailing_list:
            mailing_list._initialize()
        return mailing_list

    @classmethod
    def create(cls, canvas_site_id, list_name=None):
        mailing_list = cls.query.filter_by(canvas_site_id=canvas_site_id).first()
        if mailing_list:
            raise ValueError(f'List with id {canvas_site_id} already exists')

        mailing_list = cls(canvas_site_id=canvas_site_id)
        mailing_list._initialize()
        # Admins can optionally override the mailing list name.
        if list_name:
            mailing_list.list_name = list_name

        db.session.add(mailing_list)
        std_commit()
        return mailing_list

    @classmethod
    def populate(cls, mailing_list):
        course = canvas.get_course(course_id=mailing_list.canvas_site_id)
        canvas_course_users = list(course.get_users(include=('email', 'enrollments')))
        mailing_list_members = MailingListMembers.get_mailing_list_members(
            include_deleted=True,
            mailing_list_id=mailing_list.id,
        )
        mailing_list, update_summary = cls._update_memberships(
            canvas_course_users=canvas_course_users,
            mailing_list=mailing_list,
            mailing_list_members=mailing_list_members,
        )
        if mailing_list.welcome_email_active and mailing_list.welcome_email_body and mailing_list.welcome_email_subject:
            send_welcome_emails()
        return mailing_list, update_summary

    @classmethod
    def update_population_metadata(
            cls,
            mailing_list_id,
            members_count,
            populate_add_errors,
            populate_remove_errors,
            populated_at,
    ):
        mailing_list = cls.query.filter_by(id=mailing_list_id).first()
        if mailing_list:
            mailing_list.members_count = members_count
            mailing_list.populate_add_errors = populate_add_errors
            mailing_list.populate_remove_errors = populate_remove_errors
            mailing_list.populated_at = populated_at
            db.session.add(mailing_list)
            std_commit()
        return mailing_list

    def to_api_json(self):
        with_welcomed_at = list(filter(lambda m: m.welcomed_at, self.mailing_list_members or []))
        welcome_email_last_sent = max([m.welcomed_at for m in with_welcomed_at]) if with_welcomed_at else None
        return {
            'canvasSite': {
                'canvasCourseId': self.canvas_site_id,
                'courseCode': self.canvas_site.course_code if self.canvas_site else None,
                'name': self.canvas_site_name,
                'sisCourseId': self.canvas_site.sis_course_id if self.canvas_site else None,
                'term': self._canvas_site_term_json(),
                'url': f"{app.config['CANVAS_API_URL']}/courses/{self.canvas_site_id}",
            },
            'domain': app.config['MAILGUN_DOMAIN'],
            'id': self.id,
            'membersCount': len(self.mailing_list_members),
            'name': self.list_name,
            'populatedAt': to_isoformat(self.populated_at),
            'welcomeEmailActive': self.welcome_email_active,
            'welcomeEmailBody': self.welcome_email_body,
            'welcomeEmailLastSent': welcome_email_last_sent,
            'welcomeEmailSubject': self.welcome_email_subject,
            'createdAt': to_isoformat(self.created_at),
            'updatedAt': to_isoformat(self.updated_at),
        }

    def _canvas_site_term_json(self):
        api_json = None
        if self.canvas_site:
            canvas_sis_term_id = self.canvas_site.term['sis_term_id']
            term = BerkeleyTerm.from_canvas_sis_term_id(canvas_sis_term_id)
            if term:
                api_json = {
                    'term_yr': term.year,
                    'term_cd': term.season,
                    'name': term.to_english(),
                }
        return api_json

    def _initialize(self):
        self.canvas_site = canvas.get_course(self.canvas_site_id)
        if self.canvas_site:
            self.canvas_site_name = self.canvas_site.name.strip()
            normalized_name = unidecode(self.canvas_site_name.lower())
            self.list_name = '-'.join([word for word in re.split('[^a-z0-9]+', normalized_name) if word])[0:45]
            term = BerkeleyTerm.from_canvas_sis_term_id(self.canvas_site.term['sis_term_id'])
            if term:
                self.list_name += '-' + term.to_abbreviation()
            else:
                self.list_name += '-list'

    @classmethod
    def _update_memberships(cls, canvas_course_users, mailing_list, mailing_list_members):
        summary = {
            'add': {
                'errors': [],
                'successes': [],
                'total': 0,
            },
            'remove': {
                'errors': [],
                'successes': [],
                'total': 0,
            },
            'update': {
                'errors': [],
                'successes': [],
                'total': 0,
            },
            'welcomeEmails': {
                'successes': [],
                'total': 0,
            },
        }
        # Track by email address
        mailing_list_members_by_email = {m.email_address.lower(): m for m in mailing_list_members}
        active_mailing_list_members = list(filter(lambda m: not m.deleted_at, mailing_list_members))
        email_addresses_of_active_mailing_list_members = [m.email_address.lower() for m in active_mailing_list_members]

        count_per_chunk = 10000
        for chunk in range(0, len(canvas_course_users), count_per_chunk):
            canvas_user_chunk = canvas_course_users[chunk:chunk + count_per_chunk]
            uids = [u.login_id for u in canvas_user_chunk]
            loch_users_by_uid = {u['ldap_uid']: u for u in data_loch.get_users(uids=uids)}

            for course_user in canvas_user_chunk:
                uid = course_user.login_id
                loch_user = loch_users_by_uid[uid]
                loch_user_email = loch_user['email_address']
                preferred_email = _get_preferred_email(
                    canvas_user_email=course_user.email,
                    loch_user_email=loch_user_email,
                )
                user = {
                    **{
                        'affiliations': loch_user['affiliations'],
                        'firstName': loch_user['first_name'],
                        'emailAddress': loch_user_email,
                        'lastName': loch_user['last_name'],
                        'personType': loch_user['person_type'],
                        'sid': loch_user['sid'],
                        'uid': uid,
                    },
                    'canSend': _can_send(course_user),
                    'preferredEmail': preferred_email,
                }
                if preferred_email:
                    _remove_from_list_safely(
                        item=preferred_email,
                        list_of_items=email_addresses_of_active_mailing_list_members,
                    )
                    existing_member = mailing_list_members_by_email.get(preferred_email)
                    if existing_member:
                        if existing_member.deleted_at:
                            summary['add']['total'] += 1
                            app.logger.debug(f'Reactivating previously deleted address {preferred_email}')
                            success = MailingListMembers.update(
                                can_send=user['canSend'],
                                deleted_at=None,
                                first_name=user['firstName'],
                                last_name=user['lastName'],
                                mailing_list_member_id=existing_member.id,
                            )
                            key = 'successes' if success else 'errors'
                            summary['add'][key].append(preferred_email)
                        else:
                            update_required = user['canSend'] != existing_member.can_send or \
                                user['firstName'] != existing_member.first_name or \
                                user['lastName'] != existing_member.last_name
                            if update_required:
                                summary['update']['total'] += 1
                                app.logger.debug(f'Updating user {preferred_email} of mailing_list {mailing_list.id}')
                                success = MailingListMembers.update(
                                    can_send=user['canSend'],
                                    deleted_at=user['deletedAt'],
                                    first_name=user['firstName'],
                                    last_name=user['lastName'],
                                    mailing_list_member_id=existing_member.id,
                                )
                                key = 'successes' if success else 'errors'
                                summary['update'][key].append(preferred_email)
                    else:
                        # Address is not currently in the list. Add it.
                        summary['add']['total'] += 1
                        app.logger.debug(f'Adding user {preferred_email}')
                        success = MailingListMembers.create(
                            can_send=user['canSend'],
                            email_address=user['emailAddress'],
                            first_name=user['firstName'],
                            last_name=user['lastName'],
                            mailing_list_id=mailing_list.id,
                        )
                        key = 'successes' if success else 'errors'
                        summary['add'][key].append(preferred_email)
                else:
                    app.logger.warn(f"No email address found for UID {user['uid']}")

        # Email addresses NOT accounted for above must now be removed from the db.
        summary['remove']['total'] = len(email_addresses_of_active_mailing_list_members)
        for email_address in email_addresses_of_active_mailing_list_members:
            app.logger.debug(f'Removing {email_address} from mailing_list {mailing_list.id}')
            mailing_list_member = mailing_list_members_by_email[email_address]
            if mailing_list_member:
                MailingListMembers.delete(mailing_list_member.id)
            key = 'successes' if mailing_list_member else 'errors'
            summary['remove'][key].append(email_address)

        members = MailingListMembers.get_mailing_list_members(mailing_list_id=mailing_list.id)
        cls.update_population_metadata(
            mailing_list_id=mailing_list.id,
            members_count=len(members),
            populate_add_errors=len(summary['add']['errors']),
            populate_remove_errors=len(summary['remove']['errors']),
            populated_at=utc_now(),
        )
        mailing_list = cls.query.filter_by(id=mailing_list.id).first()
        _log_summary_of_mailing_list_updates(mailing_list, summary)
        return mailing_list, summary


def _can_send(canvas_course_user):
    return has_instructing_role(canvas_course_user) or \
        is_project_maintainer(canvas_course_user) or \
        is_project_owner(canvas_course_user)


def _get_preferred_email(canvas_user_email, loch_user_email):
    preferred_email_source = app.config['MAILING_LISTS_PREFERRED_EMAIL_SOURCE']
    preferred_email = None
    if preferred_email_source == 'DATA_LOCH':
        preferred_email = loch_user_email or canvas_user_email
    # elif preferred_email_source == 'CALNET':
    #     TODO: Do we need to support this option?
    #     preferred_email = ???
    elif preferred_email_source == 'CANVAS':
        preferred_email = canvas_user_email or loch_user_email
    return preferred_email.lower() if preferred_email else None


def _log_summary_of_mailing_list_updates(mailing_list, summary):
    info_log = []
    list_name = mailing_list.list_name

    add_errors = summary['add']['errors']
    remove_errors = summary['remove']['errors']
    remove_successes = summary['remove']['successes']
    update_errors = summary['update']['errors']
    update_successes = summary['update']['successes']
    update_total = summary['update']['total']

    def _log(statement):
        info_log.append(statement)

    _log(f'Finished population of mailing list {list_name}.')
    if add_errors:
        fails = ', '.join(add_errors)
        app.logger.error(f'[ERROR] Failed to add {len(add_errors)} addresses to {list_name}: {fails}')
    _log(f"Removed {remove_successes} of {summary['remove']['total']} former site members.")
    if remove_errors:
        fails = ', '.join(remove_errors)
        app.logger.error(f'[ERROR] Failed to remove {remove_errors.count} addresses from {list_name}: {fails}')
    _log(f'Updated {update_successes} of {update_total} new site members.')
    if update_errors:
        fails = ', '.join(update_errors)
        app.logger.error(f'[ERROR] Failed to update {update_errors.count} addresses in {list_name}: {fails}')
    # Log it all.
    app.logger.info('\n' + '\n'.join(info_log) + '\n')


def _remove_from_list_safely(item, list_of_items):
    if item in list_of_items:
        list_of_items.remove(item)
