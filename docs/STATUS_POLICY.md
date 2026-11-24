# Operational state policy — 1.2.0, revised 2026-11-20

Operational status strings and numeric measurements have different failure modes. A provider adding an enum or omitting a location status warrants WARN. An invalid capacity or timestamp prevents evaluation and remains UNKNOWN. Known faults remain CRIT.

The common mapping is implemented in `src/morpheus/lib/status.py`. It is shared by all three check modules. Status comparisons ignore case, surrounding whitespace and underscore/space differences. Original operational values remain visible in summaries or Details.

## State matrix

| API evidence | Check result |
| --- | --- |
| `ok`, `healthy`, `online`, `provisioned`, `available`, `running`, `green`, `active`, `ready`, `normal`, `in-sync`, `synced`, `connected`, `completed`, `success`, `mounted` | OK |
| `maintenancing`, `maintenance`, entering/exiting maintenance, evacuating, draining | WARN |
| Provisioning, migrating, pending, stopping, drifted and other incomplete operations | WARN |
| `warning`, degraded, any new/unrecognized operational enum | WARN |
| Missing, null or empty operational status | WARN, displayed as `not reported` |
| `failed`, `failure`, `error`, `offline`, `critical`, `red`, `down`, `fatal`, `dead` | CRIT, subject to the explicit maintenance exception below |
| Membership `unclean`, `fenced`, `unreachable`, `lost` | CRIT, including during maintenance |
| IPMI-style `cr` / `nr` sensor state | CRIT |
| No valid metric/capacity pair, non-finite/out-of-range numeric measurement, missing/invalid/future timestamp | UNKNOWN; invalid utilization is not emitted |
| Failed/unavailable API dataset | Collection service reports failure; the affected optional dataset check remains UNKNOWN |

These are monitoring states. UNKNOWN does not mean a failure is more severe than CRIT; it means the check cannot evaluate its input.

## Maintenance and host availability

Morpheus can report `status=maintenancing` while `maintenanceMode=false`. This is still maintenance in progress: Hypervisor State becomes WARN and shows `Maintenance: True`. The original `maintenanceMode` value remains in Details.

A host is considered explicitly planned offline only when `maintenanceMode` is exactly true or its status is `maintenance` (completed). A powered-off/offline host then produces WARN and resource readings are suppressed. `maintenancing` alone does not authorize a power-off: power loss before completed/flagged maintenance remains CRIT.

Explicit faults such as `failed`, `unclean`, `fenced`, `unreachable` and `lost` remain CRIT even with maintenance active. The maintenance context is passed to cluster-member and uplink checks. No Checkmk downtime is created automatically.

Unknown/unconfirmed host power or membership produces WARN; CPU, RAM, hardware and uplink evaluation is gated when availability cannot be confirmed. On recovery, valid current readings resume. A healthy powered-on host can continue to emit real resource metrics while evacuation is in progress.

## Datastores and locations

- `online=true` is OK; `online=false` is CRIT; null/missing online status is WARN.
- Missing location status normally produces WARN. On a recognized local directory pool, it is informational only when overall status is healthy, `online=true`, at least one location is healthy, and the missing entry is a host reference without an error message. An entirely unreported set of locations remains WARN.
- Locality comes from API `type` / `datastoreType` fields, not the name `local`, `morpheus-images` or any customer label. Shared evidence such as NFS/GFS2/external type or multipath takes precedence. Unknown types retain WARN for missing statuses.
- Typed `ComputeServer` references use matching hypervisor names in output, retaining object IDs. Other/unknown reference types retain their identity rather than guessing a host. Informational local gaps appear in Details without flooding the summary.
- A reported failed/offline location remains CRIT. Its failure is not downgraded because another location has no status.
- Missing operational metadata does not fabricate a usage measurement. Invalid total/free space still produces UNKNOWN in the separate Usage service.
- Multipath remains datastore-level. An explicitly offline datastore suppresses path metrics and reports CRIT. Zero active paths is CRIT; partial/failed paths or fewer than the configured minimum is WARN. Explicit failed multipath state remains CRIT even with incomplete counters.

## Context-specific rules

| Context | Policy |
| --- | --- |
| Cluster `syncing` | OK while normal refresh proceeds; age and member failures are still checked |
| Cluster members absent/partially described | WARN; online counts are inventory, not quorum |
| VM lifecycle `stopped`, `off`, `on`, `paused`, `suspended` | Accepted with a known power state |
| VM powered OFF | OK by default; CRIT if an expected-ON rule applies |
| VM power missing/unrecognized | WARN; no healthy resource metrics emitted |
| Snapshot overview partially collected | WARN, no partial total metric |
| Snapshot overview with no coverage | UNKNOWN, no total metric |
| Successful empty snapshot list | OK with count zero |
| Open alarm with unknown severity | WARN; explicit critical severity is CRIT |
| Finite license within or exactly at its entitlement | OK; usage above the limit is CRIT |
| Previously discovered license limit absent or now null/unlimited | WARN with a discovery review message |
| Some hardware sensors `ns` | Counted as unavailable, separate from failed sensors |
| All hardware sensor readings unavailable | WARN |
| Inventory object/sensor absent from a returned section | WARN; source collection errors remain independently visible |

Normal and cached data age limits remain unchanged. A fresh API request does not make an older CPU, RAM or hardware sample fresh. Unknown measurements are not replaced by zeros or new timestamps.

## Existing threshold alarms

This release does not raise limits or average away utilization spikes. JVM heap 92% still exceeds the default 90% warning level; datastore usage 86% still exceeds 80%; a 2/2 finite license is fully allocated but valid and therefore OK. API `warning` and `limitReached` allocation flags are retained in Details and do not override the valid used/max comparison. License expiration and native appliance alarms remain separate checks. Morpheus's own component status can independently raise WARN/CRIT even when a local numeric threshold is not exceeded.

## References

- [HPE Morpheus 9.1 host maintenance](https://docs.morpheusdata.com/en/9.1/infrastructure/clusters/hvm/host_maintenance.html)
- [HPE Morpheus 9.1 HVM storage operations](https://docs.morpheusdata.com/en/9.1/infrastructure/clusters/hvm/storage_operations.html)
- [Checkmk plugin state aggregation](https://docs.checkmk.com/latest/en/devel_check_plugins.html)
