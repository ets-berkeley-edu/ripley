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

from ripley.jobs.bcourses_update_archival_status import BcoursesUpdateArchivalStatusJob
from ripley.models.canvas_site_archival_status import CanvasSiteArchivalStatus


class TestBcoursesUpdateArchivalStatusJob:

    def test_removes_archival_status_for_recently_active_project_site(self, app, db):
        """Removes the archival status row for a project site with recent activity."""
        CanvasSiteArchivalStatus.create(canvas_site_id=1234567, archival_tier='2028')
        result = BcoursesUpdateArchivalStatusJob(app)._run()
        assert CanvasSiteArchivalStatus.find_by_canvas_site_id(1234567) is None
        assert '1' in result

    def test_leaves_archival_status_for_stale_project_site(self, app, db):
        """Leaves the archival status row alone when the project site has no recent activity."""
        CanvasSiteArchivalStatus.create(canvas_site_id=2345678, archival_tier='2028')
        BcoursesUpdateArchivalStatusJob(app)._run()
        assert CanvasSiteArchivalStatus.find_by_canvas_site_id(2345678) is not None

    def test_leaves_archival_status_for_deleted_project_site(self, app, db):
        """Leaves the archival status row alone when the project site has been deleted, despite recent activity."""
        CanvasSiteArchivalStatus.create(canvas_site_id=3456789, archival_tier='2028')
        BcoursesUpdateArchivalStatusJob(app)._run()
        assert CanvasSiteArchivalStatus.find_by_canvas_site_id(3456789) is not None

    def test_leaves_archival_status_for_non_project_site(self, app, db):
        """Leaves the archival status row alone for a recently active course site outside the project sites account."""
        CanvasSiteArchivalStatus.create(canvas_site_id=4567890, archival_tier='2028')
        BcoursesUpdateArchivalStatusJob(app)._run()
        assert CanvasSiteArchivalStatus.find_by_canvas_site_id(4567890) is not None

    def test_no_matching_archival_status(self, app, db):
        """Handles project sites with recent activity that have no corresponding archival status row."""
        result = BcoursesUpdateArchivalStatusJob(app)._run()
        assert result == 'No new activity found for project sites with archival status.'
