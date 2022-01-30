import pytest


@pytest.fixture
def spinner_test():
    def spinner_test(*data):
        def inner_factory(actual_length=None):
            def cycle_data():
                while True:
                    yield from data

            def inner_spinner():
                yield from next(cycle_gen)

            actual_length = actual_length or inner_factory.natural
            nonlocal data
            ratio = int(actual_length / len(data[0][0])) + 1
            data = tuple(tuple(tuple(d * ratio)[:actual_length] for d in cycle) for cycle in data)

            # generate spec info, just like the real one.
            frames = tuple(len(cycle) for cycle in data)
            inner_spinner.__dict__.update(cycles=len(data), length=len(data[0][0]),
                                          frames=frames, total_frames=sum(frames),
                                          natural=inner_factory.natural)

            cycle_gen = cycle_data()
            return inner_spinner

        # shortcut for single char animations.
        data = tuple(tuple(cycle) if isinstance(cycle, str) else cycle for cycle in data)
        # simulate to_cells().
        data = tuple(tuple(tuple(frame) for frame in cycle) for cycle in data)

        inner_factory.natural = len(data[0][0])
        return inner_factory

    yield spinner_test


@pytest.fixture
def show_marks():
    def show_marks(cells):
        return ''.join(x or 'X' for x in cells)

    return show_marks
