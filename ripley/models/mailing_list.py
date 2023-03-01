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

from ripley import db, std_commit
from ripley.externals import canvas
from ripley.lib.berkeley_term import BerkeleyTerm
from ripley.models.base import Base
from unidecode import unidecode


class MailingList(Base):
    __tablename__ = 'canvas_site_mailing_lists'

    id = db.Column(db.Integer, nullable=False, primary_key=True)  # noqa: A003
    canvas_site_id = db.Column(db.Integer, nullable=False)
    canvas_site_name = db.Column(db.String(255))
    list_name = db.Column(db.String(255))
    members_count = db.Column(db.Integer)
    populate_add_errors = db.Column(db.Integer)
    populate_remove_errors = db.Column(db.Integer)
    welcome_email_active = db.Column(db.Boolean, nullable=False)
    welcome_email_body = db.Column(db.Text)
    welcome_email_subject = db.Column(db.Text)

    def __init__(self, canvas_site_id):
        self.canvas_site_id = canvas_site_id

    @classmethod
    def find_or_initialize(cls, canvas_site_id):
        mailing_list = cls.query.filter_by(canvas_site_id=canvas_site_id).first()
        if not mailing_list:
            mailing_list = cls(canvas_site_id=canvas_site_id)
            mailing_list.initalize()
        return mailing_list

    @classmethod
    def create(cls, canvas_site_id, list_name=None):
        mailing_list = cls.query.filter_by(canvas_site_id=canvas_site_id).first()
        if mailing_list:
            raise ValueError(f'List with id {canvas_site_id} already exists')

        mailing_list = cls(canvas_site_id=canvas_site_id)
        mailing_list.initalize()
        # Admins can optionally override the mailing list name.
        if list_name:
            mailing_list.list_name = list_name

        db.session.add(mailing_list)
        std_commit()
        return mailing_list

    def initalize(self):
        self.canvas_site = canvas.get_course(self.canvas_site_id)
        if self.canvas_site:
            self.canvas_site_name = self.canvas_site.name.strip()

            # 'CHEM 1A LEC 003' => 'chem-1a-lec-003-sp15'
            # {{design}} => 'design-sp15'
            # 'The "Wild"-"Wild" West?' => 'the-wild-wild-west-sp15'
            # 'Conversation intermédiaire' => 'conversation-intermediaire-sp15'
            # 'Global Health: Disaster Preparedness and Response' => 'global-health-disaster-preparedness-and-respo-sp15'

            normalized_name = unidecode(self.canvas_site_name.lower())
            self.list_name = '-'.join([word for word in re.split('[^a-z0-9]+', normalized_name) if word])[0:45]
            term = BerkeleyTerm.from_canvas_sis_term_id(self.canvas_site.term['sis_term_id'])
            if term:
                self.list_name += '-' + term.to_abbreviation()
            else:
                self.list_name += '-list'