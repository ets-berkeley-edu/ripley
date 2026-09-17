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

from ripley import db, std_commit
from ripley.lib.util import to_isoformat
from ripley.models.base import Base


class CanvasSiteArchivalStatus(Base):
    __tablename__ = 'canvas_site_archival_status'

    canvas_site_id = db.Column(db.Integer, nullable=False, primary_key=True)
    opted_out = db.Column(db.Boolean, nullable=False)
    archival_tier = db.Column(db.String(4), nullable=False)

    def __init__(self, canvas_site_id, archival_tier):
        self.canvas_site_id = canvas_site_id
        self.archival_tier = archival_tier
        self.opted_out = False

    @classmethod
    def create(cls, canvas_site_id, archival_tier):
        archival_status = cls.query.filter_by(canvas_site_id=canvas_site_id).first()
        if archival_status:
            raise ValueError(f'Archival status with Canvas site id {canvas_site_id} already exists')
        archival_status = cls(canvas_site_id=canvas_site_id, archival_tier=archival_tier)
        db.session.add(archival_status)
        std_commit()
        return archival_status

    @classmethod
    def delete(cls, canvas_site_id):
        archival_status = cls.query.filter_by(canvas_site_id=canvas_site_id).first()
        if archival_status:
            db.session.delete(archival_status)
            std_commit()

    @classmethod
    def delete_by_canvas_site_ids(cls, canvas_site_ids):
        count = cls.query.filter(cls.canvas_site_id.in_(canvas_site_ids)).delete(synchronize_session=False)
        std_commit()
        return count

    @classmethod
    def add_opt_out(cls, canvas_site_id):
        archival_status = cls.query.filter_by(canvas_site_id=canvas_site_id).first()
        if archival_status:
            archival_status.opted_out = True
            std_commit()
            return archival_status

    @classmethod
    def remove_opt_out(cls, canvas_site_id):
        archival_status = cls.query.filter_by(canvas_site_id=canvas_site_id).first()
        if archival_status:
            archival_status.opted_out = False
            std_commit()
            return archival_status

    @classmethod
    def find_by_canvas_site_id(cls, canvas_site_id):
        return cls.query.filter_by(canvas_site_id=canvas_site_id).first()

    @classmethod
    def find_by_canvas_site_ids(cls, canvas_site_ids):
        return cls.query.filter(cls.canvas_site_id.in_(canvas_site_ids)).all()

    def to_api_json(self):
        return {
            'canvasSiteId': self.canvas_site_id,
            'optedOut': self.opted_out,
            'archivalTier': self.archival_tier,
            'createdAt': to_isoformat(self.created_at),
            'updatedAt': to_isoformat(self.updated_at),
        }
