import argparse
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = (
    "plugin.json",
    "gemini-extension.json",
    ".codex-plugin/plugin.json",
    ".claude-plugin/plugin.json",
)
SEMVER = re.compile(r"\d+\.\d+\.\d+")


def main() -> None:
    parser = argparse.ArgumentParser(description="Keep plugin manifest versions in sync.")
    parser.add_argument("version", nargs="?", help="version to set, in X.Y.Z form")
    parser.add_argument("--check", action="store_true", help="check versions without changing files")
    args = parser.parse_args()

    if args.check == bool(args.version):
        parser.error("provide either VERSION or --check")

    documents = {
        name: json.loads((ROOT / name).read_text(encoding="utf-8")) for name in MANIFESTS
    }

    if args.check:
        version = documents["plugin.json"]["version"]
        if not SEMVER.fullmatch(version):
            parser.error(f"plugin.json version must use X.Y.Z, got: {version}")
        mismatches = [
            f"{name} is {document['version']}, plugin.json is {version}"
            for name, document in documents.items()
            if document["version"] != version
        ]
        if mismatches:
            parser.error("version mismatch:\n  " + "\n  ".join(mismatches))
        print(f"all manifests at {version}")
        return

    version = args.version
    if not SEMVER.fullmatch(version):
        parser.error(f"version must use X.Y.Z, got: {version}")
    for name, document in documents.items():
        document["version"] = version
        (ROOT / name).write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"set all manifests to {version}")


if __name__ == "__main__":
    main()
