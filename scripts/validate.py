#!/usr/bin/env python3
"""Checks every v1/<device>/<channel>.json against the rules Software Updater relies on.

Standard library only, so it runs anywhere CI or a laptop has Python 3. It enforces the
same rules as schema/release-notes.v1.schema.json plus the ones a JSON Schema can't
express: file name and folder match the content, versions are unique and newest first.

Usage: scripts/validate.py [files...]   (defaults to every v1/*/*.json)
"""

import datetime
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CHANNELS = {"alpha", "beta", "stable"}
VERSION = re.compile(r"^\d+\.\d+\.\d+(-[0-9A-Za-z.]+)?$")
DEVICE = re.compile(r"^[a-z0-9_]+$")
SECTION_TYPE = re.compile(r"^[a-z][a-z0-9_]*$")


def version_key(version):
    # Same ordering as Software Updater's BuildInfoUtils.compareVersions: digit runs, left to right.
    return [int(part) for part in re.findall(r"\d+", version)]


def is_date(value):
    if not isinstance(value, str):
        return False
    try:
        datetime.date.fromisoformat(value)
        return True
    except ValueError:
        return False


def non_empty_string(value):
    return isinstance(value, str) and value.strip() != ""


def check(path):
    errors = []

    def err(where, message):
        errors.append(f"{path.relative_to(ROOT)}: {where}: {message}")

    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        err("file", f"not valid JSON ({e})")
        return errors
    if not isinstance(doc, dict):
        err("file", "top level must be an object")
        return errors

    if doc.get("schemaVersion") != 1:
        err("schemaVersion", "must be 1 for files under v1/")
    if not non_empty_string(doc.get("product")):
        err("product", "required")
    device = doc.get("device")
    if not (isinstance(device, str) and DEVICE.match(device)):
        err("device", "required, lowercase ro.product.device")
    elif device != path.parent.name:
        err("device", f"'{device}' doesn't match folder '{path.parent.name}'")
    channel = doc.get("channel")
    if channel not in CHANNELS:
        err("channel", f"must be one of {sorted(CHANNELS)}")
    elif channel != path.stem:
        err("channel", f"'{channel}' doesn't match file name '{path.name}'")
    if not is_date(doc.get("updatedAt")):
        err("updatedAt", "required, YYYY-MM-DD")

    releases = doc.get("releases")
    if not isinstance(releases, list) or not releases:
        err("releases", "must be a non-empty list")
        return errors

    seen = set()
    previous = None
    for i, release in enumerate(releases):
        where = f"releases[{i}]"
        if not isinstance(release, dict):
            err(where, "must be an object")
            continue
        version = release.get("version")
        if not (isinstance(version, str) and VERSION.match(version)):
            err(where, f"version '{version}' must look like 1.0.18-alpha.10.12 (no firmware build suffix)")
            continue
        where = f"releases[{i}] ({version})"
        if version in seen:
            err(where, "duplicate version")
        seen.add(version)
        if previous is not None and version_key(version) >= version_key(previous):
            err(where, f"must be older than the release above it ({previous}); keep newest first")
        previous = version
        if not is_date(release.get("date")):
            err(where, "date required, YYYY-MM-DD")
        if "title" in release and not non_empty_string(release["title"]):
            err(where, "title, when present, must be a non-empty string")
        sections = release.get("sections")
        if not isinstance(sections, list) or not sections:
            err(where, "sections must be a non-empty list")
            continue
        types = set()
        for j, section in enumerate(sections):
            swhere = f"{where} sections[{j}]"
            if not isinstance(section, dict):
                err(swhere, "must be an object")
                continue
            stype = section.get("type")
            if not (isinstance(stype, str) and SECTION_TYPE.match(stype)):
                err(swhere, "type required, lowercase identifier")
            elif stype in types:
                err(swhere, f"type '{stype}' appears twice; merge the items")
            types.add(stype)
            if not non_empty_string(section.get("title")):
                err(swhere, "title required")
            items = section.get("items")
            if not isinstance(items, list) or not items:
                err(swhere, "items must be a non-empty list; drop empty sections")
            elif not all(non_empty_string(item) for item in items):
                err(swhere, "every item must be a non-empty string")
    return errors


def main(argv):
    paths = [pathlib.Path(a).resolve() for a in argv] or sorted(ROOT.glob("v1/*/*.json"))
    if not paths:
        print("no release notes files found under v1/", file=sys.stderr)
        return 1
    errors = [e for p in paths for e in check(p)]
    for e in errors:
        print(e, file=sys.stderr)
    if errors:
        return 1
    print(f"OK: {len(paths)} file(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
