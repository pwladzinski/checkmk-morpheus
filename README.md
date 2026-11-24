# HPE Morpheus Monitoring for Checkmk

Read-only HPE Morpheus REST API monitoring, with infrastructure services on an API source host and VM services delivered through Checkmk piggyback.

**Version:** 1.2.0 (revision 2026-11-20)  
**Maintainer:** Pawel Wladzinski <pawel.wladzinski@vayana.pl>  
**License:** GPL-2.0-only  
**Source and issues:** https://github.com/pwladzinski/checkmk-morpheus

## Compatibility

| Component | Supported scope and validation |
| --- | --- |
| Checkmk | 2.4 and 2.5; manifest minimum `2.4.0`, Until Version `2.5.0p99` |
| Version boundary | Checkmk treats Until Version as exclusive: `2.4.0 <= version < 2.5.0p99` |
| Public plugin APIs exercised | Official Checkmk `2.4.0p26` and `2.5.0p19` source snapshots |
| Morpheus | API 9.1; deployment evidence from 9.1.0.1 with HVM |
| Other providers | Field availability and units depend on the provider; VMware inventory has sample-data coverage |

Release 1.2.0 provides consistent operational states: maintenance and incomplete operational status fields produce WARN; optional secondary statuses on a confirmed healthy local directory pool are informational. Explicit failures remain CRIT. License use at the exact entitlement is OK. Invalid measurements and unavailable API datasets remain UNKNOWN. See [status policy](docs/STATUS_POLICY.md), [validation](docs/VALIDATION_1.2.0.md) and the [upgrade guide](docs/UPGRADE_1.2.0.md).

This is an independent community integration maintained by the author. It is not an official HPE or Checkmk product.

## Services

- Appliance application health/version, CPU, JVM heap, database connections, threads, storage, Elasticsearch and RabbitMQ health.
- Cloud state and synchronization age.
- Datastore state, locations, used/free/total capacity and datastore-level multipath counters when present.
- Hypervisor power, provisioning/maintenance state, membership, CPU, RAM and hardware health; optional individual sensors.
- Cluster state, synchronization, online/total inventory members, reported HA configuration and worker CPU/RAM.
- VM power overview with VM names in Details and one power service per VM on the source host.
- VM state, expected power, guest-agent status, CPU, RAM, API storage and conditional read/write disk IOPS through piggyback.
- Optional snapshot count/age/size, scoped snapshot overview, API volumes, health alarms, license expiration/capacity and virtual-switch/uplink configuration.
- Named metrics, units, primary utilization/capacity graphs and Perf-O-Meters; data age stays auxiliary.

Infrastructure service names use object names. Duplicate names are qualified by cloud and IDs as necessary; IDs also remain in service details. Release 1.2.0 preserves existing service, host, metric and rule names. Upgrading from before 1.0.3 requires rediscovery because that older release changed infrastructure naming.

## Requirements and API scope

The collecting Checkmk site must reach Morpheus over HTTPS. Use a dedicated API token with read access to the selected objects. Exact role permissions and visible objects depend on the Morpheus account, tenant and provider. The collector performs GET requests only.

| Endpoint | Use |
| --- | --- |
| `/api/health` | Appliance components and application health |
| `/api/zones` | Clouds and synchronization |
| `/api/servers?vm=true` | Paginated VM inventory and statistics |
| `/api/servers?vmHypervisor=true` | Paginated hypervisor inventory and statistics |
| `/api/servers/{id}` | Bounded fallback for missing VM metrics or hardware readings |
| `/api/clusters` | Clusters and members |
| `/api/zones/{id}/data-stores` | Cloud datastores |
| `/api/clusters/{id}/datastores` | Cluster datastores and multipath |
| `/api/servers/{id}/snapshots` | Optional snapshots |
| `/api/health/alarms` | Optional appliance/account-wide alarms |
| `/api/license` | Optional appliance/account-wide license information |
| `/api/virtual-switches?clusterId={id}` | Optional virtual-switch inventory |
| `/api/virtual-switches/{id}/uplinks` | Optional per-host uplink configuration |

Volumes are selected from the server inventory. No guest filesystem endpoint is inferred. See [API coverage](docs/API_COVERAGE.md) for remaining gaps.

## Install or upgrade

Download `morpheus-1.2.0.mkp` from the release assets or Checkmk Exchange. Put it in the Checkmk site user's home, then run as that site user in a fresh login shell:

```bash
mkp inspect ~/morpheus-1.2.0.mkp
mkp add ~/morpheus-1.2.0.mkp
mkp enable morpheus 1.2.0
mkp list
cmk-validate-plugins
cmk -U
omd restart
```

