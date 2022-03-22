"""
Implements support for grapheme clusters and cells (columns on screen).
Graphemes are sequences of codepoints, which are interpreted together based on the Unicode
standard. Grapheme clusters are sequences of graphemes, glued together by Zero Width Joiners.
These graphemes may occupy one or two cells on screen, depending on their glyph size.

Support for these cool chars, like Emojis 😃, was so damn hard to implement because:
1. Python don't know chars that occupy two columns on screen, nor grapheme clusters that are
    rendered as a single char (wide or not), it only understands codepoints;
2. Alive-progress needs to visually align all frames, to keep its progress bars' length from
    popping up and down while running. For this I must somehow know which chars are wide and
    counterbalance that;
3. Alive-progress also has all kinds of animations, which to be generated needs several operations,
    namely len, iterating, indexing, slicing, concatenating and reversing, which now must support
    graphemes and cells! Argh.
4. For that I needed to parse them myself, which I tried but soon realized it was tricky and
    finicky, in addition to changing every year;
5. Then I looked into some lib dependencies, tested several, created the validate tool to help me
    test some Unicode versions, and chose one lib to use;
6. I finally implemented the operations I needed, to the best of my current knowledge, but it
    still wouldn't work. So I tried several spinners to check their alignments, until I finally
    realized what was wrong: I actually needed to align cells, not lengths nor even graphemes!

    For example:
        string \\ length  python  graphemes  cells
             nonono          6        6        6
             🏴󠁧󠁢󠁥󠁮󠁧󠁿👉🏾🏴󠁧󠁢󠁥󠁮󠁧󠁿          16       3        6

7. With that knowledge, I implemented "wide" marks on graphemes, and refactored all operations,
    but it still didn't work. I realized that animations would make these wide chars dynamically
    enter and leave the stage at will, so the frames would end up with different sizes!
    I needed something that could "see" all the frames at once, so I could equalize their sizes...
    So I created the cool spinner compiler, including a light and rocket fast runner;
8. Then I refactored the frame spinner factory, the first and simplest one, and WOW, it worked!
9. To make the others work too, I created the check tool to help me see a spinner's contents,
    directly from the compiled data;
10. The spinner compiler has enabled several improvements in the spinners code, since it ended up
    being a central command center with a lot of functionality, like reshaping and transposing
    the cycle data, or randomizing its playing. The concept of styling parameters and operational
    parameters got stronger with new operational commands, which enabled simpler compound
    animations, without any code duplication. That has enabled me to create the new sequential and
    alongside spinners, way more advanced than before, with intermix and pivot control of cycles;
11. After all of them was working, it was time for the bars, title, exhibit and alive_bar rendering
    itself, which needed to learn how to use the new architecture: change ordinary strings for
    tuples of cells (marked graphemes). All of them needed this same support for the soft wrap to
    keep working;
12. Profit! Only no... But what a ride! 😅

"""

import re
import unicodedata

from .terminal import FULL

PATTERN_SANITIZE = re.compile(r'[\r\n]')
VS_15 = '\ufe0e'


def print_cells(fragments, cols, last_line_len=0, _term=FULL):
    """Print a tuple of fragments of tuples of cells on the terminal, until a given number of
    cols is achieved, slicing over cells when needed.

    Args:
        fragments (Tuple[Union[str, Tuple[str, ...]]): the fragments of message, which are
            joined and gain spaces between them
        cols (int): maximum columns to use
        last_line_len (int): if the size of these fragments are smaller than this, the line is
            cleared before printing anything
        _term: the terminal to be used

    Returns:
        the number of actually used cols.

    """
    available = cols
    _term.write(_term.carriage_return)
    for fragment in filter(None, fragments):
        if fragment == '\n':
            _term.clear_end_line(available)
            available = cols
        elif available == 0:
            continue
        else:
            length = len(fragment)
            if length <= available:
                available -= length
            else:
                available, fragment = 0, fix_cells(fragment[:available])

        _term.write(join_cells(fragment))

    if last_line_len and cols - available < last_line_len:
        _term.clear_end_line(available)

    return cols - available


def join_cells(fragment):
    """Beware, this looses the cell information, converting to a simple string again.
    Don't use unless it is a special case."""
    return ''.join(strip_marks(fragment))


def combine_cells(*fragments):
    """Combine several fragments of cells into one.
    Remember that the fragments get a space between them, so this is mainly to avoid it when
    not desired."""
    return sum(fragments, ())  # this is way faster than tuple(chain.from_iterable()).


def is_wide(g):
    """Try to detect wide chars.

    This is tricky, I've seen several graphemes that have Neutral width (and thus use one
    cell), but actually render as two cells, like shamrock and heart ☘️❤️.
    I've talked to George Nachman, the creator of iTerm2, which has explained to me [1] the fix
    would be to insert a space after these cases, but I can't possibly know if this
    behavior is spread among all terminals, it probably has to do with the Unicode version too,
    so I'm afraid of fixing it.
    Use the `alive_progress.tools.print_chars` tool, and check the section around `0x1f300`
    for more examples.

    [1]: https://gitlab.com/gnachman/iterm2/-/issues/9185

    Args:
        g (str): the grapheme sequence to be tested

    """
    return g[-1] != VS_15 and (len(g) > 1 or unicodedata.east_asian_width(g) in ('W', 'F'))


def fix_cells(chars):
    """Fix truncated cells, removing whole clusters when needed."""
    if not chars:
        return chars

    start = (' ',) if chars[0] is None else ()
    end = (' ',) if chars[-1] is not None and is_wide(chars[-1]) else ()
    return (*start, *chars[bool(start):-1 if end else None], *end)  # noqa


def to_cells(text):
    text = ' '.join(PATTERN_SANITIZE.split(text or ''))
    return mark_graphemes(split_graphemes(text))


def split_graphemes(text):
    from grapheme import graphemes
    return tuple(graphemes(text))


def mark_graphemes(gs):
    return sum(((g, *((None,) if is_wide(g) else ())) for g in gs), ())


def strip_marks(chars):
    return (c for c in chars if c)


def has_wide(text):
    return any(is_wide(x) for x in text)
