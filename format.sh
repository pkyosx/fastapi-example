#!/bin/bash

FORMAT_DIR=app

autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place "${FORMAT_DIR}" --exclude=__init__.py
black "${FORMAT_DIR}"
isort -rc "${FORMAT_DIR}"
