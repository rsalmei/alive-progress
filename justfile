# coverage related
cov := "--cov=alive_progress --cov-branch --cov-report=term-missing"

all:
    @just --list

install:
    pip install -r requirements/dev.txt -r requirements/test.txt -e .

clean: clean-build clean-pyc

clean-build:
    rm -rf build dist alive_progress.egg-info

clean-pyc:
    find . -type f -name *.pyc -delete

lint:
    ruff alive_progress --line-length 100

build: lint clean
    python setup.py sdist bdist_wheel

release: build
    twine upload dist/*

test:
    pytest {{cov}}

ptw:
    ptw -- {{cov}}

cov-report:
    coverage report -m
