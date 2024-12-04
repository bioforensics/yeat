SHELL = bash
TEST_DATA_PATH ?= yeat/tests/data
PYFILES = $(shell ls yeat/*.py yeat/*/*.py)

## #===== development tasks =====#

## help:        print this help message and exit
help: Makefile
	@sed -n 's/^## //p' Makefile

## test:        run only short-running automated tests
test:
	pytest --cov=yeat -m short

## testlong:    run only long-running automated tests
testlong:
	pytest --cov=yeat -m long

## testillumina:run only Illumina short-read automated tests
testillumina:
	pytest --cov=yeat -m illumina

## testhifi:    run only PacBio HiFi-read automated tests
testhifi:
	pytest --cov=yeat -m hifi

## testnano:    run only Oxford Nanopore-read automated tests
testnano:
	pytest --cov=yeat -m nano

## testhybrid:  run only Hybrid automated tests
testhybrid:
	pytest --cov=yeat -m hybrid

## testbandage: run only Bandage required automated tests
testbandage:
	pytest --cov=yeat -m bandage

## testlinux:   run only Linux required automated tests
testlinux:
	pytest --cov=yeat -m linux

## testgrid:    run only grid required automated tests
testgrid:
	pytest --cov=yeat -m grid --basetemp=tmp

## testall:     run all tests but Bandage, Linux, and grid required tests
testall:
	pytest --cov=yeat -m 'not bandage and not linux and not grid'

## testdata:    download test data for test suite
testdata:
	pushd $(TEST_DATA_PATH) && \
	curl -L -o osfstorage-archive.zip https://files.osf.io/v1/resources/b8x5q/providers/osfstorage/?zip= && \
	unzip -o osfstorage-archive.zip && \
	rm osfstorage-archive.zip && \
	popd

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
