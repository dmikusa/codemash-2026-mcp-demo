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

pack build \
  --descriptor "$PROJECT/project.toml" \
  --pull-policy=always \
  --trust-builder \
  --publish \
  "$IMAGE_URI"
