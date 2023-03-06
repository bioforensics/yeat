SHELL = bash
PYFILES = $(shell ls yeat/*.py yeat/*/*.py yeat/*/*/*.py)
# grep -R ".py" . <- doing this gets lots of random files

## #===== development tasks =====#

## help:        print this help message and exit
help: Makefile
	@sed -n 's/^## //p' Makefile

## test:        run automated test suite
test:
	pytest --cov=yeat -m 'not long and not bandage'

## testlong:    run only long-running automated tests
testlong:
	pytest --cov=yeat -m 'long and not bandage'

## testbandage: run only bandage required automated tests
testbandage:
	pytest --cov=yeat -m bandage

## testall:     run all tests but bandage required tests
testall:
	pytest --cov=yeat -m 'not bandage'

## style:       check code style vs Black
style:
	black --line-length=99 --check $(PYFILES)

## format:      autoformat Python code
format:
	black --line-length=99 $(PYFILES)

## hooks:       deploy git pre-commit hooks for development
hooks:
	echo "#!/usr/bin/env bash" > .git/hooks/pre-commit
	echo "set -eo pipefail" >> .git/hooks/pre-commit
	echo "make format" >> .git/hooks/pre-commit
	echo 'git add $$(ls setup.py yeat/*.py yeat/*/*.py)' >> .git/hooks/pre-commit
	chmod 755 .git/hooks/pre-commit
