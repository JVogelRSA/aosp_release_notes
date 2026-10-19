# SolOS release notes

Customer-facing release notes that Software Updater shows when someone taps **Release Notes**.
The app reads them straight from this public repo, so anything merged to `main` is visible on
devices within a few minutes. GitHub's raw CDN caches files for about 5 minutes.

## Where the app looks

```
https://raw.githubusercontent.com/makedaylight/aosp_release_notes/main/v1/<device>/<channel>.json
```

- `<device>` is the device's `ro.product.device` (for example `jagar`).
- `<channel>` is `alpha` when the running build is an alpha tag (`1.0.18-alpha.…`), otherwise `stable`.

If the file is missing or broken, the app shows "Couldn't load release notes" and a retry button.
It keeps the last good copy, so devices that loaded the notes once can still see them offline.

## File format (v1)

`schema/release-notes.v1.schema.json` is the full schema. In short:

```json
{
  "schemaVersion": 1,
  "product": "SolOS",
  "device": "jagar",
  "channel": "alpha",
  "updatedAt": "2026-10-19",
  "releases": [
    {
      "version": "1.0.18-alpha.10.12",
      "date": "2026-10-15",
      "sections": [
        { "type": "new", "title": "What's New", "items": ["…"] },
        { "type": "improvements", "title": "Improvements", "items": ["…"] },
        { "type": "fixes", "title": "Bug Fixes", "items": ["…"] }
      ]
    }
  ]
}
```

- **`releases`** go newest first. The app marks the release whose version matches the
  installed build as **Installed**.
- **`version`** is the build's `ro.mediatek.version.release` without the trailing firmware
  build number: `1.0.18-alpha.10.12`, not `1.0.18-alpha.10.12-1407`.
- **Section types:** `important`, `new`, `improvements` and `fixes` are shown in that order.
  Any other type is shown after them, under its own `title`, so you can add one without an app
  update. Leave out sections that would be empty.
- **`title`** on a release is optional. When set, it's shown under the version.
- **Compatibility:** adding optional fields or new section types keeps `schemaVersion` 1. A
  change that old apps can't read goes in a new `v2/` folder; leave `v1/` in place for devices
  that haven't updated.

## Adding a release

`AGENTS.md` has the full process for turning raw notes (commit logs, tickets, an engineering
changelog) into published entries: what to keep, what to drop and how to word it. It's written
so an LLM can follow it: hand the raw notes to Claude Code or another agent in this repo and it
picks the guide up automatically. People can follow the same steps by hand.

1. Put raw notes under `drafts/` (ignored by git) or paste them into the chat.
2. Add the release to `v1/<device>/<channel>.json` as `AGENTS.md` describes.
3. Run `scripts/validate.py`. CI runs it on every pull request and on `main`.
4. Open a pull request and get it reviewed, including the list of dropped items. Merging
   publishes it.

Builds pulled before or after release aren't listed. For example, 1.0.18-alpha.10.6 was
superseded by 1.0.18-alpha.10.7, and 1.0.18-alpha.8.1 by 1.0.18-alpha.8.2.
