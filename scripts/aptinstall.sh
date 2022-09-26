#!/bin/bash
set -e

if [[ ! -x "$(command -v curl)" ]]; then
  apt-get update && apt-get install -y curl
fi

if [[ ! -x "$(command -v xmllint)" ]]; then
  apt-get update && apt-get install -y libxml2-utils
fi

set +e
