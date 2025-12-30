#!/usr/bin/env bash
set -eo pipefail

if [ -z "$IMAGE_URI" ]; then
  echo "IMAGE_URI is not set. IMAGE_URI should be set to the registry coordinates at which the image will be published"
  exit 255
fi

if [ -z "$PROJECT" ]; then
  echo "PROJECT is not set. PROJECT should be set to the directory name of the project to package."
  exit 255
fi

if [ -z "$CACHE_URI" ]; then
  echo "CACHE_URI is not set. CACHE_URI should be set to the registry coordinates at which the build cache will be stored"
  exit 255
fi

pack build \
  --descriptor "$PROJECT/project.toml" \
  --pull-policy=always \
  --trust-builder \
  --publish \
  --cache-image "$CACHE_URI" \
  "$IMAGE_URI" \
  --buildpack "dmikusa/apt@0.0.4" \
  --buildpack "urn:cnb:builder:paketo-buildpacks/python" \
