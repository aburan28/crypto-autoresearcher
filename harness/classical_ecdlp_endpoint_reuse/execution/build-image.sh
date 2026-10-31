#!/usr/bin/env bash
# Explicit operator build only. This file never publishes or launches an image.
set -euo pipefail
: "${SOURCE_REPO:?Set source repository checkout}"
: "${SOURCE_REVISION:?Set full committed source SHA}"
: "${PACKAGE_PATH:?Set committed repository-relative package path}"
: "${BASE_IMAGE:?Set actual Debian/Ubuntu-compatible OCI image at a SHA-256 digest}"
: "${IMAGE_TAG:?Set the explicit local image tag}"
: "${BUILD_CONTEXT:?Set a fresh build-context directory}"
[[ "$SOURCE_REVISION" =~ ^[a-f0-9]{40}$ ]] || { echo 'Invalid source SHA' >&2; exit 2; }
[[ "$BASE_IMAGE" =~ ^[^[:space:]]+@sha256:[a-f0-9]{64}$ ]] || { echo 'Base image must be digest-pinned' >&2; exit 2; }
python3 "$(dirname "$0")/prepare_context.py" --repo "$SOURCE_REPO" \
  --package-path "$PACKAGE_PATH" --source-revision "$SOURCE_REVISION" --output "$BUILD_CONTEXT"
docker build --platform linux/amd64 --pull --build-arg "BASE_IMAGE=$BASE_IMAGE" \
  --build-arg "SOURCE_REVISION=$SOURCE_REVISION" --iidfile "$BUILD_CONTEXT/local-image-id.txt" \
  --tag "$IMAGE_TAG" "$BUILD_CONTEXT"
printf 'Built locally. Publish through the authorized registry, retain the resulting registry digest and build-info.json. No workload was launched.\n'
