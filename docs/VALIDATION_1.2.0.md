# Validation record — 1.2.0

Date: 2026-11-20 (revision of version 1.2.0). Build/test interpreter: Python 3.12.14. Package identity: `morpheus` version `1.2.0`, author Pawel Wladzinski <pawel.wladzinski@vayana.pl>, GPL-2.0-only.

## Regression tests

`python3 -m unittest discover -s tests -v` passes **170 tests**. Function tests use a small Checkmk result-object shim, not a monitoring core.

Coverage includes pagination/schema errors, optional permission failures, source inventory, per-metric cache/timestamp/capacity protections, hardware fallback, names/identities, graphs, power-loss/recovery and expected power. New cases cover maintenance before the API flag changes, completed versus incomplete maintenance, explicit faults during maintenance, missing datastore locations, null online status, invalid memory pairs, incomplete multipath counters, unknown operational status, partial snapshot coverage and license-limit transitions. Added regressions cover healthy local directory pools, all-missing locations, typed host identities, shared/unknown types, conflicting shared evidence, metadata whitelist/merge, and license allocation flags at/below/above the entitlement.

## Actual public plugin APIs

The public API validation script is executed in separate processes against unmodified official Checkmk source snapshots. It uses real `AgentSection`, `CheckPlugin`, `Result`, `State`, ruleset forms, server-side-call secrets/commands and graphing classes.

| Checkmk ref | Pinned official commit |
| --- | --- |
| `v2.4.0p26` | `4ba58f6610852472b1aa27bbfdd867f991b39728` |
| `v2.5.0p19` | `8efcf83a153b201ce640a6c1da9de9c52d9c3650` |

On both snapshots:

- 15 platform/VM sample services evaluated.
- 475 infrastructure sample services evaluated, including 35 without detailed sensors.
- 13 extended sample services evaluated.
- 13 ruleset forms constructed, with matching default-parameter keys.
- Password-store secret references and all optional collector arguments validated through `SpecialAgentConfig`.
- 59 metric definitions, 40 primary graphs and 13 Perf-O-Meters validated. Data age stays auxiliary; existing MiB-to-byte graph conversions are preserved.
- Maintenance/partial-location WARN and explicit-failure CRIT verified with the actual `State.worst` aggregation. The revised local-pool exception and license 8/8 OK versus 9/8 CRIT are also exercised with actual API Result objects.

Reference sources: [Checkmk 2.4](https://github.com/Checkmk/checkmk/tree/v2.4.0p26), [Checkmk 2.5](https://github.com/Checkmk/checkmk/tree/v2.5.0p19). These snapshots are validation dependencies, not bundled runtime dependencies.

## Package and publication validation

- Exact MKP manifests agree and describe minimum `2.4.0`, Until Version `2.5.0p99`, version `1.2.0` and the public maintainer/project URL.
- The official Checkmk MKP parser accepts the manifest; official extraction produces the ten expected installed files.
- Every installed file matches the corresponding `src/` bytes. Collector permissions are 0755; other installed files are 0644. License text is installed as `morpheus/COPYING`.
- Repeated standard-library builds produce the same MKP bytes. Gzip and tar metadata are deterministic.
- Source/archives are checked for bytecode, unsafe paths, private deployment identifiers, raw API dumps and unintended credentials.
- The repository ZIP includes `.gitignore`, `.gitattributes`, English source/docs/tests/tools, the exact MKP and its SHA-256 checksum.

Run `python3 tests/validate_package.py` after building, or pass `--mkp package/morpheus-1.2.0.mkp` to validate the included asset. `TEST_RESULTS.txt` records the test commands/results; `package/SHA256SUMS.txt` identifies the installable bytes.

## Validation boundary

There is no running Checkmk monitoring core, Agent Bakery or live Morpheus appliance in the build environment. Public API validation is performed with the interpreter stated above, not a full installed Checkmk 2.5 runtime. It does not claim every future 2.5 patch, edition/provider, rendered graph or live failure scenario has been exercised. Run `cmk-validate-plugins`, a fresh source collection, discovery and the acceptance cases in [UPGRADE_1.2.0.md](UPGRADE_1.2.0.md) on the exact installed package.

Checkmk treats Until Version as an **exclusive** boundary. The manifest intentionally contains exactly `2.5.0p99`; it permits versions below that value, not `2.5.0p99` itself. This follows the official `_raise_for_too_new_cmk_version` implementation in [Checkmk's MKP version checks](https://github.com/Checkmk/checkmk/blob/8efcf83a153b201ce640a6c1da9de9c52d9c3650/packages/cmk-mkp-tool/cmk/mkp_tool/_unsorted.py).