The restart briefly interrupts monitoring and the web interface and reloads persistent processes. Alternatively, upload and enable the MKP through **Setup > Maintenance > Extension packages**, then activate changes and reload the site processes as needed.

For distributed monitoring, install the same package version on the central site that provides configuration/graphs and the remote sites that collect or check Morpheus data. If **Replicate extensions** is disabled, install it on each relevant site manually. A central 2.4 site and remote 2.5 site can load this same MKP; Checkmk's own distributed-version compatibility rules still apply.

Follow [UPGRADE_1.2.0.md](docs/UPGRADE_1.2.0.md) for verification and rollback, including replacement of an earlier 1.2.0 archive. The collector reports build revision `2026-11-20` in Morpheus API Details.

## Configure the API source host

1. Store the Morpheus API token in Checkmk's Password store.
2. Create a logical host, for example `morpheus-api`.
3. Set **Checkmk agent / API integrations** to **Configured API integrations, no Checkmk agent**; disable SNMP. Select an address and host check appropriate to the network.
4. Search Setup for **HPE Morpheus**, create a rule and restrict it to this source host.
5. Enter the appliance base URL, for example `https://morpheus.example.com` without `/api`, and select the stored token.
6. Leave TLS verification enabled and trust the appropriate CA. The explicit verification-disable option is available for untrusted certificates.
7. Optionally restrict infrastructure and VMs to a cloud ID. Without the filter, collection includes all API-visible clouds.
8. Initially leave individual hardware sensors disabled; enabling them can create hundreds of services.
9. Enable any optional collections required, discover services, accept them and activate changes.

Connection fields have no customer-specific defaults. The MKP contains no installation URL, token, site name, host prefix or Dynamic host management connection.

## Configure VM hosts

The default piggyback identity is `morpheus-vm-<server-id>`. The integration rule can instead use the VM name or guest hostname with an optional prefix. Names must be unique and match the Checkmk destination hosts exactly.

For hosts monitored only through this integration:

- **Checkmk agent / API integrations:** No API integrations, no Checkmk agent.
- **SNMP:** No SNMP.
- **IP address family:** No IP.
- **Piggyback:** Always use and expect piggyback data.

Create the hosts manually or use Dynamic host management in a suitable edition. Restrict the piggyback connector to the API source host and intended VM name pattern. Enable **Discover services during creation**. Existing hosts need a separate service rescan when new checks become available.

For a host that also uses an OS agent, retain that agent configuration and arrange intentional piggyback name matching. DCD configuration is separate from the MKP.

## Operational states and thresholds

| Condition | Result |
| --- | --- |
| Known healthy state | OK |
| `maintenancing`, `maintenance`, other lifecycle operations | WARN |
| Empty, missing or unrecognized operational status | WARN; qualified local-directory location exception below |
| Known local directory pool, healthy/online overall and at least one healthy location | Missing secondary host statuses are informational; reported faults still apply |
| Explicit failure, failed/offline storage, unclean/fenced/unreachable member | CRIT |
| Completed or explicitly flagged maintenance with a powered-off/offline host | WARN; resource readings suppressed |
| Power lost during `maintenancing` before completed/flagged maintenance | CRIT |
| Missing/invalid metric, capacity, timestamp or unavailable API dataset | UNKNOWN; invalid readings are not fabricated |

`syncing` on a cluster remains OK during normal inventory refresh; synchronization age and member failures are checked independently. Maintenance does not suppress fencing, unclean membership or other explicit faults. See [STATUS_POLICY.md](docs/STATUS_POLICY.md) for the full matrix.

| Rule | Default WARN / CRIT |
| --- | --- |
| General CPU/RAM/JVM/platform utilization | 90% / 95% |
| Datastore utilization | 80% / 90% |
| Normal VM/source metric age | 900 s / 1800 s |
| Cached VM sample age | 120 s / 900 s |
| Hardware sample age | 120 s / 900 s |
| Oldest VM snapshot | 7 days / 30 days |
| License expiration | 30 days / 7 days remaining |

Existing custom rules remain effective. Cached VM groups use the stricter of normal and cache age limits. Multipath expects at least two active paths by default. HA is informational unless explicitly required. Finite-license use within or equal to the entitlement is OK; usage above the limit is CRIT. API allocation flags do not override the valid numeric ratio. Resource utilization and freshness thresholds are unchanged.

## Data interpretation

