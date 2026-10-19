# Turning raw release notes into published notes

You'll be handed **raw notes** for one or more SolOS builds: commit logs, Jira or Linear
exports, Slack threads, an engineering changelog, or a JSON draft like an earlier
`jagar_release.json`. Your job is to turn them into **customer-facing** entries in
`v1/<device>/<channel>.json`. Software Updater shows these to customers, and merging to `main`
publishes them within minutes, because this repo is public.

The file format is defined once, in `schema/release-notes.v1.schema.json`. `README.md` explains
how the app reads it. Read both before your first edit, and follow the existing entries in
`v1/jagar/alpha.json` for tone.

## Steps

1. **Identify the target file and builds.**
   - The device is the `ro.product.device` codename. `jagar` is the DC-1.
   - The channel is `alpha` for `-alpha` versions and `stable` otherwise; those are the only two
     the app reads. For any other pre-release (`-beta`, `-rc`), ask which file it belongs in.
   - Normalise each version to the published form: `1.0.18-alpha.10.13`. Drop the trailing
     firmware build number (`-1407`, `-26101600`) and OTA file name parts (`20261015.1558`,
     `jagar.user`, `signed-ota`). "Alpha 10.13" means `1.0.18-alpha.10.13` only if the file's
     newest entry is on 1.0.18; otherwise ask.
   - Confirm each build was offered to devices. The raw notes need to say so, for example "offered
     to alpha group" or a release date; if they don't, ask.
   - Done when every build in the raw notes maps to one target file and one version.

2. **Sort every raw item.** Give each item exactly one fate, as defined under
   [Sorting items](#sorting-items): **important**, **new**, **improvements**, **fixes** or
   **dropped**. Done when every raw item is accounted for, with no item left unsorted and none
   used twice.

3. **Rewrite the kept items.** Follow [Writing items](#writing-items). Done when each item is
   one sentence a customer understands without knowing the codebase.

4. **Edit the file.**
   - Add each new release at its position by version: newest first, so a new build usually
     goes at the top.
   - Include only sections that have items, in the order important, new, improvements, fixes.
   - Set the release `date` (YYYY-MM-DD) to the day the build was offered to devices. Use the
     date from the raw notes. A missing year can come from the OTA file name, which starts with
     the build date (`20261016.0912…`). With no date at all, ask.
   - Set the file's `updatedAt` to today; it may already be today.
   - When the raw notes revise a release that's already published, edit that entry in place.
     Never add a second entry for the same version.
   - Done when the file contains every kept item, and the only other change is `updatedAt`.

5. **Validate.** Run `scripts/validate.py`. Done when it prints `OK`. Fix every error it
   reports rather than working around the check.

6. **Report back for review.** A person approves every change before it's merged. Give them:
   - the versions you added or changed;
   - every **dropped** item, with a one-line reason each;
   - every judgement call: an item you weren't sure was customer-facing, merged items, a
     section you weren't sure about, a date or version you inferred, a number you left out;
   - every **future behaviour** item you held back, so they can decide whether customers need
     a heads-up now.

   Commit and push only when they ask. The repo is public, so the raw notes stay out of it: keep
   them in chat or under `drafts/`, which git ignores.

## Sorting items

| Fate | What goes there | Examples |
|---|---|---|
| **important** | Something the customer must know before or after updating: data that won't carry over, a setting that resets, an action they need to take. Rare. | "Notes stored in the previous Note Overlay app are not automatically imported into the new app in this release." |
| **new** | A capability the customer didn't have before. | A new app, setting, gesture or shortcut. |
| **improvements** | Something that existed and now works or looks better. | Faster, smoother, clearer, more reliable, redesigned. |
| **fixes** | Something that was broken and now isn't. | A crash, a wrong action, a visual glitch. |
| **dropped** | Anything a customer wouldn't notice or shouldn't see. | See the list below. |

Drop:
- **Internal-only changes:** build, CI, signing, test, logging, tooling, refactors, dependency
  bumps and manifest changes with no visible effect.
- **Changes that cancel out:** a change and its revert within the same release.
- **Builds never offered to devices,** such as a build pulled before release. Leave the whole
  build out and mention it in your report; `README.md` lists the known ones.
- **Internal names:** ticket numbers, branch names, code names, people's names and partner
  names that aren't public. Rewrite the item without them if it's still worth keeping;
  otherwise drop it.
- **Unconfirmed claims:** wording the raw notes mark as tentative or unverified, such as "may
  fix", "should improve" or "needs QA". When an item mixes a confirmed change with an
  unconfirmed claim, publish the confirmed part only if it stands on its own, and flag the item
  either way.
- **Future behaviour:** anything the notes say only takes effect in a later build. It belongs
  in that build's notes; list it in your report.

**Merge** follow-ups into the change they follow: when one customer-visible change appears as
several raw items in the same release (a feature plus fixes for bugs it introduced), publish it
once and report the follow-ups as merged into it.

## Writing items

- **One sentence, ending with a full stop,** in plain language a customer understands.
  Describe what they see or can now do, not how it was built.
- **Start new and improvement items with what the customer can do or see:** "Swipe inward from
  either screen edge to go back." "See connected Wi-Fi and Bluetooth device names more
  clearly."
- **Start fixes with "Fixed",** naming the symptom the customer saw: "Fixed issues with taskbar
  taps and closing apps." Some older entries predate this rule; follow the rule for new ones.
- **Use product names as customers see them:** SolOS, Note Overlay, Quick Settings, the orange
  button, Kindle. Use US spelling.
- **Stay factual and modest.** Describe exactly what changed, without overstating it. Leave
  out figures ("2x faster", "30% less battery") unless the raw notes say they come from release
  testing, and report any you left out.
- **Keep a release `title` out** unless the raw notes give a real headline for that build.
  The app already shows "SolOS <version>" as the heading.

## Adding a device or channel

Create `v1/<device>/<channel>.json` with the same top-level fields as `v1/jagar/alpha.json`.
The folder name must equal `device` and the file name must equal `channel`; the validator
checks both. Confirm the codename with the person first, because a typo makes the app show
"Couldn't load release notes" on every device of that kind.
