SHELL = bash
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

## testbandage: run only Bandage required automated tests
testbandage:
	pytest --cov=yeat -m bandage

## testlinux:   run only Linux required automated tests
testlinux:
	pytest --cov=yeat -m linux

## testgrid:    run only grid required automated tests
testgrid:
	pytest --cov=yeat -m grid --basetemp=tmp

## testall:     run all tests but Bandage and linux required tests
testall:
	pytest --cov=yeat -m 'not bandage and not linux and not grid'

## hifidata:    download PacBio HiFi-read test data for test suite
hifidata:
	curl -L -o yeat/tests/data/ecoli.fastq https://sra-pub-src-1.s3.amazonaws.com/SRR10971019/m54316_180808_005743.fastq.1
	gzip yeat/tests/data/ecoli.fastq

## nanodata:    download Oxford Nanopore-read test data for test suite
nanodata:
	curl -L -o yeat/tests/data/ecolk12mg1655_R10_3_guppy_345_HAC.fastq.gz https://figshare.com/ndownloader/files/21623145

## metadata:    download PacBio HiFi-read metagenomics test data for test suite
metadata:
	curl -L -o yeat/tests/data/zymoD6331std-ecoli-ten-percent.fq.gz https://zenodo.org/record/5908204/files/zymoD6331std-ecoli-ten-percent.fq.gz?download=1

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
