[<img align="right" src="https://cdn.buymeacoffee.com/buttons/default-orange.png" width="217px" height="51x">](https://www.buymeacoffee.com/rsalmei)

![alive!](https://raw.githubusercontent.com/rsalmei/alive-progress/master/img/alive-logo.gif)

# alive-progress :)
### A new kind of Progress Bar, with real-time throughput, eta and very cool animations!

[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://gitHub.com/rsalmei/alive-progress/graphs/commit-activity)
[![PyPI version](https://img.shields.io/pypi/v/alive-progress.svg)](https://pypi.python.org/pypi/alive-progress/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/alive-progress.svg)](https://pypi.python.org/pypi/alive-progress/)
[![PyPI status](https://img.shields.io/pypi/status/alive-progress.svg)](https://pypi.python.org/pypi/alive-progress/)
[![PyPI downloads](https://img.shields.io/pypi/dm/alive-progress.svg)](https://pypi.python.org/pypi/alive-progress/)

Ever found yourself in a remote ssh session, doing some lengthy operations, and every now and then you feel the need to hit [enter] just to ensure you didn't lose the connection? Ever wondered where your processing is in, and when will it finish? Ever needed to *pause* the progress bar for a while, return to the python REPL for a manual inspection or fixing an item, and then *resume* the process like it never happened? I did...

I've made this cool progress bar thinking about all that, the **Alive-Progress** bar! :)

![alive-progress](https://raw.githubusercontent.com/rsalmei/alive-progress/master/img/alive-demo.gif)


I like to think of it as a new kind of progress bar for python, as it has among other things:

- a **cool live spinner**, which clearly shows your lengthy process did not hang and your ssh connection is healthy;
- a **visual feedback** of the current speed/throughput, as the spinner runs faster or slower according to the actual processing speed;
- an **efficient** multi-threaded bar, which updates itself at a fraction of the actual speed (1,000,000 iterations per second equates to roughly 60 frames per second refresh rate) to keep CPU usage low and avoid terminal spamming; (📌 new: you can now calibrate this!)
- an expected time of arrival (**ETA**), with a smart exponential smoothing algorithm that shows the remaining processing time in the most friendly way;
- a _print() hook_ and (📌 new) _logging support_, which allows print statements and logging messages **effortlessly** in the midst of an animated bar, automatically cleaning the screen and even enriching it with the current position when that occurred;
- after your processing has finished, a **nice receipt** is printed with the statistics of that run, including the elapsed time and observed throughput;
- it tracks your desired count, not necessarily the actual iterations, to detect **under and overflows**, so it will look different if you send in less or more than expected;
- it automatically detects if there's an **allocated tty**, and if there isn't (like in a pipe redirection), only the final receipt is printed, so you can safely include it in any code and rest assure your log file won't get thousands of progress lines;
- you can **pause** it! I think that's an unprecedented feature for a progress bar! It's incredible to be able to manually operate on some items while inside a running progress bar context, and get the bar back like it had never stopped whenever you want;
- it is **customizable**, with a growing smorgasbord of different bar and spinner styles, as well as several factories to easily generate yours!

> ### 📌 New in 1.6 series!
> - soft wrapping support - or lack thereof actually, it won't scroll your terminal desperately up if it doesn't fit the line anymore!
> - hiding cursor support - more beautiful and professional appearance!
> - python logging support - adequately clean and enriched messages from logging without any configuration or hack!
> - exponential smoothing of ETA - way smoother when you need it the most!
> - proper bar title - left aligned always visible title so you know what is expected from that processing!
> - enhanced elapsed time and ETA representation - the smallest rendition possible, so you can maximize the animations!
> - new `bar.text()` dedicated method - now you can change the situational message without making the bar going forward!
> - performance optimizations - even less overhead, your processing won't even notice it!


## Get it

Just install with pip:

```bash
$ pip install alive-progress
```


## Awake it

Open a context manager like this:

```python
from alive_progress import alive_bar
items = range(1000)                  # retrieve your set of items
with alive_bar(len(items)) as bar:   # declare your expected total
    for item in items:               # iterate as usual
        # process each item
        bar()                        # call after consuming one item
```

And it's alive! 👏

In general lines, just retrieve the items, enter the `alive_bar()` context manager, and iterate/process normally, calling `bar()` once per item.


### Understand it

- the `items` can be any iterable, and usually will be some queryset;
- the first argument of the `alive_bar` is the expected total, so it can be anything that returns an integer, like `qs.count()` for querysets, `len(items)` for iterables that support it, or even a static integer;
- the `bar()` call is what makes the bar go forward -- you usually call it in every iteration after consuming an item, but you can get creative! Remember the bar is counting for you _independently of the iteration process_, only when you call `bar()` (something no other progress bar have), so you can use it to count anything you want! For example, you could call `bar()` only when you find something expected and then know how many of those there were, including the percentage that it represents! Or call it more than once in the same iteration, no problem at all, you choose what you are monitoring! The ETA will not be that useful unfortunately;
- the `bar()` call returns the current count or percentage.

So, you could even use it without any loops, like for example:

```python
with alive_bar(3) as bar:
    corpus = read_big_file()
    bar('file read, tokenizing')
    tokens = tokenize(corpus)
    bar('tokens ok, processing')
    process(tokens)
    bar()
```


## Modes of operation

Actually, the `total` argument is optional. Providing it makes the bar enter the **definite mode**, the one used for well-bounded tasks. This mode has all statistics widgets `alive-progress` has to offer: counter, throughput and eta.

If you do not provide a `total`, the bar enters the **unknown mode**. In this mode, the whole progress-bar is animated like the cool spinners, as it's not possible to determine the percentage of completion. Therefore, it's also not possible to compute an eta, but you still get the counter and throughput widgets.

> The cool spinner are still present in this mode, so the animations from both bar and spinner runs concurrently and independently of each other, rendering a unique show in your terminal 😜.

Then you have the (📌 new) **manual modes**, where you get to actually control the bar! That way, you can put it in whatever position you want, including make it go backwards or act like a gauge of some sort!
Just pass a `manual=True` argument to `alive_bar()` (or `config_handler.set_global()`), and you get to send a percentage to the very same `bar()` handler! For example to set it at 15%, you would call `bar(0.15)`, which is 15 / 100, as simple as that.
Call it as frequently as you need, the refresh rate will be asynchronously computed as usual, according to current progress and elapsed time.

And please provide the `total` if you have it, to get all the same counter, throughput and eta widgets as the _definite mode_. The counter will be inferred from the supplied user percentage.
<br>If you omit the `total`, it's not possible to infer the counter widget, but you'll still kinda get the throughput and eta widgets, a simpler one with only "%/s" (percent per second) and a rough ETA to get to 100%, which are very inaccurate, but better than nothing.

> Just remember: You do not have to think about which mode you should be using, just always pass a `total` if you know it, and use `manual` if you need it! It will just work! 👏

To summarize it all:

|       mode         |     completion         | counter    | throughput |   eta    | overflow and underflow |
|:---:|:---:|:---:|:---:|:---:|:---:|
|     definite       | ✅ automatic           | ✅          | ✅         | ✅       | ✅ |
|     unknown        | ❌ (an animation runs) | ✅          | ✅         | ❌       | ❌ |
| manual (bounded)   | ✅ you choose          | ✅ inferred | ✅         | ✅       | ✅ |
| manual (unbounded) | ✅ you choose          | ❌          | ⚠️ simpler | ⚠️ rough | ✅ |


### The `bar()` handler

- in **definite and unknown** modes, it accepts an **optional** `int` argument, which increments the counter by any positive number, like `bar(5)` to increment the counter by 5 in one step ➔ relative positioning;
- in **manual** modes, it needs a **mandatory** `float` argument, which overwrites the progress percentage, like `bar(.35)` to put the bar in the 35% position ➔ absolute positioning.
- and it always returns the updated counter/progress value.

> Deprecated: the `bar()` handlers used to also have a `text` parameter which is being removed, more details [here](#displaying-messages).


## Styles

Wondering what styles does it have bundled? It's `showtime`! ;)

![alive-progress spinner styles](https://raw.githubusercontent.com/rsalmei/alive-progress/master/img/showtime-spinners.gif)

Actually I've made these styles just to put to use all combinations of the factories I've created, but I think some of them ended up very very cool! Use them at will, or create your own!

There's also a bars `showtime`, check it out! ;)

![alive-progress bar styles](https://raw.githubusercontent.com/rsalmei/alive-progress/master/img/showtime-bars.gif)

(📌 new) Now there are new commands in exhibition! Try the `show_bars()` and `show_spinners()`!
 
```python
from alive_progress import show_bars, show_spinners
# call them and enjoy the show ;)
```

There's also a (📌 new) utility called `print_chars`, to help finding that cool one to put in your customized spinner or bar, or to determine if your terminal do support unicode chars.


## Displaying messages

While in any alive progress context, you can display messages with:
- the usual Python `print()` statement and `logging` framework, which properly clean the line, print or log an enriched message (including the current bar position) and continues the bar right below it;
- the (📌 new) `bar.text('message')` call, which sets a situational message right within the bar, usually to display something about the items being processed or the phase the processing is in.

> Deprecated: there's still a `bar(text='message')` to update the situational message, but that did not allow you to update it without also changing the bar position, which was inconvenient.
> Now they are separate methods, and the message can be changed whenever you want.
> `DeprecationWarning`s should be displayed to alert you if needed, please update your software to `bar.text('message')`, since this will be removed in the next version.

![alive-progress messages](https://raw.githubusercontent.com/rsalmei/alive-progress/master/img/print-hook.gif)


## Appearance and behavior

There are several options to customize appearance and behavior, most of them usable both locally and globally. But there's a few that only make sense locally, these are:

- `title`: an optional yet always visible title if defined, that represents what is that processing;
- `calibrate`: calibrates the fps engine (more details [here](#advanced))

Those used anywhere are [default values in brackets]:
- `length`: [`40`] number of characters to render the animated progress bar
- `spinner`: the spinner to be used in all renditions
<br>    it's a predefined name in `show_spinners()`, or a custom spinner
- `bar`: bar to be used in definite and both manual modes
<br>    it's a predefined name in `show_bars()`, or a custom bar
- `unknown`: bar to be used in unknown mode (whole bar is a spinner)
<br>    it's a predefined name in `show_spinners()`, or a custom spinner
- `theme`: [`'smooth'`, which sets spinner, bar and unknown] theme name in alive_progress.THEMES
- `force_tty`: [`False`] runs animations even without a tty (more details [here](#advanced))
- `manual`: [`False`] set to manually control percentage
- `enrich_print`: [`True`] includes the bar position in print() and logging messages
- `title_length`: [`0`] fixed title length, or 0 for unlimited

To use them locally just send the option to `alive_bar`:

```python
from alive_progress import alive_bar

with alive_bar(total, title='Title here', length=20, ...):
    ...
```

To use them globally, set them before in `config_handler` object, and any `alive_bar` created after that will also use those options:

```python
from alive_progress import alive_bar, config_handler

config_handler.set_global(length=20, ...)

with alive_bar(total, ...):
    # both sets of options will be active here!
    ...
```

And you can mix and match them, local options always have precedence over global ones!

_Click to see it in motion_
[![alive-progress customization](https://asciinema.org/a/j392MaLz1w0zDw6EVHw4QbLAO.svg)](https://asciinema.org/a/260882)


## Advanced

You should now be completely able to use `alive-progress`, have fun!
<br>If you've appreciated my work and would like me to continue improving it, you could buy me a coffee! I would really appreciate that 😊! Thank you!

And if you want to do even more, exciting stuff lies ahead!

<details>
<summary><strong><em>You want to calibrate the engine?</em></strong></summary>

> ### Calibration (📌 new)
>
> The `alive-progress` bars have a cool visual feedback of the current throughput, so you can instantly **see** how fast your processing is, as the spinner runs faster or slower with it.
> For this to happen, I've put together and implemented a few fps curves to empirically find which one gave the best feel of speed:
>
> ![alive-progress fps curves](https://raw.githubusercontent.com/rsalmei/alive-progress/master/img/alive-bar_fps.png)
> (interactive version [here](https://www.desmos.com/calculator/ema05elsux))
>
> The graph shows the logarithmic (red), parabolic (blue) and linear (green) curves, as well as an adjusted logarithmic curve (dotted orange), with a few twists for small numbers. I've settled with the adjusted logarithmic curve, as it seemed to provide the best all around perceived speed changes. In the future and if someone would find it useful, it could be configurable.
>
> The default `alive-progress` calibration is _1,000,000_ in auto (and manual bounded) modes, ie. it takes 1 million iterations per second for the bar to refresh itself at 60 frames per second. In the manual unbounded mode it is 1.0 (100%). Both enable a vast operating range and generally work well.
>
> Let's say your processing hardly gets to 20 items per second, and you think `alive-progress` is rendering sluggish, you could:
>
> ```python
>     with alive_bar(total, calibrate=20) as bar:
>         ...
> ```
>
> And it will be running waaaay faster...
> <br>Perhaps too fast, consider calibrating to ~50% more, find the one you like the most! :)
>
> ---
</details>

<details>
<summary><strong><em>Perhaps customize it even more?</em></strong></summary>

> ### Create your own animations
>
> Make your own spinners and bars! All of the major components are individually customizable!
>
> There's builtin support for a plethora of special effects, like frames, scrolling, bouncing, delayed and compound spinners! Get creative!
>
> These animations are made by very advanced generators, defined by factories of factory methods: the first level receives and process the styling parameters to create the actual factory; this factory then receives operating parameters like screen length, to build the infinite animation generators.
>
> These generators are capable of several different animation cycles, for example a bouncing ball has a cycle to the right and another to the left. They continually yield the next rendered animation frame in a cycle until it is exhausted. This just enables the next one, but does not start it! That has all kinds of cool implications: the cycles can have different animation sizes, different screen lengths, they do not need to be synchronized, they can create long different sequences by themselves, they can cooperate with each other to play cycles in sequence or simultaneously, and I can display several at once on the screen without any interferences! It's almost like they are _alive_! 😉

> The types I've made are:
> - `frames`: draw any sequence of characters, that will be played frame by frame in sequence;
> - `scrolling`: pick a frame or a sequence of characters and make it flow smoothly from one side to the other, hiding behind or wrapping upon the invisible borders; if using a sequence, generates several cycles of distinct characters;
> - `bouncing`: aggregates two `scrolling` in opposite directions, to make two frames or two sequences of characters flow interleaved from/to each side, hiding or immediately bouncing upon the invisible borders; supports several interleaved cycles too;
> - `delayed`: get any other animation generator, and copy it multiple times, skipping some frames at the start! very cool effects are made here;
> - `compound` get a handful of generators and play them side by side simultaneously! why choose if you can have them all?
>
> A small example (_Click to see it in motion_)
>
> [![alive-progress creative](https://asciinema.org/a/mK9rbzLC1xkMRfRDk5QJMy8xc.svg)](https://asciinema.org/a/260884)
>
> ---
</details>

<details>
<summary><strong><em>Oh you want to stop it altogether!</em></strong></summary>

> ### The Pause mechanism
>
> Why would you want to pause it, I hear? To get to manually act on some items at will, I say!
> <br>Suppose you need to reconcile payment transactions. You need to iterate over thousands of them, detect somehow the faulty ones, and fix them. This fix is not simple nor deterministic, you need to study each one to understand what to do. They could be missing a recipient, or have the wrong amount, or not be synced with the server, etc, it's hard to even imagine all possibilities. Typically you would have to let the detection process run until completion, appending to a list each inconsistency found, and waiting potentially a long time until you can actually start fixing them. You could of course mitigate this by processing in chunks or printing them and acting in another shell, but those have their own shortcomings.
> <br>Now there's a better way, pause the actual detection for a moment! Then you have to wait only until the next one is found, and act in near real time!
>
> To use the pause mechanism, you must be inside a function, which you should already be in your code (in the ipython shell just wrap it inside one). This requires a function to act as a generator and `yield` the objects you want to interact with. The `bar` handler includes a context manager for this, just do `with bar.pause(): yield transaction`.
>
> ```python
> def reconcile_transactions():
>     qs = Transaction.objects.filter()  # django example, or in sqlalchemy: session.query(Transaction).filter()
>     with alive_bar(qs.count()) as bar:
>         for transaction in qs:
>             if not validate(transaction):
>                 with bar.pause():
>                     yield transaction
>             bar()
> ```
>
> That's it! Then you can use it in ipython (or your preferred _REPL_)! Just call the function to instantiate the generator and, whenever you want another transaction, call `next(gen, None)`! The progress bar will run as usual while searching, but as soon as an inconsistency is found, the bar pauses itself and you get the prompt back with a transaction! How cool is that 😃?
>
> ```text
> In [11]: gen = reconcile_transactions()
>
> In [12]: next(gen, None)
> |█████████████████████                   | 105/200 [52%] in 5s (18.8/s, eta: 4s)
> Out[12]: Transaction<#123>
> ```
>
> When you're done, continue the process with the same `next` as before... The bar reappears and continues like nothing happened!! :)
>
> ```text
> In [21]: next(gen, None)
> |█████████████████████                   | ▁▃▅ 106/200 [52%] in 5s (18.8/s, eta: 4s)
> ```
>
> ---
</details>

<details>
<summary><strong><em>Those astonishing animations refuse to display?</em></strong></summary>

> ### Forcing animations on non-interactive consoles (like Pycharm's)
>
> Pycharm's python console for instance do not report itself as "interactive", so I've included a `force_tty` argument to be able to use the alive-progress bar in it.
>
> So, just start it as:
>
> ```python
> with alive_bar(1000, force_tty=True) as bar:
>     for i in range(1000):
>         time.sleep(.01)
>         bar()
> ```
>
> You can also set it system-wide in `config_handler`.
>
> Do note that this console is heavily instrumented and has more overhead, so the outcome may not be as fluid as you would expect.
>
> ---
</details>


## Interesting facts

- This whole project was implemented in functional style;
- It does not declare even a single class;
- It uses extensively (and very creatively) python _Closures_ and _Generators_, they're in almost all modules (look for instance the [spinners factories](https://github.com/rsalmei/alive-progress/blob/master/alive_progress/animations/spinners.py) and [spinner_player](https://github.com/rsalmei/alive-progress/blob/master/alive_progress/animations/utils.py) 😜);
- It does not have any dependencies.


## To do

- improve test coverage, hopefully achieving 100% branch coverage
- variable width bar rendition, listening to changes in terminal size
- enable multiple simultaneous bars, for nested or multiple statuses
- create a contrib system, to allow a simple way to share users' spinners and bars styles
- jupyter notebook support
- support colors in spinners and bars
- any other ideas welcome!

<details>
<summary>Already done.</summary>

> - create an unknown mode for bars (without a known total and eta)
> - implement a pausing mechanism
> - change spinner styles
> - change bar styles
> - include a global configuration system
> - create generators for scrolling, bouncing, delayed and compound spinners
> - create an exhibition of spinners and bars, to see them all in motion
> - include theme support in configuration
> - soft wrapping support
> - hiding cursor support
> - python logging support
> - exponential smoothing of ETA time series
>
> ---
</details>


## Python 2 EOL

The `alive_progress` next major version 2.0 will support Python 3.5+ only. But if you still need support for Python 2, there is a full featured one you can use, just:

```bash
$ pip install -U "alive_progress<2"
```

## Changelog highlights:
- 1.6.0: soft wrapping support; hiding cursor support; python logging support; exponential smoothing of ETA time series; proper always visible bar title; enhanced elapsed time representation; new bar.text() dedicated method (deprecating 'text' parameter in bar()); performance optimizations
- 1.5.1: fix compatibility with python 2.7 (should be the last one, version 2 is in the works, with python 3 support only)
- 1.5.0: standard_bar accepts a background parameter instead of blank, which accepts arbitrarily sized strings and remains fixed in the background, simulating a bar going "over it"
- 1.4.4: restructure internal packages; 100% branch coverage of all animations systems, i.e., bars and spinners
- 1.4.3: protect configuration system against other errors (length='a' for example); first automated tests, 100% branch coverage of configuration system
- 1.4.2: sanitize text input, keeping \n from entering and replicating bar on screen
- 1.4.1: include license file in source distribution
- 1.4.0: print() enrichment can now be disabled (locally and globally), exhibits now have a real time fps indicator, new exhibit functions `show_spinners` and `show_bars`, new utility `print_chars`, `show_bars` gains some advanced demonstrations (try it again!)
- 1.3.3: further improve stream compatibility with isatty
- 1.3.2: beautifully finalize bar in case of unexpected errors
- 1.3.1: fix a subtle race condition that could leave artifacts if ended very fast, flush print buffer when position changes or bar terminates, keep total argument from unexpected types
- 1.3.0: new fps calibration system, support force_tty and manual options in global configuration, multiple increment support in bar handler
- 1.2.0: filled blanks bar styles, clean underflow representation of filled blanks
- 1.1.1: optional percentage in manual mode
- 1.1.0: new manual mode
- 1.0.1: pycharm console support with force_tty, improve compatibility with python stdio streams
- 1.0.0: first public release, already very complete and mature


## License
This software is licensed under the MIT License. See the LICENSE file in the top distribution directory for the full license text.


## Did you like it?

Thank you for your interest!

I've put much ❤️ and effort into this.
<br>If you've appreciated my work and would like me to continue improving it, you could buy me a coffee! I would really appreciate that 😊! (the button is on the top-right corner) Thank you!
