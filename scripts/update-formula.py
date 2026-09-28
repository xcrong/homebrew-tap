#!/usr/bin/env python3
"""Point each Formula/*.rb at the latest GitHub release of its app.

Usage:
    python3 scripts/update-formula.py [formula ...]

With no arguments, every registered formula is checked. A formula that
already matches its latest release is left untouched.

To onboard a new app: add one entry to FORMULAE below, drop its
Formula/<name>.rb into this tap, and the daily workflow picks it up.
"""

import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

FORMULAE = {
    # formula name -> upstream GitHub repo and expected release assets.
    "brewup": {
        "repo": "xcrong/brewup",
        "assets": (
            "brewup-aarch64-apple-darwin.tar.gz",
            "brewup-x86_64-apple-darwin.tar.gz",
            "brewup-x86_64-unknown-linux-gnu.tar.gz",
        ),
    },
}


def latest_tag(repo: str, assets: tuple[str, ...]) -> str:
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "homebrew-tap-update",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        f"https://api.github.com/repos/{repo}/releases/latest",
        headers=headers,
    )
    payload = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req) as response:
                payload = json.load(response)
            break
        except urllib.error.HTTPError as exc:
            retryable = exc.code in (403, 429, 500, 502, 503)
            last_attempt = attempt == 2
            if not retryable or last_attempt:
                if exc.code == 403:
                    sys.exit(
                        "GitHub API returned 403 (rate limit exceeded). "
                        "Set GH_TOKEN/GITHUB_TOKEN so the request is authenticated."
                    )
                raise
            retry_after = exc.headers.get("Retry-After")
            if retry_after is not None:
                delay = int(retry_after)
            else:
                delay = 2**attempt * 10
            print(f"GitHub API returned {exc.code}, retrying in {delay}s...")
            time.sleep(delay)
    assert payload is not None
    tag = payload["tag_name"]
    names = {asset["name"] for asset in payload["assets"]}
    missing = [name for name in assets if name not in names]
    if missing:
        sys.exit(f"latest {repo} release {tag} is missing assets: {', '.join(missing)}")
    return tag


def formula_tag(text: str, formula: Path) -> str:
    found = set(re.findall(r"releases/download/(v[^/]+)/", text))
    if len(found) != 1:
        sys.exit(f"{formula} should pin one release tag, found {sorted(found)}")
    return found.pop()


def sha256(url: str) -> str:
    with tempfile.NamedTemporaryFile() as tmp:
        subprocess.run(["curl", "-fsSL", "-o", tmp.name, url], check=True)
        digest = hashlib.sha256()
        with open(tmp.name, "rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()


def replace_asset(
    text: str, repo: str, formula: Path, filename: str, tag: str, digest: str
) -> str:
    pattern = (
        rf'(url "https://github.com/{repo}/releases/download/)v[^/]+'
        rf'(/{re.escape(filename)}"\n\s*sha256 ")[0-9a-f]+(")'
    )

    def repl(match: re.Match[str]) -> str:
        return f"{match.group(1)}{tag}{match.group(2)}{digest}{match.group(3)}"

    updated, count = re.subn(pattern, repl, text, count=1)
    if count != 1:
        sys.exit(f"could not update {filename} in {formula}")
    return updated


def update_one(name: str) -> bool:
    """Update one formula. Returns True when the file changed."""
    entry = FORMULAE[name]
    repo, assets = entry["repo"], entry["assets"]
    formula = Path(f"Formula/{name}.rb")
    if not formula.is_file():
        sys.exit(f"missing {formula}; run from the tap repository root")
    text = formula.read_text()
    current = formula_tag(text, formula)
    tag = latest_tag(repo, assets)
    if tag == current:
        print(f"{name}: already matches {tag}")
        return False

    print(f"{name}: updating {current} -> {tag}")
    for filename in assets:
        url = f"https://github.com/{repo}/releases/download/{tag}/{filename}"
        text = replace_asset(text, repo, formula, filename, tag, sha256(url))
    if formula_tag(text, formula) != tag:
        sys.exit(f"{name}: formula tag was not updated")
    formula.write_text(text)
    print(f"{name}: updated to {tag}")
    return True


def main(argv: list[str]) -> None:
    names = argv or sorted(FORMULAE)
    unknown = [name for name in names if name not in FORMULAE]
    if unknown:
        sys.exit(f"unknown formulae: {', '.join(unknown)} (known: {sorted(FORMULAE)})")
    changed = [name for name in names if update_one(name)]
    if changed:
        print(f"updated: {', '.join(changed)}")
    else:
        print("all formulae already match their latest releases")


if __name__ == "__main__":
    main(sys.argv[1:])
