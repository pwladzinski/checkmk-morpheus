# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2026 Pawel Wladzinski <pawel.wladzinski@vayana.pl>
"""Regression cases for maintenance, partial status and real failures."""
import unittest
from test_morpheus import State, agent, checks
from test_infrastructure import fixture, infra, states
from test_extended import extended, fixture as extended_fixture
from cmk_addons.plugins.morpheus.lib.status import operational_state


class StatusPolicyTests(unittest.TestCase):
    def test_missing_and_new_operational_states_warn(self):
        for value in (None, '', '  ', 'unknown', 'new-provider-status'):
            with self.subTest(value=value):
                self.assertEqual(operational_state(value), State.WARN)

    def test_lifecycle_operations_warn(self):
        for value in ('maintenancing', 'maintenance', 'provisioning', 'syncing',
                      'migrating', 'stopping', 'resuming', 'pending', 'drifted'):
            self.assertEqual(operational_state(value), State.WARN, value)

    def test_failures_remain_critical(self):
        for value in ('failed', 'error', 'offline', 'unclean', 'fenced', 'unreachable', 'lost', 'nr', 'cr'):
            self.assertEqual(operational_state(value), State.CRIT, value)

    def test_healthy_status_whitespace_and_case(self):
        for value in (' PROVISIONED ', 'Mounted', 'online', 'In_Sync'):
            self.assertEqual(operational_state(value), State.OK, value)

    def test_maintenance_is_detected_before_api_flag_changes(self):
        data = fixture()
        host = data['hypervisors'][0]
        host.update(status='maintenancing', powerState='on', maintenanceMode=False,
                    serverGroupMemberStatus='online')
        item = infra.item_name(host)
        rows = list(infra.check_hypervisor_state(item, data))
        self.assertEqual(max(states(rows)), State.WARN)
        self.assertTrue(any(getattr(row, 'summary', '') == 'Maintenance: True' for row in rows))
        self.assertEqual(max(states(list(infra.check_hypervisor_cpu(item, {}, data)))), State.OK)

    def test_completed_maintenance_can_be_offline(self):
        data = fixture()
        host = data['hypervisors'][0]
        host.update(status='maintenance', powerState='off', maintenanceMode=False,
                    serverGroupMemberStatus='offline')
        item = infra.item_name(host)
        self.assertEqual(max(states(list(infra.check_hypervisor_state(item, data)))), State.WARN)
        for check in (infra.check_hypervisor_cpu, infra.check_hypervisor_memory, infra.check_hardware):
            rows = list(check(item, {}, data))
            self.assertEqual(max(states(rows)), State.WARN)
            self.assertFalse(any(row.args for row in rows))

    def test_explicit_host_failure_wins_over_planned_offline_membership(self):
        host = {'status': 'failed', 'powerState': 'off',
                'maintenanceMode': True, 'serverGroupMemberStatus': 'offline'}
        self.assertEqual(infra.hypervisor_blocked(host)[0], State.CRIT)

    def test_reported_offline_status_in_completed_maintenance_warns(self):
        host = {'status': 'offline', 'powerState': 'off',
                'maintenanceMode': True, 'serverGroupMemberStatus': 'offline'}
        self.assertEqual(infra.hypervisor_blocked(host)[0], State.WARN)

    def test_power_loss_during_evacuation_remains_critical(self):
        host = {'status': 'maintenancing', 'powerState': 'off', 'maintenanceMode': False}
        self.assertEqual(infra.hypervisor_blocked(host)[0], State.CRIT)

    def test_fencing_during_maintenance_remains_critical(self):
        for member in ('unclean', 'fenced', 'unreachable', 'lost'):
            host = {'status': 'maintenance', 'powerState': 'unknown',
                    'maintenanceMode': True, 'serverGroupMemberStatus': member}
            self.assertEqual(infra.hypervisor_blocked(host)[0], State.CRIT)

    def test_partial_datastore_locations_warn_and_name_missing_status(self):
        data = fixture()
        store = data['datastores'][0]
        store.update(online=True, status='provisioned', maintenanceStatus='available',
                     locations=[{'refId': 1, 'status': 'provisioned'}, {'refId': 2, 'status': None}, {'refId': 3}])
        rows = list(infra.check_datastore_state(infra.item_name(store), data))
        self.assertEqual(max(states(rows)), State.WARN)
        self.assertTrue(any('Location 2: not reported' == getattr(row, 'summary', '') for row in rows))
        store['locations'].append({'refId': 4, 'status': 'failed'})
        self.assertEqual(max(states(list(infra.check_datastore_state(infra.item_name(store), data)))), State.CRIT)

    def test_datastore_online_null_is_warning_not_offline(self):
        data = fixture()
        store = data['datastores'][0]
        store.update(online=None, status='provisioned', locations=[])
        self.assertEqual(max(states(list(infra.check_datastore_state(infra.item_name(store), data)))), State.WARN)
        store['online'] = False
        self.assertEqual(max(states(list(infra.check_datastore_state(infra.item_name(store), data)))), State.CRIT)

    def test_cluster_sync_remains_healthy_but_incomplete_members_warn(self):
        data = fixture()
        cluster = data['clusters'][0]
        cluster.update(status='syncing', ha_enabled=False)
        item = infra.item_name(cluster)
        self.assertEqual(max(states(list(infra.check_cluster(item, {}, data)))), State.OK)
        cluster['members'][0]['serverGroupMemberStatus'] = None
        self.assertEqual(max(states(list(infra.check_cluster(item, {}, data)))), State.WARN)
        cluster['members'][0]['serverGroupMemberStatus'] = 'unclean'
        cluster['lastSync'] = None
        self.assertEqual(max(states(list(infra.check_cluster(item, {}, data)))), State.CRIT)

    def test_cluster_offline_member_has_explicit_maintenance_context(self):
        data = fixture()
        cluster = data['clusters'][0]
        cluster['members'][0].update(status='maintenance', serverGroupMemberStatus='offline')
        rows = list(infra.check_cluster(infra.item_name(cluster), {}, data))
        self.assertEqual(max(states(rows)), State.WARN)

    def test_missing_vm_power_never_reports_healthy_resource_metrics(self):
        vm = {'powerState': None, 'stats': {'cpuUsage': 0}}
        rows = list(checks.check_vm_metrics('CPU', {}, vm))
        self.assertEqual(states(rows), [State.WARN])
        self.assertFalse(any(row.args for row in rows))
        inventory = {'vms': [{'id': 1, 'name': 'ExampleVM', 'powerState': None}]}
        self.assertEqual(states(list(extended.check_vm_inventory(inventory))), [State.WARN])

    def test_known_vm_offline_respects_expected_power(self):
        vm = {'id': 1, 'name': 'ExampleVM', 'status': 'stopped', 'powerState': 'off'}
        self.assertEqual(max(states(list(checks.check_vm({}, vm)))), State.OK)
        self.assertEqual(max(states(list(checks.check_vm({'expected_power': 'on'}, vm)))), State.CRIT)

    def test_snapshot_partial_coverage_warns_without_partial_total_metric(self):
        section = {'snapshots_enabled': True, 'vms': [{'id': 1, 'snapshot_count': 2}, {'id': 2}]}
        rows = list(extended.check_inventory_snapshots(section))
        self.assertEqual(states(rows), [State.WARN])
        self.assertFalse(any(row.args for row in rows))
        section['vms'][0].pop('snapshot_count')
        self.assertEqual(states(list(extended.check_inventory_snapshots(section))), [State.UNKNOWN])

    def test_failed_volume_retains_critical_with_missing_capacity(self):
        rows = list(extended.check_volume('Disk', {'volumes': [{'id': 1, 'name': 'Disk', 'status': 'failed'}]}))
        self.assertEqual(max(states(rows)), State.CRIT)

    def test_optional_api_failure_and_invalid_measurements_remain_unknown(self):
        self.assertEqual(extended.failure({'success': False, 'error': 'HTTP 403'}).state, State.UNKNOWN)
        self.assertEqual(extended.failure('invalid').state, State.UNKNOWN)
        self.assertEqual(states(list(infra.usage(None, 'metric', 'CPU', {}))), [State.UNKNOWN])
        self.assertEqual(states(list(infra.age_results(None, {}))), [State.UNKNOWN])

    def test_failed_switch_remains_critical_when_uplinks_are_unavailable(self):
        rows = list(extended.check_switch('Switch', {'virtual_switches': [
            {'id': 1, 'name': 'Switch', 'status': 'failed', 'uplinks': {'success': False, 'error': 'HTTP 403'}}
        ]}))
        self.assertEqual(max(states(rows)), State.CRIT)

    def test_failed_multipath_state_survives_incomplete_counters(self):
        data = fixture()
        store = data['datastores'][0]
        store['multipath'] = {'multipathState': 'failed'}
        rows = list(infra.check_multipath(infra.item_name(store), {}, data))
        self.assertEqual(max(states(rows)), State.CRIT)

    def test_offline_datastore_does_not_publish_healthy_paths(self):
        data = fixture()
        store = next(value for value in data['datastores'] if value.get('multipath'))
        store['online'] = False
        rows = list(infra.check_multipath(infra.item_name(store), {}, data))
        self.assertEqual(max(states(rows)), State.CRIT)
        self.assertFalse(any(row.args for row in rows))

    def test_healthy_sensor_subset_and_all_unavailable_are_distinguished(self):
        data = fixture()
        host = data['hypervisors'][0]
        host['hardware_summary'] = {'count': 240, 'unavailable': 20, 'problems': []}
        self.assertEqual(max(states(list(infra.check_hardware(infra.item_name(host), {}, data)))), State.OK)
        host['hardware_summary']['unavailable'] = 240
        self.assertEqual(max(states(list(infra.check_hardware(infra.item_name(host), {}, data)))), State.WARN)

    def test_missing_status_cloud_and_vm_warn(self):
        rows = list(checks.status_result({'status': None}, {'provisioned'}))
        self.assertEqual(states(rows), [State.WARN])
        self.assertEqual(rows[0].summary, 'not reported')
        rows = list(checks.status_result({'success': False, 'status': None}, {'provisioned'}))
        self.assertEqual(states(rows), [State.CRIT])

    def test_uplink_maintenance_and_known_failure(self):
        section = extended_fixture()['extensions']
        uplink = section['virtual_switches'][0]['uplinks']['data'][0]
        item = list(extended.discover_uplinks(section))[0].item
        uplink['host'] = {'status': 'maintenance', 'powerState': 'off', 'serverGroupMemberStatus': 'offline'}
        self.assertEqual(max(states(list(extended.check_uplink(item, section)))), State.WARN)
        uplink['host']['serverGroupMemberStatus'] = 'fenced'
        self.assertEqual(max(states(list(extended.check_uplink(item, section)))), State.CRIT)

    def test_license_limit_becoming_unlimited_warns_without_a_ratio(self):
        section = {'license': {'success': True, 'data': {'limits': [
            {'code': 'sockets', 'used': 2, 'max': None}
        ]}}}
        rows = list(extended.check_license_limit('sockets', section))
        self.assertEqual(states(rows), [State.WARN])
        self.assertFalse(any(row.args for row in rows))

    def test_invalid_memory_capacity_never_emits_usage_metrics(self):
        data = fixture()
        host = data['hypervisors'][0]
        host['stats'].update(usedMemory=101, maxMemory=100)
        rows = list(infra.check_hypervisor_memory(infra.item_name(host), {}, data))
        self.assertIn(State.UNKNOWN, states(rows))
        self.assertFalse(any(row.args and 'memory' in row.args[0] for row in rows))

    def test_power_labels_and_paused_vm_are_consistent(self):
        for raw in ('Powered ON', 'powered-on', 'on'):
            inventory = {'vms': [{'id': 1, 'name': 'ExampleVM', 'powerState': raw}]}
            item = extended.vm_power_item(inventory['vms'][0])
            self.assertEqual(states(list(extended.check_vm_power(item, {'expected_power': 'on'}, inventory))), [State.OK])
        vm = {'id': 1, 'name': 'ExampleVM', 'status': 'paused', 'powerState': 'paused'}
        self.assertEqual(max(states(list(checks.check_vm({}, vm)))), State.OK)

    def test_collector_carries_maintenance_context_to_cluster_and_uplink(self):
        host = {'id': 5, 'name': 'Host1', 'zone': {'id': 1}, 'status': 'maintenance',
                'maintenanceMode': True, 'powerState': 'off', 'serverGroupMemberStatus': 'offline'}
        class API:
            def listing(self, endpoint, key, **filters):
                if endpoint == 'servers': return [host]
                if endpoint == 'clusters': return [
                    {'id': 2, 'name': 'Cluster1', 'zone': {'id': 1}, 'servers': [host]}
                ]
                return []

            def get(self, endpoint, **params):
                if endpoint == 'virtual-switches': return {'virtualSwitches': [{'id': 1, 'name': 'vs0'}]}
                if endpoint.endswith('/uplinks'): return {'uplinks': [{'id': 1, 'serverId': 5}]}
                return {}

        api = API()
        infrastructure = agent.collect_infrastructure(api, [{'id': 1}])
        self.assertTrue(infrastructure['clusters'][0]['members'][0]['maintenanceMode'])
        extension = agent.collect_extensions(api, [], infrastructure, {'virtual_switches': True})
        uplink = extension['virtual_switches'][0]['uplinks']['data'][0]
        self.assertTrue(uplink['host']['maintenanceMode'])


if __name__ == '__main__':
    unittest.main()
