SHELL = bash
PYFILES = $(shell ls yeat/*.py yeat/*/*.py)

## #===== development tasks =====#

## help:        print this help message and exit
help: Makefile
	@sed -n 's/^## //p' Makefile

## test:        run automated test suite
test:
	pytest --cov=yeat -m 'not long and not bandage and not hifi'

## testlong:    run only long-running automated tests
testlong:
	pytest --cov=yeat -m 'long and not bandage and not hifi'

## testbandage: run only bandage required automated tests
testbandage:
	pytest --cov=yeat -m bandage

## testhifi:    run only PacBio HiFi-reads automated tests
testhifi:
	pytest --cov=yeat -m 'hifi and not long and not bandage'

## testall:     run all tests but bandage required tests
testall:
	pytest --cov=yeat -m 'not bandage'

## hifidata:    download PacBio HiFi test data for test suite
hifidata:
	curl -L -o yeat/tests/data/ecoli.fastq https://sra-pub-src-1.s3.amazonaws.com/SRR10971019/m54316_180808_005743.fastq.1
	gzip yeat/tests/data/ecoli.fastq

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
