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
    ruff check alive_progress --line-length 100

build: lint clean
    python setup.py sdist bdist_wheel

release: build && tag
    twine upload dist/*

tag:
    #!/usr/bin/env zsh
    tag=$(python -c 'import alive_progress; print("v" + alive_progress.__version__)')
    git tag -a $tag -m "Details: https://github.com/rsalmei/alive-progress/blob/main/CHANGELOG.md"
    git push origin $tag

test:
    pytest {{ cov }}

ptw:
    ptw -- {{ cov }}

cov-report:
    coverage report -m
