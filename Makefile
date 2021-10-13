SHELL = bash
PYFILES = $(shell ls yeat/*.py yeat/*/*.py)

## #===== development tasks =====#

## help:        print this help message and exit
help: Makefile
	@sed -n 's/^## //p' Makefile

## test:        run automated test suite
test:
	pytest --cov=yeat -m 'not drmaa and not long'

## format:      autoformat Python code
format:
	black --line-length=99 $(PYFILES)
