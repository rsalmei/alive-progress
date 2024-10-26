# Changelog

## 3.2.0 - Oct 26, 2024
- print/logging hooks now support multithreading
- rounded ETAs for long tasks
- support for zero and even negative bar increments
- custom offset for enriched print/logging messages
- improved compatibility with PyInstaller
- improved compatibility with Celery
- drop python 3.7 and 3.8, hello 3.12 and 3.13

## 3.1.5 - Nov 08, 2023
- ignore more errors when trying to set hooks (it seems `pyam` uses `setuptools_scm` which does `assert value is sys.stderr` in `setStream()` for whatever reason)

## 3.1.4 - May 31, 2023
- support spaces at the start and end of titles and units (removed trim)

## 3.1.3 - May 26, 2023
- better error handling of invalid `alive_it` calls before iterating it
- detect nested uses of alive_progress and throw a clearer error message

## 3.1.2 - May 08, 2023
- fix some exotic ANSI Escape Codes not being printed by supporting terminal [OSC](https://en.wikipedia.org/wiki/ANSI_escape_code#OSC)

## 3.1.1 - Apr 08, 2023
- support for printing ANSI Escape Codes without extra newlines, like "set console title"
- typing annotations in `alive_it`, so collection types are correctly identified

## 3.1.0 - Mar 23, 2023
- new resuming computations support with `skipped` items
- new `max_cols` config setting, the number of columns to use if not possible to fetch it, like in jupyter and other platforms which doesn't support size
- fix fetching the size of the terminal when using stderr
- officially supports Python 3.11
- included [ruff](https://github.com/charliermarsh/ruff) linter before building

## 3.0.1 - Jan 01, 2023
- fix for logging streams that extend StreamHandler but doesn't allow changing streams (import dill/tensorflow/dask issues)

## 3.0.0 - Dec 22, 2022
- units with automatic scaling and configurable precision
- automatic scaling for slow throughputs
- support for using `stderr` and other files instead of `stdout`
- smooth out the rate estimation
- more queries into the currently running widgets' data, including monitor, rate, and ETA
- new help system on configuration errors
- support for reusing logging handlers
- seek support for logging `RotatingFileHandler`
- fix unknown mode always ending with a warning (!)
- improved test branch coverage to 89%

## 2.4.1 - Apr 01, 2022
- fix a crash when dual-line and disabled are set

## 2.4.0 - Mar 21, 2022
- support dual-line text mode
- finalize function parameter in alive_it
- improve logging support, detecting customized ones
- fix final receipt and truncated bar in jupyter
- fix default stats_end, which did not follow stats
- fix `bar.text` assignment not working on alive_it

## 2.3.1 - Feb 11, 2022
- introduce ctrl_c config param
- print the final receipt even when interrupted

## 2.3.0 - Feb 07, 2022
- customizable `monitor`, `elapsed`, and `stats` core widgets
- new `monitor_end`, `elapsed_end`, and `stats_end` core widgets
- better support for CTRL+C, which makes `alive_bar` stop prematurely

## 2.2.0 - Feb 02, 2022
- bar title can be dynamically set, changed or removed
- new custom fps system, which enables very slow refresh rates (long periods)
- the final receipt can be hidden (great for special effects)
- new support for `click.echo()` printing
- more resilient `text` method which accepts any value, even numbers
- bar methods like `current` and `pause` are now read-only (read-only data descriptors)
- bar methods like `text` and `title` now support assigning in addition to calling (data descriptors)
- faster performance, with optimized flush control
- detection of terminal columns is safer for exotic environments
- fix hook manager trimming spaces at the start
- remove Python 3.6 support

## 2.1.0 - Oct 18, 2021
- Jupyter notebook support (experimental), Jupyter auto-detection, disable feature and configuration
- four internal terminal abstractions, to support TTY, JUPYTER, NON_TTY, and VOID

## 2.0.0 - Aug 25, 2021

This is a major achievement in `alive-progress`!
- now there's complete support for Emojis 🤩 and exotic Unicode chars in general, which required MAJOR refactoring deep within the project, giving rise to what I called **Cells Architecture** => now all internal components use and generate streams of cells instead of chars, and correctly interprets grapheme clusters — it has enabled to render complex multi-chars symbols as if they were one, thus making them work on any spinners, bars, texts, borders, backgrounds, everything!!! there's even support for wide chars, which are represented with any number of chars, including one, but take two spaces on screen!! pretty advanced stuff 🤓
- new super cool spinner compiler and runner, which generates complete animations ahead of time, and plays these ready-to-go animations seamlessly, with no overhead at all! 🚀
- the spinner compiler also includes advanced extra commands to generate and modify animations, like reshape, replace, transpose, or randomize the animation cycles!
- new powerful and polished `.check()` tools, that compile and beautifully render all frames from all animation cycles of spinners and bars! they can even include complete frame data, internal codepoints, and even their animations! 👏
- bars engine revamp, with invisible fills, advanced support for multi-char tips (which gradually enter and leave the bar), borders, tips and errors of any length, and underflow errors that can leap into the border if they can't fit!
- spinners engine revamp, with standardized factory signatures, improved performance, new types, and new features: smoother bouncing spinners (with an additional frame at the edges), optimized scrolling of text messages (which go slower and pause for a moment at the edges), new alongside and sequential spinners, nicer effect in alongside spinners (which use weighted spreading over the available space), smoother animation in scrolling spinners (when the input is longer than the available space)
- new builtin spinners, bars, and themes, which makes use of the new animation features
- new showtime that displays themes and is dynamic => it does not scroll the screen when it can't fit either vertically or horizontally, and can even filter for patterns!
- improved support for logging into files, which gets enriched as the print hook is!
- several new configuration options for customizing appearance, including support for disabling any `alive-progress` widgets!
- includes a new iterator adapter `alive_it`, that accepts an iterable and calls `bar()` for you!
- requires Python 3.6+ (and officially supports Python 3.9 and 3.10)

## 1.6.2 - Jan 7, 2021
- new `bar.current()` method
- newlines get printed on vanilla Python REPL
- bar is truncated to 80 chars on Windows

## 1.6.1 - Jul 11, 2020
- fix logging support for Python 3.6 and lower
- support logging for file
- support for wide Unicode chars, which use 2 columns but have length 1

## 1.6.0 - Jul 9, 2020
- soft wrapping support
- hiding cursor support
- Python logging support
- exponential smoothing of ETA time series
- proper bar title, always visible
- enhanced times representation
- new `bar.text()` method, to set situational messages at any time without incrementing position (deprecates 'text' parameter in `bar()`)
- performance optimizations

## 1.5.1 - May 4, 2020
- fix compatibility with Python 2.7 (should be the last one, version 2 is in the works, with Python 3 support only)

## 1.5.0 - May 2, 2020
- standard_bar accepts a `background` parameter instead of `blank`, which accepts arbitrarily sized strings and remains fixed in the background, simulating a bar going "over it"

## 1.4.4 - Apr 18, 2020
- restructure internal packages
- 100% branch coverage of all animations systems, i.e., bars and spinners

## 1.4.3 - Apr 14, 2020
- protect configuration system against other errors (length='a' for example)
- first automated tests, 100% branch coverage of configuration system

## 1.4.2 - Apr 13, 2020
- sanitize text input, keeping '\n' from entering and replicating the bar on the screen

## 1.4.1 - Mar 7, 2020
- include a license file in the source distribution

## 1.4.0 - Mar 5, 2020
- print() enrichment can now be disabled (locally and globally)
- exhibits now have a real-time fps indicator
- new exhibit functions `show_spinners` and `show_bars`
- new utility `print_chars`
- `show_bars` gains some advanced demonstrations (try it again!)

## 1.3.3 - Jan 26, 2020
- further improve stream compatibility with isatty

## 1.3.2 - Jan 26, 2020
- beautifully finalize bar in case of unexpected errors

## 1.3.1 - Jan 26, 2020
- fix a subtle race condition that could leave artifacts if ended very fast
- flush print buffer when position changes or bar terminates
- keep the total argument from unexpected types

## 1.3.0 - Sep 17, 2019
- new fps calibration system
- support force_tty and manual options in global configuration
- multiple increment support in bar handler

## 1.2.0 - Aug 24, 2019
- filled blanks bar styles
- clean underflow representation of filled blanks

## 1.1.1 - Aug 21, 2019
- optional percentage in manual mode

## 1.1.0 - Aug 17, 2019
- new manual mode

## 1.0.1 - Aug 9, 2019
- PyCharm console support with force_tty
- improve compatibility with Python stdio streams

## 1.0.0 - Aug 5, 2019
- first public release, already very complete and mature
