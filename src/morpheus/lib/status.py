# SPDX-License-Identifier: GPL-2.0-only
# Copyright (c) 2026 Pawel Wladzinski <pawel.wladzinski@vayana.pl>
"""Operational states reported by Morpheus, shared by the check plug-ins."""
from cmk.agent_based.v2 import State


OK_STATUSES = frozenset({
    'ok', 'healthy', 'online', 'provisioned', 'available', 'running', 'green',
    'active', 'ready', 'normal', 'in-sync', 'synced', 'connected', 'completed',
    'success', 'mounted',
})
MAINTENANCE_STATUSES = frozenset({
    'maintenance', 'maintenancing', 'entering-maintenance', 'exiting-maintenance',
    'evacuating', 'draining',
})
CRITICAL_STATUSES = frozenset({
    'error', 'failed', 'failure', 'offline', 'critical', 'red', 'cr', 'nr',
    'down', 'fatal', 'unclean', 'fenced', 'unreachable', 'lost', 'dead',
})
POWER_STATES = {
    'on': 'on', 'off': 'off', 'paused': 'paused', 'suspended': 'suspended',
    'poweredon': 'on', 'poweredoff': 'off',
    'powered-on': 'on', 'powered-off': 'off',
}


def status_key(value):
    return str(value or '').strip().lower().replace('_', '-').replace(' ', '-')


def status_text(value):
    text = str(value).strip() if value is not None else ''
    return text or 'not reported'


def operational_state(value, good=()):
    status = status_key(value)
    if status in CRITICAL_STATUSES:
        return State.CRIT
    if status in OK_STATUSES or status in good:
        return State.OK
    # A new or missing operational status warrants investigation. UNKNOWN is
    # reserved for checks whose measurements or API datasets cannot be evaluated.
    return State.WARN


def power_state(value):
    return POWER_STATES.get(status_key(value))


def in_maintenance(host):
    return host.get('maintenanceMode') is True or status_key(host.get('status')) in MAINTENANCE_STATUSES


def planned_offline(host):
    return host.get('maintenanceMode') is True or status_key(host.get('status')) == 'maintenance'


def membership_state(host):
    member = host.get('serverGroupMemberStatus')
    if status_key(member) == 'offline' and planned_offline(host):
        return State.WARN
    return operational_state(member)


def host_status_state(host):
    if status_key(host.get('status')) == 'offline' and planned_offline(host):
        return State.WARN
    return operational_state(host.get('status'))


def host_blocked(host):
    """Gate resource checks on availability without reporting healthy zeros."""
    membership = status_key(host.get('serverGroupMemberStatus'))
    maintenance = planned_offline(host)
    if membership in CRITICAL_STATUSES and membership_state(host) == State.CRIT:
        return State.CRIT, 'Membership: ' + status_text(host.get('serverGroupMemberStatus'))
    if host_status_state(host) == State.CRIT:
        return State.CRIT, 'Status: ' + status_text(host.get('status'))
    if membership in CRITICAL_STATUSES:
        return State.WARN, 'Membership: ' + status_text(host.get('serverGroupMemberStatus')) + '; maintenance active'
    if status_key(host.get('status')) == 'offline':
        return State.WARN, 'Status: offline; maintenance active'
    power = power_state(host.get('powerState'))
    if power == 'off':
        return (State.WARN if maintenance else State.CRIT), 'Power: off' + ('; maintenance active' if maintenance else '')
    if power != 'on':
        return State.WARN, 'Power not confirmed on: ' + status_text(host.get('powerState'))
    if membership and membership not in OK_STATUSES and membership not in MAINTENANCE_STATUSES:
        return State.WARN, 'Membership not confirmed healthy: ' + status_text(host.get('serverGroupMemberStatus'))
    return None
