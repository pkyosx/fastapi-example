#!/usr/bin/env bash

set -ex
pushd fastapi_example
exec alembic upgrade head
