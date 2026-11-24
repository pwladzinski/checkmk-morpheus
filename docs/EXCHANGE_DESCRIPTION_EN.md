# HPE Morpheus Monitoring

Read-only HPE Morpheus REST API monitoring for Checkmk 2.4 and 2.5, maintained by Pawel Wladzinski.

## Features

- Appliance health/version, CPU, JVM heap, database connections, storage, threads, Elasticsearch and RabbitMQ.
- Cloud synchronization; datastores with capacity, location state and datastore-level multipath counters.
- Hypervisor CPU/RAM, power, maintenance and membership; cluster state, inventory member counts, reported HA configuration and worker metrics.
- Hardware summaries and optional individual sensors.
- VM state, power, guest-agent status, CPU/RAM, API storage and conditional disk IOPS through piggyback.
- VM power overview with named VM lists and individual source-host power checks with optional expected-ON/OFF rules.
- Optional snapshots and scoped snapshot overview, API volumes, health alarms, license expiration/capacity and virtual-switch/uplink configuration.
- Readable metric units, primary utilization/capacity graphs and Perf-O-Meters.

## Status policy in 1.2.0

Maintenance, `maintenancing` and incomplete operational states produce WARN. Missing secondary host-location statuses on a positively identified healthy/online local directory pool with a healthy baseline are informational; shared or unclassified storage retains WARN for missing status. Host names are shown where typed references can be resolved. License use at its entitlement, such as 8/8, is valid and OK; exceeding the finite limit is CRIT. Explicit failures, unclean/fenced membership and unplanned host outages remain CRIT. Completed/flagged maintenance can identify a planned offline host without publishing healthy zero resource readings. Invalid measurements and unavailable API datasets remain UNKNOWN. Existing utilization/freshness thresholds and sample timestamps are preserved. Version 1.2.0 revision 2026-11-20 includes these location/license refinements.

## Compatibility and configuration

Manifest minimum: **2.4.0**. Until Version: **2.5.0p99**, an exclusive upper boundary in Checkmk. Actual public plugin APIs from **2.4.0p26** and **2.5.0p19** were exercised. The Morpheus deployment evidence is API **9.1.0.1 with HVM**; provider field availability varies.

Install and enable the MKP on relevant central/remote sites. Store a read-access token in Checkmk's Password store, configure the **HPE Morpheus** special-agent rule for an API source host, discover services and activate changes. VM hosts consume piggyback data and may be created manually or through a separately configured Dynamic host management connection.

Connection fields have no customer defaults. TLS verification is enabled by default. Optional collections must be explicitly enabled and can require additional read access.

## Interpretation

API storage and volumes are not guest filesystem fullness checks; use a guest OS agent for C:, D: or mount points. VM CPU preserves the provider scale, which can exceed 100%. Independent metric caches retain original timestamps and cannot recover samples the API never returns. Cluster member counts do not prove quorum, datastore multipath does not verify every host path, and virtual-switch sync does not prove physical NIC/LACP health. Alarm/license summaries are appliance/account-wide.

The release includes 170 local regression tests, two-version public API checks, exact package validation and upgrade/status documentation. Live collection/core/GUI acceptance remains a target-site check.

**Maintainer:** Pawel Wladzinski <pawel.wladzinski@vayana.pl>  
**License:** GPL-2.0-only  
**Source, documentation and issues:** https://github.com/pwladzinski/checkmk-morpheus

Independent community integration; not an official HPE or Checkmk product.
