# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals
import pytest


@pytest.fixture
def spinner_test():
    def spinner_test(output):
        # noinspection PyUnusedLocal
        def inner_factory(length_actual=None):
            def inner_spinner():
                for c in output:  # TODO python 27
                    yield c

            inner_spinner.cycles = len(output)
            return inner_spinner

        inner_factory.natural = len(output[0])
        return inner_factory

    yield spinner_test
