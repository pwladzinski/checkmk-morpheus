# Install or upgrade to 1.2.0

This is a stable release of HPE Morpheus Monitoring, maintained by Pawel Wladzinski. The package name remains `morpheus`. Existing service, host, rule and metric identities are preserved from 1.1.x. No new endpoint or permission is required for the status-policy changes.

## Replace an earlier 1.2.0 archive

Revision `2026-11-20` intentionally keeps version `1.2.0`. Its bytes and SHA-256 differ from the earlier archive. Confirm that the new MKP has been copied to the site home, then run as the site user:

```bash
mkp inspect ~/morpheus-1.2.0.mkp &&
mkp disable morpheus 1.2.0 &&
mkp remove morpheus 1.2.0 &&
mkp add ~/morpheus-1.2.0.mkp &&
mkp enable morpheus 1.2.0 &&
cmk-validate-plugins &&
cmk -U &&
omd restart
```

This removes/replaces the registered extension package; it does not delete WATO hosts, rules or monitoring history. Keep the downloaded MKP outside the managed package store, such as the site home used above. The restart briefly interrupts the site. Repeat on the central and relevant remote sites. Morpheus API Details must show `build revision: 2026-11-20`.

## Version limits

Manifest values are minimum `2.4.0` and Until Version `2.5.0p99`. Until Version is exclusive in Checkmk: version `2.5.0p99` itself and later versions are outside this bound. The package was exercised with the public APIs from Checkmk `2.4.0p26` and `2.5.0p19`; see [validation](VALIDATION_1.2.0.md).

## Copy and enable

Put `morpheus-1.2.0.mkp` in the site user's home directory. When transferring from a restricted administrator home, copy as root rather than making that home world-readable. Replace both placeholders below with the real site name and administrative file location:

```bash
# Run as root; replace <site> and the source path.
install -o <site> -g <site> -m 0640 \
  /path/to/morpheus-1.2.0.mkp \
  /omd/sites/<site>/morpheus-1.2.0.mkp
su - <site>
```

As the site user in that fresh login shell:

```bash
mkp inspect ~/morpheus-1.2.0.mkp
mkp add ~/morpheus-1.2.0.mkp
mkp enable morpheus 1.2.0
mkp list
cmk-validate-plugins
cmk -U
omd restart
```

The restart briefly interrupts monitoring and the web interface. It reloads persistent core, GUI and helper processes; installing source files alone can leave older code running in memory. GUI installation through Extension packages is also supported.

## Distributed monitoring

Install the same MKP version on the central site providing rules/graphs and all remote sites executing Morpheus collection or checks. This MKP can be loaded by both 2.4 and 2.5 sites within its version bounds. It does not change Checkmk's own rules for mixed-version distributed deployments.

- With **Replicate extensions** disabled: install and enable on each relevant site manually, then activate configuration from the central site.
- With extension replication enabled: install centrally and use the established replication process; verify the resulting remote package state.

On every relevant site, `mkp list` must show **1.2.0 Enabled (active on this site)**. An enabled but inactive older version is not used. Verify that the effective HPE Morpheus rule still applies to the API source host and that the host uses configured API integrations.

## Verify collection

Use your own source-host name:

```bash
cmk -nv --no-cache <morpheus-source-host>
```

Confirm `[special_morpheus] Success`. If it reports that a datasource is required but none is configured, inspect the effective rule, host agent mode and package activation on the collecting site; this is not a Morpheus TLS or metric error.

Rescan the source and existing piggyback VM hosts, review discovery and activate changes. Upgrading from 1.1.x does not rename established services. A deployment from before 1.0.3 may still need the older naming migration described in the changelog.

## Expected results

| Scenario | Expected result |
| --- | --- |
| Host `maintenancing`, power on, member online, API maintenance flag false | Hypervisor State WARN, Maintenance True; valid resource metrics continue |
| Missing secondary host location on a healthy/online, positively identified local directory pool with one healthy location | Informational in Details; no automatic WARN |
| Missing location status on shared/unclassified storage, with an error message, or with no healthy baseline | WARN with `not reported` |
| License use 8/8, including allocation flags | OK; 9/8 is CRIT |
| Completed/flagged maintenance, host powered off/offline | WARN; no CPU/RAM/hardware metrics fabricated |
| Power loss during uncompleted/unflagged evacuation | CRIT |
| Member `unclean` or `fenced`, including in maintenance | CRIT |
| Known failed datastore/location/multipath | CRIT |
| Unknown operational enum | WARN |
| Invalid numeric measurement or unusable timestamp | UNKNOWN |
| VM expected ON but powered OFF | CRIT; known OFF is OK with default expected-any policy |
| Partial snapshot coverage | WARN and no misleading total metric |

JVM heap, datastore usage, license capacity, API failures and stale-sample limits remain independently monitored. Review existing custom parameter rules before comparing default thresholds. Do not clear caches to make old samples appear current.

## Rollback

Retain the previous MKP and its version before upgrading. Enable that version, run `cmk-validate-plugins`, regenerate configuration and restart the site. Use a package whose version limits permit the site's Checkmk version. For a 2.5 site, the older 1.1.0 archive with Until Version `2.5.0` is not a suitable rollback; use the retained 1.1.1 compatibility package if available.
