# Changelog

## 2.0.0 - Apr 29, 2021
This is a major breakthrough in `alive-progress`!
- now there's complete support for Emojis and exotic Unicode chars in general, which required MAJOR refactoring throughout the project, giving rise to a new **Cells Architecture** => now all internal components generate streams of codepoints instead of chars, which are rendered in "screen cells"; that enables to render complete grapheme clusters which semantically display as one char, and using one or two cells on screen (wide chars), pretty advanced stuff 🤓
- this architecture is system-wide, so it is supported in bar title, bar text, in all spinners (including front chars, borders and backgrounds) and in bars (including front chars, tip, borders, backgrounds and errors!)
- new super cool spinner compiler, which generates complete animations ahead-of-time! and spinner runner, which seamlessly play these artifacts with no overhead! 🚀
- this compiler even includes advanced extra commands to help generate animations, like reshape, replace and transpose, or even modify their runner like randomizing the animation cycles!
- super powerful and polished `.check()` tools in both spinners and bars! they compile and display custom spinners and bars, including complete frame data, internal codepoints and even their animations!
- bars engine revamp, with invisible fills, advanced support for multi-char tips, which gradually enter and leave the bar, borders, tips and errors of any length, and underflow error that can leap to border if it can't fit!
- spinners engine revamp, with standardized factory signatures, improved performance and new features: smoother bouncing spinners (additional frame at the edges), optimized scrolling of text messages (they go slower and pause for a moment at the edges), new animation modes in alongside and sequential spinners, nicer effect in alongside spinners, which use weighted spreading over the available space, smoother animation in scrolling spinners when the input is longer than the available space
- new builtin spinners, bars and themes that highlight the new animation features
- showtime now displays themes! and it is dynamic => it does not scroll the screen when it can't fit either vertically or horizontally, and can filter patterns!
- `bar()` handle now supports absolute and relative positioning in all modes
- improved logging for files, which gets enriched as the print hook
- several new configuration options for customizing appearance, for instance you can disable any `alive-progress` components, even the whole graphic bar if you'd like!
- includes a new quick mode `alive_it`, that iterates and calls `bar()` for you!
- uses `time.perf_counter()` high resolution clock
- when not connected to a tty, it won't generate any ansi escape sequences to the terminal
- improved `print_chars()` utility
- new tool to validate unicode grapheme cluster breaks
- new tool to estimate overhead, with a sampling of plenty of configuration options
- requires python 3.6+ (and officially supports python 3.9 and 3.10)


## 1.6.2 - Jan 7, 2021
- new `bar.current()` method
- newlines get printed on vanilla Python REPL
- bar is truncated to 80 chars on Windows


## 1.6.1 - Jul 11, 2020
- fix logging support for python 3.6 and lower
- support logging for file
- support for wide unicode chars, which use 2 columns but have length 1


## 1.6.0 - Jul 9, 2020
- soft wrapping support
- hiding cursor support
- python logging support
- exponential smoothing of ETA time series
- proper bar title, always visible
- enhanced times representation
- new `bar.text()` method, to set situational messages at any time without incrementing position (deprecates 'text' parameter in `bar()`)
- performance optimizations


## 1.5.1 - May 4, 2020
- fix compatibility with python 2.7 (should be the last one, version 2 is in the works, with python 3 support only)


## 1.5.0 - May 2, 2020
- standard_bar accepts a `background` parameter instead of `blank`, which accepts arbitrarily sized strings and remains fixed in the background, simulating a bar going "over it"


## 1.4.4 - Apr 18, 2020
- restructure internal packages
- 100% branch coverage of all animations systems, i.e., bars and spinners


## 1.4.3 - Apr 14, 2020
- protect configuration system against other errors (length='a' for example)
- first automated tests, 100% branch coverage of configuration system


## 1.4.2 - Apr 13, 2020
- sanitize text input, keeping '\n' from entering and replicating bar on screen


## 1.4.1 - Mar 7, 2020
- include license file in source distribution


## 1.4.0 - Mar 5, 2020
- print() enrichment can now be disabled (locally and globally)
- exhibits now have a real time fps indicator
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
- keep total argument from unexpected types


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
- pycharm console support with force_tty
- improve compatibility with python stdio streams


## 1.0.0 - Aug 5, 2019
- first public release, already very complete and mature
