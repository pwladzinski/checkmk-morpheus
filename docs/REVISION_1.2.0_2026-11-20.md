# Version 1.2.0 — revision 2026-11-20

The requested revision keeps the package version at **1.2.0**. Source, MKP and checksums replace the earlier supplied 1.2.0 assets together. The original archive is identified by MKP SHA-256 `f8b89c69acc5fa5ec0df7636d9500d4f8592c57add156cb84f07b57e31a283a9`; use the new `package/SHA256SUMS.txt` for this revision.

## License capacity

Valid numeric use at or below the finite entitlement is OK. Use above it is CRIT. Thus 8/8 is OK and 9/8 is CRIT. `warning`/`limitReached` allocation flags remain visible in Details; they do not override the validated used/max ratio. License expiry and appliance alarms continue to be monitored separately. Zero entitlement is enforced without division by zero; invalid measurements remain UNKNOWN.

## Datastore locations

The collector now retains the API's `type`, `externalType` and selected `datastoreType` fields, including when cloud/cluster listings differ in completeness. It does not infer storage type from a datastore name.

A recognized local directory pool can have a healthy location while secondary host-location records omit their status. These omissions are informational only when the main datastore is healthy and online, at least one location is healthy, the omitted status belongs to a typed host reference and there is no accompanying error message. All-missing location health remains WARN.

Shared/unclassified datastores still warn about missing location status. Explicit location warnings/failures remain WARN/CRIT, including on local pools. Shared evidence such as NFS/GFS2 or actual multipath paths takes precedence over directory labels; null/zero multipath placeholders do not imply shared storage. Typed host references display matching names and IDs; other references keep their original identity.

Morpheus API Details identify the installed collector as `build revision: 2026-11-20`. Established service/host/metric/rule names and resource utilization/freshness thresholds are preserved.

## Installation and publication

For an earlier installed 1.2.0, use the disable/remove/add/enable sequence in [UPGRADE_1.2.0.md](UPGRADE_1.2.0.md); an ordinary `mkp add` refuses an already registered version. Repeat on the central and relevant remote sites. Use the updated release notes and Exchange description included in this bundle.
