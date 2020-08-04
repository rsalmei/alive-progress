import pytest


@pytest.fixture
def spinner_test():
    def spinner_test(output):
        # noinspection PyUnusedLocal
        def inner_factory(length_actual=None):
            def inner_spinner():
                yield from output

            inner_spinner.cycles = len(output)
            return inner_spinner

        inner_factory.natural = len(output[0])
        return inner_factory

    yield spinner_test
