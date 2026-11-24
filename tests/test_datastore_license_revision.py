# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2026 Pawel Wladzinski <pawel.wladzinski@vayana.pl>
"""Regressions for the 2026-11-20 revision of release 1.2.0."""
import unittest
from test_morpheus import State, agent, checks
from test_infrastructure import infra, states
from test_extended import extended


class DatastoreLicenseRevisionTests(unittest.TestCase):
    def storage(self, kind='Directory Pool'):
        return {'datastores': [{
            'id': 1, 'name': 'Example storage', 'type': kind, 'online': True,
            'status': 'provisioned', 'maintenanceStatus': 'available',
            'locations': [
                {'refType': 'ComputeServer', 'refId': 15, 'status': 'provisioned'},
                {'refType': 'ComputeServer', 'refId': 16, 'status': None},
                {'refType': 'ComputeServer', 'refId': 17},
                {'refType': 'ComputeServer', 'refId': 18, 'status': ''},
            ],
        }], 'hypervisors': [{'id': i, 'name': f'Host{i}'} for i in range(15, 19)]}

    def rows(self, section):
        return list(infra.check_datastore_state('Example storage', section))

    def test_local_directory_missing_secondary_statuses_are_informational(self):
        rows = self.rows(self.storage())
        self.assertEqual(max(states(rows)), State.OK)
        missing = [row for row in rows if 'status not reported' in getattr(row, 'notice', '')]
        self.assertEqual(len(missing), 3)
        self.assertTrue(any('Host Host16 (ID 16)' in row.notice for row in missing))

    def test_no_local_healthy_baseline_still_warns(self):
        data = self.storage()
        data['datastores'][0]['locations'][0]['status'] = None
        self.assertEqual(max(states(self.rows(data))), State.WARN)

    def test_local_reported_failures_and_warnings_remain_visible(self):
        for status, expected in [('failed', State.CRIT), ('warning', State.WARN),
                                 ('offline', State.CRIT), ('new-status', State.WARN)]:
            data = self.storage()
            data['datastores'][0]['locations'][1]['status'] = status
            self.assertEqual(max(states(self.rows(data))), expected)

    def test_local_missing_status_with_a_message_still_warns(self):
        data = self.storage()
        data['datastores'][0]['locations'][1]['statusMessage'] = 'Mount status unavailable'
        self.assertEqual(max(states(self.rows(data))), State.WARN)

    def test_null_global_online_and_status_are_not_suppressed(self):
        for key, value, expected in [('online', None, State.WARN), ('online', False, State.CRIT),
                                     ('status', None, State.WARN), ('status', 'failed', State.CRIT)]:
            data = self.storage()
            data['datastores'][0][key] = value
            self.assertEqual(max(states(self.rows(data))), expected)

    def test_shared_and_unknown_datastores_require_location_statuses(self):
        for kind in ('NFS Pool', 'GFS2 Pool (Global File System 2)', 'vmfs', 'generic', None):
            self.assertEqual(max(states(self.rows(self.storage(kind)))), State.WARN)

    def test_datastore_names_never_determine_locality(self):
        data = self.storage(None)
        data['datastores'][0]['name'] = 'local'
        rows = list(infra.check_datastore_state('local', data))
        self.assertEqual(max(states(rows)), State.WARN)

    def test_shared_evidence_overrides_directory_label(self):
        for fields in ({'externalType': 'dir:gfs2'}, {'externalType': 'netfs'},
                       {'multipath': {'multipathPaths': 8}},
                       {'datastoreType': {'code': 'hvm-nfs'}}):
            data = self.storage()
            data['datastores'][0].update(fields)
            self.assertEqual(infra.datastore_scope(data['datastores'][0]), 'shared')
            self.assertEqual(max(states(self.rows(data))), State.WARN)

    def test_empty_multipath_placeholders_do_not_make_a_local_pool_shared(self):
        for paths in ({'multipathPaths': None}, {'multipathPaths': 0, 'multipathState': None}):
            data = self.storage()
            data['datastores'][0]['multipath'] = paths
            self.assertEqual(infra.datastore_scope(data['datastores'][0]), 'local')
            self.assertEqual(max(states(self.rows(data))), State.OK)

    def test_location_identity_uses_reference_type_before_matching_ids(self):
        data = self.storage()
        self.assertEqual(infra.location_label({'refType': 'ComputeZone', 'refId': 15}, data),
                         'Location 15 (ComputeZone)')
        self.assertEqual(infra.location_label({'refType': 'ComputeServer', 'refId': 99}, data),
                         'Host ID 99')
        data['datastores'][0]['locations'][1].pop('refType')
        self.assertEqual(max(states(self.rows(data))), State.WARN)

    def test_datastore_normalization_preserves_only_selected_type_fields(self):
        raw = {'id': 1, 'type': 'Directory Pool', 'externalType': 'dir',
               'datastoreType': {'id': 5, 'code': 'directory', 'name': 'Directory Pool',
                                 'password': 'EXAMPLE_SECRET'}, 'locations': None}
        result = agent.normalize_datastore(raw, {'id': 1}, None, {})
        self.assertEqual(result['type'], 'Directory Pool')
        self.assertEqual(result['externalType'], 'dir')
        self.assertEqual(result['datastoreType'], {'id': 5, 'code': 'directory', 'name': 'Directory Pool'})
        self.assertEqual(result['locations'], [])

    def test_cluster_response_retains_cloud_type_metadata(self):
        class API:
            def listing(self, endpoint, key, **filters):
                if endpoint == 'servers': return []
                if endpoint == 'clusters': return [{'id': 1, 'name': 'Cluster', 'zone': {'id': 1}}]
                result = {'id': 1, 'name': 'Example storage'}
                if endpoint.startswith('zones/'):
                    result.update(type='Directory Pool', externalType='dir',
                                  datastoreType={'id': 5, 'name': 'Directory Pool'})
                else:
                    result.update(type='generic', datastoreType={'id': 5, 'name': None})
                return [result]
        data = agent.collect_infrastructure(API(), [{'id': 1}])
        store = data['datastores'][0]
        self.assertEqual(store['type'], 'Directory Pool')
        self.assertEqual(store['externalType'], 'dir')
        self.assertEqual(infra.datastore_scope(store), 'local')

    def test_valid_license_ratio_wins_over_allocation_flags(self):
        for used, maximum, expected in [(0, 0, State.OK), (4, 8, State.OK),
                                         (8, 8, State.OK), (9, 8, State.CRIT), (1, 0, State.CRIT)]:
            section = {'license': {'success': True, 'data': {'limits': [
                {'code': 'sockets', 'used': used, 'max': maximum,
                 'warning': True, 'limitReached': True}
            ]}}}
            rows = list(extended.check_license_limit('sockets', section))
            self.assertEqual(max(states(rows)), expected)

    def test_invalid_license_values_remain_unknown(self):
        for used in (None, -1, True, float('nan'), '8'):
            section = {'license': {'success': True, 'data': {'limits': [
                {'code': 'sockets', 'used': used, 'max': 8}
            ]}}}
            self.assertEqual(max(states(list(extended.check_license_limit('sockets', section)))), State.UNKNOWN)

    def test_build_revision_is_visible_without_new_service_identity(self):
        rows = list(checks.check_api({'success': True, 'vm_count': 8, 'cloud_count': 1,
                                     'duration': 1.0, 'version': agent.VERSION,
                                     'revision': agent.BUILD_REVISION}))
        self.assertEqual(rows[0].summary, 'Collected 8 VMs, 1 clouds')
        self.assertTrue(any('build revision: 2026-11-20' in getattr(row, 'notice', '') for row in rows))
        self.assertEqual(agent.VERSION, '1.2.0')


if __name__ == '__main__':
    unittest.main()
