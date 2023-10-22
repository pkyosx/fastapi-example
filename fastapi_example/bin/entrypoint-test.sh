#!/usr/bin/env bash

set -ex
pip install -r requirements-dev.txt
pushd fastapi_example
exec pytest --log-level=INFO --sw tests