# Publish HPE Morpheus Monitoring 1.2.0

Repository: https://github.com/pwladzinski/checkmk-morpheus  
Existing Exchange listing: https://exchange.checkmk.com/p/morpheus

Keep the package identity `morpheus`, version `1.2.0`, maintainer attribution and GPL-2.0-only license. This bundle is the requested 2026-11-20 revision of the earlier 1.2.0 archive; use its updated source, MKP and checksums together. Source, examples, configuration labels and release text are English and contain no customer defaults.

## 1. Update GitHub through the website

1. Extract `Morpheus_Checkmk_2.4-2.5_MKP_1.2.0.zip` on your computer. The archive contains repository-root files directly.
2. Open the repository's **Code** tab on `main`, then **Add file > Upload files**.
3. Drag the extracted contents into the upload area: `src`, `tests`, `tools`, `docs`, `package` and the root files. Upload their contents at repository root; do not upload the ZIP as the source tree or add a versioned wrapper directory.
4. Include `.gitignore` and `.gitattributes`. On macOS, press **Command + Shift + .** in Finder to display dotfiles. If the browser skips them, use **Add file > Create new file** with the exact filename and paste the supplied file content.
5. Review replacement files. Use commit message `Release 1.2.0: maintenance states and Checkmk 2.5 compatibility`.
6. Commit to `main`, or use a branch and review/merge it first. Confirm `README.md`, `src/morpheus/lib/status.py`, `docs/UPGRADE_1.2.0.md` and `package/morpheus-1.2.0.mkp` are visible at the expected paths.

GitHub uploads replace matching files but do not remove old files automatically. Older versioned folders or ZIPs are not needed for the current source layout; remove those separately only when you intend to. Preserve project history through commits and release tags.

The supplied `.gitignore` explicitly permits `package/*.mkp`; build output under `dist/` remains ignored. The release ZIP contains the exact installable MKP in `package/`.

## 2. Verify the exact package on a site

Use [UPGRADE_1.2.0.md](UPGRADE_1.2.0.md). Install matching code centrally and on relevant collecting/checking sites, including mixed 2.4/2.5 sites where supported by Checkmk. Run `cmk-validate-plugins`, collect without cache, verify maintenance/failure states, discover services and inspect graphs.

The supplied [validation record](VALIDATION_1.2.0.md) covers local regressions and actual public APIs. It does not claim a live monitoring-core run.

To rebuild and check the source package locally:

```bash
python3 -m unittest discover -s tests -v
python3 build.py --download-url https://github.com/pwladzinski/checkmk-morpheus
python3 tests/validate_package.py
```

## 3. Create the GitHub release

1. Open **Releases > Draft a new release**.
2. Choose a new tag `v1.2.0`, targeting the reviewed `main` commit.
3. Title: `HPE Morpheus Monitoring 1.2.0`.
4. Paste [RELEASE_NOTES_1.2.0_EN.md](RELEASE_NOTES_1.2.0_EN.md).
5. Attach `morpheus-1.2.0.mkp` and `SHA256SUMS.txt` from the extracted `package/` directory. GitHub also provides source archives from the tag automatically.
6. Use the normal release label, not pre-release. Review the selected tag, assets and preview, then publish.

Check the attachment against the checksum before publication. For this requested same-version revision, replace the earlier 1.2.0 draft assets together and verify the updated checksum. The installed collector identifies this revision as 2026-11-20; follow the upgrade guide for same-version reinstallation.

## 4. Add the Exchange version

Sign in with the account that owns the existing `morpheus` listing. Open its management/edit page and use **Add Version** (or the current new-version action). Keep the same listing rather than creating a second package.

- Upload **`morpheus-1.2.0.mkp`**, not the source ZIP.
- Confirm version **1.2.0**, title **HPE Morpheus Monitoring**, and author **Pawel Wladzinski <pawel.wladzinski@vayana.pl>**.
- Confirm minimum **2.4.0**, Until Version **2.5.0p99**, and project URL.
- Use [RELEASE_NOTES_1.2.0_EN.md](RELEASE_NOTES_1.2.0_EN.md) for version notes and [EXCHANGE_DESCRIPTION_EN.md](EXCHANGE_DESCRIPTION_EN.md) for the general listing description.
- Retain the existing project icon, review the form and submit.

Exchange may moderate the new version. An under-review submission is not yet approved. The package/source files have been prepared; no upload or publication is performed automatically.

References: [GitHub release management](https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository), [Checkmk Exchange upload guide](https://exchange.checkmk.com/how-to-upload).
