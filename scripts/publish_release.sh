#!/usr/bin/env bash
set -euo pipefail

: "${BEFORE_SHA:?BEFORE_SHA is required}"
: "${GITHUB_SHA:?GITHUB_SHA is required}"

version=$(python3 -c 'import json; print(json.load(open("plugin.json"))["version"])')
if [[ ! "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "plugin.json version must use X.Y.Z, got: $version" >&2
  exit 1
fi

previous_version=$(git show "${BEFORE_SHA}:plugin.json" | python3 -c 'import json, sys; print(json.load(sys.stdin)["version"])')
if [[ "$version" == "$previous_version" ]]; then
  echo "Version remains $version; nothing to release."
  exit 0
fi

tag="v$version"
if gh release view "$tag" >/dev/null 2>&1; then
  echo "Release $tag already exists."
  exit 0
fi

if git show-ref --verify --quiet "refs/tags/$tag"; then
  tag_sha=$(git rev-list -n 1 "$tag")
  if [[ "$tag_sha" != "$GITHUB_SHA" ]]; then
    echo "$tag already points to $tag_sha, expected $GITHUB_SHA" >&2
    exit 1
  fi
  gh release create "$tag" --verify-tag --generate-notes
else
  gh release create "$tag" --target "$GITHUB_SHA" --generate-notes
fi
