# HPE Morpheus Monitoring 1.2.0

Stable maintenance and status-policy release for Checkmk 2.4 and 2.5, targeting the Morpheus 9.1 API. Revised on 2026-11-20 within version 1.2.0.

- Recognize `maintenancing` and maintenance transitions as WARN, including before the API maintenance flag changes.
- Use API datastore types to distinguish local directory pools from shared/unclassified storage. Missing secondary local host statuses are informational only with healthy/online overall state and at least one healthy location; missing shared statuses remain WARN. Display matching host names where references permit. Explicit faults remain CRIT.
- Treat license use within or equal to the entitlement as OK, including 8/8 with allocation flags. Only numeric use above a finite limit is CRIT. Expiration and native alarms remain independently monitored.
- Carry maintenance context into cluster and uplink checks. Completed/flagged maintenance can report a planned powered-off/offline host as WARN; unclean/fenced/unreachable/lost membership and explicit faults stay CRIT.
- Warn for partial snapshot coverage, unknown alarm severity and inventory changes. Preserve UNKNOWN for measurements or API datasets that cannot be evaluated.
- Validate memory pairs and multipath counters before publishing usage metrics. Keep explicit failed multipath state visible when counters are incomplete.
- Preserve service/host/metric/rule identities, graph priority, original sample timestamps and existing resource utilization/freshness thresholds. No new endpoint or permission requirement.
- Produce reproducible MKP archives and include English status, upgrade and validation guides.

Package metadata: minimum Checkmk `2.4.0`, Until Version `2.5.0p99`. Checkmk treats Until Version as exclusive. Validation includes 170 regression tests, actual public plugin APIs from `2.4.0p26` and `2.5.0p19`, and exact package/source checks. A live monitoring core and appliance are not present in the build environment; verify the exact MKP on the target site before wider rollout.

An earlier 1.2.0 package must be disabled and removed before importing the revised archive under the same version. Verify build revision `2026-11-20` in Morpheus API Details.

For distributed monitoring, install matching code on the central site and relevant remote sites. Follow [the upgrade guide](https://github.com/pwladzinski/checkmk-morpheus/blob/v1.2.0/docs/UPGRADE_1.2.0.md) and [status policy](https://github.com/pwladzinski/checkmk-morpheus/blob/v1.2.0/docs/STATUS_POLICY.md).

Maintainer: Pawel Wladzinski <pawel.wladzinski@vayana.pl>. License: GPL-2.0-only.
