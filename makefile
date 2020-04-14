.PHONY: all install clean build release

# coverage related
SRC = alive_progress
COV = --cov=$(SRC) --cov-branch --cov-report=term-missing

all:
	@grep -E "^\w+:" makefile | cut -d: -f1

install:
	pip install -r requirements/dev.txt -r requirements/test.txt -e .

clean: clean-build clean-pyc

clean-build:
	rm -rf build dist

clean-pyc:
	find . -type f -name *.pyc -delete

build: clean
	python setup.py sdist bdist_wheel

release: build
	twine upload dist/*

test:
	pytest $(COV)

ptw:
	ptw -- $(COV)

cov-report:
	coverage report -m