**VM statistics:** CPU, RAM, storage and disk I/O are retained independently with their original timestamp and source. Missing values never become zeros. A bounded detail lookup can supply valid groups, while each usage/capacity pair stays from one response. Untimestamped root-level aggregates are not used. No valid initial sample means UNKNOWN; critical age suppresses old usage metrics. Capacity changes prevent reuse, and observed power-off clears cached samples. Cache reuse cannot recover measurements never returned by the API.

**CPU and RAM:** CPU preserves the provider's `cpuUsage` scale, including values above 100%; it is not divided by vCPU count. Set thresholds to that scale. RAM uses valid used/max pairs; zero used RAM without a connected/reported guest-agent heartbeat remains unverified.

**Storage and volumes:** API storage is backing/allocation information, not C:, D: or mount-point fullness. Individual API volumes have no independent measurement timestamp in the observed payload. Use an OS agent for guest filesystem alerts. Directory datastores may share one filesystem and show identical capacity; do not sum them as separate pools. Storage classification uses API type fields, never datastore names. Missing secondary host-location statuses are informational only for a confirmed healthy/online local directory pool with at least one healthy location and no location error message. Shared/unclassified storage and completely missing location health remain WARN. Host names are resolved from typed references where available.

**Power and snapshots:** The source overview lists VMs by power state in Details. Individual power services accept any known state by default; use **Morpheus VM expected power state** to require ON/OFF for selected VMs. Snapshot totals follow the cloud filter and account visibility. Partial coverage is WARN, no coverage is UNKNOWN, and either condition suppresses the total metric. A successful empty snapshot list is a valid zero baseline.

**Hypervisors and hardware:** Unavailable hosts do not publish healthy zero CPU/RAM or old sensor readings as current health. Hardware uses its own original timestamp when sensors are cached. A subset of unavailable sensors is counted separately; all sensor readings unavailable is WARN.

**Cluster, multipath and network:** Online/total members are inventory counts, not quorum or a failover test. Multipath counters are datastore-level and do not verify each host's paths. Virtual-switch/uplink checks validate configuration sync, not physical carrier, LACP health, speed, packet errors or drops. Old configuration sync dates are not periodic measurement ages.

**Alarms and licenses:** Appliance summaries are account/appliance-wide, even with a cloud filter. VM alarms are matched by stable server ID. Unknown alarm severity is WARN; explicit critical severity remains CRIT. Unlimited license limits are not discovered as finite capacity checks.

## Collection and security

Only GET requests are used. Redirects are blocked; response size, pagination, detail fallbacks and overall runtime are bounded. Snapshot collection makes one additional request per VM, limited to 100 VMs per run. VM detail fallback is limited to ten VMs per run and the remaining time budget. Requested but incomplete collections are reported explicitly; a failed source collection never emits old inventory as current.

Persistent metric/hardware caches are scoped by site, appliance URL and token identity under `$OMD_ROOT/var/check_mk/morpheus_vm_stats/` and `morpheus_hardware/`. Identity directories use mode 0700; files use 0600. Without `OMD_ROOT`, persistent caches are disabled. Removed-object cache files are not garbage-collected automatically and never create active inventory.

The token uses Checkmk's Password store and special-agent argument mechanism. CLI diagnostics can expose arguments. Optional `setproctitle` reduces process-title exposure after startup. Token refresh is not implemented. See [SECURITY.md](SECURITY.md).

## Build and validation

The builder uses Python's standard library and produces a reproducible MKP:

```bash
python3 -m unittest discover -s tests -v
python3 build.py --download-url https://github.com/pwladzinski/checkmk-morpheus
```

Output: `dist/morpheus-1.2.0.mkp`. On a Checkmk 2.4/2.5 site with its public APIs installed:

```bash
python3 tests/validate_public_api.py
```

Function-level tests use small result-object shims; the second script uses real public API classes. [VALIDATION_1.2.0.md](docs/VALIDATION_1.2.0.md) records exact snapshots and results. Live collection, the monitoring core and GUI rendering require target-site verification.

## Support and publication

Report issues with package, Checkmk and Morpheus versions, provider, affected service and sanitized output. See [CONTRIBUTING.md](CONTRIBUTING.md), [troubleshooting](docs/TROUBLESHOOTING_API_STATS.md) and [publishing instructions](docs/PUBLISHING.md).

The source and publication materials are English and contain no customer configuration. The installed MKP includes `morpheus/COPYING`; see [LICENSE](LICENSE) and [COPYRIGHT](COPYRIGHT). Earlier archives through 1.0.3 carried MIT notices; this GPL-2.0-only release does not revoke permissions already granted for those archives.
