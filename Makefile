SHELL = bash
PYFILES = $(shell ls yeat/*.py yeat/*/*.py)
OS = $(shell uname)

## #===== development tasks =====#

## help:        print this help message and exit
help: Makefile
	@sed -n 's/^## //p' Makefile

## test:        run automated test suite
test:
	pytest --cov=yeat -m 'not long'

## testlong:    run only long-running automated tests
testlong:
	pytest --cov=yeat -m long

## testall:     run all tests
testall:
	pytest --cov=yeat

## style:       check code style vs Black
style:
	black --line-length=99 --check $(PYFILES)

## format:      autoformat Python code
format:
	black --line-length=99 $(PYFILES)

## bandage:     unpack Bandage to enable assembly graphs visualizations
bandage:
	@if [[ "$(OS)" == "Linux" ]]; then \
		yes A | unzip yeat/data/Bandage_Ubuntu_dynamic_v0_8_1.zip -d ~/Bandage; \
		sudo apt install build-essential git libgl1-mesa-dev libxcb-xinerama0; \
		sudo apt-get install libqt5gui5; \
	elif [[ "$(OS)" == "Darwin" ]]; then \
		yes A | unzip yeat/data/Bandage_Mac_v0_8_1.zip -d ~/Bandage; \
	else \
		echo "yeat does not support Bandage for: $(OS)"; \
	fi

## hooks:       deploy git pre-commit hooks for development
hooks:
	echo "#!/usr/bin/env bash" > .git/hooks/pre-commit
	echo "set -eo pipefail" >> .git/hooks/pre-commit
	echo "make format" >> .git/hooks/pre-commit
	echo 'git add $$(ls setup.py yeat/*.py yeat/*/*.py)' >> .git/hooks/pre-commit
	chmod 755 .git/hooks/pre-commit
