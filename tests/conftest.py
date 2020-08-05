import pytest


@pytest.fixture
def spinner_test():
    def spinner_test(output):
        def inner_factory(length_actual=None):
            def inner_spinner():
                for c in output:
                    yield (c * (length_actual or 1))[:length_actual]

            inner_spinner.cycles = len(output)
            return inner_spinner

        inner_factory.natural = len(output[0])
        return inner_factory

    yield spinner_test
