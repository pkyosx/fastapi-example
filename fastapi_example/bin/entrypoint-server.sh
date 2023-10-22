#!/usr/bin/env bash

set -ex
pip install watchdog
pushd fastapi_example
exec watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- gunicorn main:app
