.PHONY: clean build release

all:
	@grep -E "^\w+:" makefile | cut -d: -f1

clean: clean-build clean-pyc

clean-build:
	rm -rf build dist

clean-pyc:
	find . -type f -name *.pyc -delete

build: clean
	python setup.py sdist bdist_wheel

release: build
	twine upload dist/*
