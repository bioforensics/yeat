SHELL = bash
TEST_DATA_PATH ?= yeat/tests/data
PYFILES = $(shell find yeat/ -type f -name "*.py")

## #===== development tasks =====#

## help:         print this help message and exit
help: Makefile
	@sed -n 's/^## //p' Makefile

## test:         run short-running automated tests
test:
	pytest --cov=yeat -m "not long"

## testgrid:     run grid-specific automated tests
testgrid:
	pytest --cov=yeat -m grid --basetemp=tmp

## testall:      run all tests, excluding grid-specific tests
testall:
	pytest --cov=yeat -m 'not grid'

## style:        check code style against Black
style:
	black --line-length=99 --check $(PYFILES)
	snakefmt --line-length=9999 --check yeat/workflow

## format:       autoformat Python code
format:
	black --line-length=99 $(PYFILES)
	snakefmt --line-length=9999 yeat/workflow

## hooks:        deploy Git pre-commit hooks for development
hooks:
	echo "#!/usr/bin/env bash" > .git/hooks/pre-commit
	echo "set -eo pipefail" >> .git/hooks/pre-commit
	echo "make format" >> .git/hooks/pre-commit
	echo 'git add $$(ls setup.py yeat/*.py yeat/*/*.py)' >> .git/hooks/pre-commit
	chmod 755 .git/hooks/pre-commit
