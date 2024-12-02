SHELL = bash
PYFILES = $(shell ls yeat/*.py yeat/*/*.py)

## #===== development tasks =====#

## help:         print this help message and exit
help: Makefile
	@sed -n 's/^## //p' Makefile

## test:         run short-running automated tests
test:
	pytest --cov=yeat -m short

## testlong:     run long-running automated tests
testlong:
	pytest --cov=yeat -m long

## testillumina: run Illumina short-read automated tests
testillumina:
	pytest --cov=yeat -m illumina

## testhifi:     run PacBio HiFi-read automated tests
testhifi:
	pytest --cov=yeat -m hifi

## testnano:     run Oxford Nanopore-read automated tests
testnano:
	pytest --cov=yeat -m nano

## testhybrid:   run hybrid automated tests
testhybrid:
	pytest --cov=yeat -m hybrid

## testbandage:  run Bandage-specific automated tests
testbandage:
	pytest --cov=yeat -m bandage

## testlinux:    run Linux-specific automated tests
testlinux:
	pytest --cov=yeat -m linux

## testgrid:     run grid-specific automated tests
testgrid:
	pytest --cov=yeat -m grid --basetemp=tmp

## testall:      run all tests, excluding Bandage, Linux, and grid-specific tests
testall:
	pytest --cov=yeat -m 'not bandage and not linux and not grid'

## testdata:     download test data for test suite
testdata:
	curl -L -o yeat/tests/data/ecoli.fastq https://sra-pub-src-1.s3.amazonaws.com/SRR10971019/m54316_180808_005743.fastq.1
	gzip yeat/tests/data/ecoli.fastq
	curl -L -o yeat/tests/data/ecolk12mg1655_R10_3_guppy_345_HAC.fastq.gz https://figshare.com/ndownloader/files/21623145
	curl -L -o yeat/tests/data/zymoD6331std-ecoli-ten-percent.fq.gz https://zenodo.org/record/5908204/files/zymoD6331std-ecoli-ten-percent.fq.gz?download=1

## style:        check code style against Black
style:
	black --line-length=99 --check $(PYFILES)

## format:       autoformat Python code
format:
	black --line-length=99 $(PYFILES)

## hooks:        deploy Git pre-commit hooks for development
hooks:
	echo "#!/usr/bin/env bash" > .git/hooks/pre-commit
	echo "set -eo pipefail" >> .git/hooks/pre-commit
	echo "make format" >> .git/hooks/pre-commit
	echo 'git add $$(ls setup.py yeat/*.py yeat/*/*.py)' >> .git/hooks/pre-commit
	chmod 755 .git/hooks/pre-commit
