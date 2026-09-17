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

from flask import current_app as app
from ripley.externals.data_loch import get_recently_active_project_sites
from ripley.jobs.base_job import BaseJob
from ripley.models.canvas_site_archival_status import CanvasSiteArchivalStatus


class BcoursesUpdateArchivalStatusJob(BaseJob):

    def _run(self, params={}):
        active_site_ids = [int(row['id']) for row in get_recently_active_project_sites()]

        removed_count = CanvasSiteArchivalStatus.delete_by_canvas_site_ids(active_site_ids)

        if removed_count == 0:
            result = 'No new activity found for project sites with archival status.'
        else:
            result = f'Removed archival status for {removed_count} recently active project site(s).'
        app.logger.info(result)
        return result

    @classmethod
    def description(cls):
        return 'Removes archival status for project sites with recent user activity.'

    @classmethod
    def key(cls):
        return 'bcourses_update_archival_status'
