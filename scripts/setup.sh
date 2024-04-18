#!/usr/bin/env bash
set -e

curl -sSL https://pdm-project.org/install-pdm.py | python3 -

pdm install -G testing
