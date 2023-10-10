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

from datetime import timedelta
import re
import tempfile

from flask import current_app as app
from ripley.externals import s3
from ripley.jobs.base_job import BaseJob
from ripley.lib.berkeley_term import BerkeleyTerm
from ripley.lib.util import utc_now


class CompareSisImportCsvs(BaseJob):

    def _run(self, params={}):
        timestamp = utc_now().strftime('%F_%H-%M-%S')

        junction_csvs, ripley_csvs = _collect_csv_keys(days_ago=params.get('days_ago', 1))
        junction_lines = {}
        ripley_lines = {}

        for csv_key in junction_csvs.keys():
            app.logger.info(f'DARE TO COMPARE! {csv_key}')
            junction_lines[csv_key] = set()
            ripley_lines[csv_key] = set()

            for junction_s3_key in junction_csvs[csv_key]:
                app.logger.info(f'Found Junction CSV: {junction_s3_key}')
                header = None
                for line in s3.stream_object_text(junction_s3_key, bucket=app.config['JUNCTION_COMPARISON_CSV_BUCKET']):
                    if not header:
                        header = line
                    else:
                        junction_lines[csv_key].add(line)

            for ripley_s3_key in ripley_csvs[csv_key]:
                app.logger.info(f'Found Ripley CSV: {ripley_s3_key}')
                header = None
                for line in s3.stream_object_text(ripley_s3_key):
                    if not header:
                        header = line
                    else:
                        ripley_lines[csv_key].add(line)

            junction_not_ripley = junction_lines[csv_key].difference(ripley_lines[csv_key])
            app.logger.info(f'{csv_key}: found {len(junction_not_ripley)} lines in Junction but not Ripley')
            if len(junction_not_ripley):
                junction_not_ripley_file = tempfile.NamedTemporaryFile()
                with open(junction_not_ripley_file.name, 'w') as f:
                    f.write(header)
                    for line in junction_not_ripley:
                        f.write(line)
                s3.upload_dated_csv(junction_not_ripley_file.name, f'{csv_key}-junction-not-ripley', 'junction_diffs', timestamp)

            ripley_not_junction = ripley_lines[csv_key].difference(junction_lines[csv_key])
            app.logger.info(f'{csv_key}: found {len(ripley_not_junction)} lines in Ripley but not Junction')
            if len(ripley_not_junction):
                ripley_not_junction_file = tempfile.NamedTemporaryFile()
                with open(ripley_not_junction_file.name, 'w') as f:
                    f.write(header)
                    for line in ripley_not_junction:
                        f.write(line)
                s3.upload_dated_csv(ripley_not_junction_file.name, f'{csv_key}-ripley-not-junction', 'junction_diffs', timestamp)

    @classmethod
    def description(cls):
        return 'Compare Canvas SIS import CSVs between Ripley and Junction.'

    @classmethod
    def key(cls):
        return 'compare_sis_import_csvs'


def _collect_csv_keys(days_ago): # noqa C901
    csv_keys = [
        'users-initial',
        'users-update',
        'sis-ids-update',
    ]
    for t in BerkeleyTerm.get_current_terms().values():
        term_id = '-'.join([t.year, t.season])
        csv_keys.append(f'enrollments-{t.year}-{t.season}-initial')
        csv_keys.append(f'enrollments-{t.year}-{t.season}-update')

    junction_csvs = {k: [] for k in csv_keys}
    ripley_csvs = {k: [] for k in csv_keys}

    datestamp = (utc_now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

    for key in s3.get_keys_with_prefix(f'provisioned-users-{datestamp}', app.config['JUNCTION_COMPARISON_CSV_BUCKET']):
        junction_csvs['users-initial'].append(key)

    for key in s3.get_keys_with_prefix(f'canvas-{datestamp}', app.config['JUNCTION_COMPARISON_CSV_BUCKET']):
        if 'term-enrollments-export' in key:
            term_id = _get_term_id(key)
            if term_id:
                junction_csvs[f'enrollments-{term_id}-initial'].append(key)
        elif 'users' in key and 'users-report' not in key:
            junction_csvs['users-update'].append(key)
        elif 'sis-ids' in key:
            junction_csvs['sis-ids-update'].append(key)
        elif 'enrollments' in key:
            term_id = _get_term_id(key)
            if 'term-enrollments-export' in key and f'enrollments-{term_id}-initial' in junction_csvs:
                junction_csvs[f'enrollments-{term_id}-initial'].append(key)
            elif f'enrollments-{term_id}-update' in junction_csvs:
                junction_csvs[f'enrollments-{term_id}-update'].append(key)

    for key in s3.iterate_monthly_folder('canvas_provisioning_reports'):
        if not _within_daily_window(key, days_ago):
            continue
        if 'user-provision-report' in key:
            ripley_csvs['users-initial'].append(key)
        elif 'enrollments-export' in key:
            term_id = _get_term_id(key)
            if term_id:
                ripley_csvs[f'enrollments-{term_id}-initial'].append(key)

    for key in s3.iterate_monthly_folder('canvas_sis_imports'):
        if not _within_daily_window(key, days_ago):
            continue
        if 'user-sis-import' in key:
            ripley_csvs['users-update'].append(key)
        elif 'sis-id-sis-import' in key:
            ripley_csvs['sis-ids-update'].append(key)
        elif 'enrollments-TERM' in key and 'sis-import' in key:
            term_id = _get_term_id(key)
            if term_id:
                ripley_csvs[f'enrollments-{term_id}-update'].append(key)

    return junction_csvs, ripley_csvs


def _get_term_id(string):
    match = re.search('20\\d{2}-[BCD]', string)
    if match and match[0]:
        return match[0]


def _within_daily_window(string, days_ago):
    match = re.search('\\d{4}-\\d{2}-\\d{2}_\\d{2}-\\d{2}-\\d{2}', string)
    if not match or not match[0]:
        return False

    end_cutoff = (utc_now() - timedelta(days=(days_ago - 1))).replace(hour=7, minute=0, second=0)
    start_cutoff = end_cutoff - timedelta(days=1)
    timestamp_format = '%F_%H-%M-%S'

    if match[0] > start_cutoff.strftime(timestamp_format) and match[0] < end_cutoff.strftime(timestamp_format):
        return True
    else:
        return False
