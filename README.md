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

I've made this cool progress bar thinking about all that, the Alive-Progress bar! :)

![alive-progress](https://raw.githubusercontent.com/rsalmei/alive-progress/master/img/alive-demo.gif)


I like to think of it as a new kind of progress bar for python, as it has among other things:

  - a **cool live spinner**, which makes it clear the process did not hang and your terminal/connection is healthy;
  - a **visual feedback** of the current speed/throughput, as the spinner runs faster or slower according to the actual processing speed;
  - an **efficient** multi-threaded bar, which updates itself at a fraction of the actual speed (1,000,000 iterations per second equates to roughly 60fps refresh rate) to keep CPU usage low and avoid terminal spamming; (📌 new: you can now calibrate this!)
  - an expected time of arrival (**ETA**), that shows the remaining processing time in a friendly way, not anything like `eta: 1584s`, it will nicely show `eta: 0:26:24` as you would expect (but anything less than a minute is indeed `eta: 42s`);
  - a `print()` hook, which allows print statements in the midst of an alive-bar context **without any hassle**, automatically cleaning the screen, and even enriching with the current position when it occurred;
  - after your processing has finished, a **nice receipt** is printed with the statistics of that run, including the elapsed time and observed throughput;
  - it tracks the actual count to detect **under and overflows**, so it will look different if you send in less or more than expected;
  - it automatically detects if there's an **allocated tty**, and if there isn't, only the final receipt is printed, so you can safely include the alive-bar in any code, and rest assure your log file won't get 60fps progress lines;
  - you can **pause** the alive-bar! I think that's an unprecedented feature for a progress bar! It's incredible to be able to manually operate on some items while inside a running progress bar context, and get the bar back like it had never stopped whenever you want;
  - it is **customizable**, with a growing smorgasbord of different bar and spinner styles, as well as several factories to easily generate yours!


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
- the `bar()` call is what makes the bar go forward -- you usually call it in every iteration after consuming an item, but you can get creative! For example you could call it only when you find something you want, or call it more than once in the same iteration, depending on what you want to monitor. Just adjust the total accordingly to get a useful eta;
- the `bar()` call also returns the current count/percentage if needed, and enables to pass situational messages to the bar.

So, you could even use it without any loops, like:

```python
with alive_bar(3) as bar:
    corpus = read_big_file()
    bar('file read, tokenizing')
    tokens = tokenize(corpus)
    bar('tokens ok, processing')
    process(tokens)
    bar()
```


## Alive-Bar modes

Actually, the `total` argument is optional. Providing it makes the bar enter the **definite mode**, the one used for well-bounded tasks. This mode has all statistics widgets the alive-bar has to offer: counter, throughput and eta.

If you do not provide a `total`, the bar enters the **unknown mode**. In this mode, the whole progress-bar is animated like the cool spinners, as it's not possible to determine the percentage of completion. Therefore it's also not possible to compute an eta, but you still get the counter and throughput widgets. And the cool spinners are still present in this mode, so each animation runs independently of each other, rendering a unique show in your terminal 😜.

Then you have the (📌 new) **manual mode**, where you get to actually control the bar! That way, you can put it in whatever position you want, like make it go backwards, or act like a gauge of some sort!
Just pass a `manual=True` argument to `alive_bar()` (or `config_handler.set_global()`), and you get to send a percentage to the very same `bar()` handler to put the alive-bar where you want! For example to send 15%, you would call `bar(0.15)` (which is 15 / 100).
Call it as frequently as you need, the refresh rate will be asynchronously computed according to the progress and the elapsed time, not the update rate.

And of course, in this mode you can also provide the `total`, and get all the same counter, throughput and eta statistics widgets as the _definite mode_. The counter is inferred from the supplied percentage.
If you omit the `total`, it's not possible to infer neither the counter nor the throughput widgets, and you get a simpler "percent/second" (%/s) and a rough eta, calculated to get to 100%.

> Just remember: You do not have to think about which mode you should be using, just always pass a `total` if you know it, and use `manual` if you need it! It will just work! 👏

To summarize it all:

| mode | positioning | counter | throughput | eta | overflow and underflow |
|:---:|:---:|:---:|:---:|:---:|:---:|
| definite (with total)   | ✅ automatic  | ✅          | ✅           | ✅ | ✅ |
| unknown (without total) | ❌            | ✅          | ✅           | ❌ | ❌ |
| manual (with total)     | ✅ you choose | ✅ inferred | ✅           | ✅ | ✅ |
| manual (without total)  | ✅ you choose | ❌          | ⚠️ simpler | ⚠️ rough | ✅ |


### Signatures of the `bar()` handler

- in **definite and unknown** modes: `bar(text=None, incr=1)` ➔ increases the current count (by any positive increment), optionally setting the situational text message, and returns the new count;
- in **manual** modes: `bar(perc=None, text=None)` ➔ sets the new progress percentage, optionally setting the situational text message, and returns the new percentage.


## Styles

Wondering what styles does it have bundled? It's `showtime`! ;)

![alive-progress spinner styles](https://raw.githubusercontent.com/rsalmei/alive-progress/master/img/showtime-spinners.gif)

Actually I've made these styles just to put to use all combinations of the factories I've created, but I think some of them ended up very very cool! Use them at will, or create your own!

There's also a bars `showtime`, check it out! ;)

![alive-progress bar styles](https://raw.githubusercontent.com/rsalmei/alive-progress/master/img/showtime-bars.gif)

(📌 new) Now there's new commands in exhibition! Try the `show_bars()` and `show_spinners()`! Just:
 
```python
from alive_progress import show_bars, show_spinners
# call them!
```

Enjoy ;)

There's also a new utility called `print_chars`, to help finding that cool one to put in your customized spinner or bar, or to determine if your terminal support unicode chars.


## Printing messages

While in an alive progress bar context, you have two ways to output messages:
  - calling `bar(text='message')`, which sets/overwrites a situational message within the bar line, usually to display something about the items being processed, or the phase the processing is in;
  - calling the usual Python `print()` statement, which will print an enriched message that includes the current position of the alive bar, thus leaving behind a cool log and continuing the bar below it.

Both methods work the same in all modes, and always clear the line appropriately to remove any garbage on screen.

![alive-progress messages](https://raw.githubusercontent.com/rsalmei/alive-progress/master/img/print-hook.gif)


## Configuration

There are several options to customize behavior, both globally and per use! Just use the `config_handler` object!

```python
from alive_progress import config_handler
config_handler.set_global(...)
```

The options are:
- `length`: number of characters to render the animated progress bar
- `spinner`: spinner name in alive_progress.SPINNERS or custom
- `bar`: bar name in alive_progress.BARS or custom
- `unknown`: spinner name in alive_progress.SPINNERS or custom
- `theme`: theme name in alive_progress.THEMES
- `force_tty`: runs animations even without a tty (pycharm terminal for example)
- `manual`: set to manually control percentage
- `enrich_print`: enabled by default, unset to remove the bar position from print() messages

And you can mix and match them, global and local! (_Click to see it in motion_)

[![alive-progress customization](https://asciinema.org/a/j392MaLz1w0zDw6EVHw4QbLAO.svg)](https://asciinema.org/a/260882)


## Advanced

### Calibration (📌 new)

The Alive-Bar has a cool visual feedback of the current throughput, so you can instantly see how fast your processing is, as the spinner runs faster or slower with it.
For this to happen, I've put together and implemented a few fps curves to empirically find which one gave the best feel of speed:

![alive-bar fps curves](https://raw.githubusercontent.com/rsalmei/alive-progress/master/img/alive-bar_fps.png)
(interactive version [here](https://www.desmos.com/calculator/ema05elsux))

The graph shows the logarithmic (red), parabolic (blue) and linear (green) curves, as well as an adjusted logarithmic curve (dotted orange), with a few twists for small numbers. I've settled with the adjusted logarithmic curve, as it seemed to provide the best all around perceived speed changes.

The default Alive-Bar calibrations are _1,000,000_ in auto (and manual definite) modes and 1 (100%) in manual unknown mode. Both enable a vast operating range and generally work well.

But let's say your processing hardly gets to 20 items per second, and you think the Alive-Bar is rendering sluggish, you can:

```python
    with alive_bar(total, calibrate=20) as bar:
        ...
``` 

And it will be running waaaay faster... :)
Adjust the calibration to your liking!


### Create your own animations

Make your own spinners and bars! All of the major components are individually customizable!

There's builtin support for a plethora of special effects, like frames, scrolling, bouncing, delayed and compound spinners! Get creative!

These animations are made by very advanced generators, defined by factories of factory methods: the first level receives and process the styling parameters to create the actual factory; this factory then receives operating parameters like screen length, to build the infinite animation generators.

These generators are capable of several different animation cycles, for example a bouncing ball has a cycle to the right and another to the left. They continually yield the next rendered animation frame in a cycle until it is exhausted. This just enables the next one, but does not start it! That has all kinds of cool implications: the cycles can have different animation sizes, different screen lengths, they do not need to be synchronized, they can create long different sequences by themselves, they can cooperate with each other to play cycles in sequence or simultaneously, and I can display several at once on the screen without any interferences! It's almost like they are _alive_! 😉

The types I've made are:
- `frames`: draw any sequence of characters, that will be played frame by frame in sequence;
- `scrolling`: pick a frame or a sequence of characters and make it flow smoothly from one side to the other, hiding behind or wrapping upon the invisible borders; if using a sequence, generates several cycles of distinct characters;
- `bouncing`: aggregates two `scrolling` in opposite directions, to make two frames or two sequences of characters flow interleaved from/to each side, hiding or immediately bouncing upon the invisible borders; supports several interleaved cycles too;
- `delayed`: get any other animation generator, and copy it multiple times, skipping some frames at the start! very cool effects are made here;
- `compound` get a handful of generators and play them side by side simultaneously! why choose if you can have them all?

A small example (_Click to see it in motion_)

[![alive-progress creative](https://asciinema.org/a/mK9rbzLC1xkMRfRDk5QJMy8xc.svg)](https://asciinema.org/a/260884)


### The Pause mechanism

To use the pause mechanism, you must wrap the alive-bar inside a function generator to yield the objects you want to interact with. The `bar` handler includes another context manager to yield anything you want, just do `with bar.pause(): yield obj`.

Suppose you need to reconcile transactions. You need to iterate over thousands of them, detect somehow the faulty ones, and fix them. They could be broken or not synced or invalid or anything else, several different problems. Typically you would have to let the process run, appending to a list each inconsistency found, and waiting, potentially a long time, until the end to be able to do anything. You could mitigate this by processing in chunks, but that has its own shortcomings.

With the Alive-Progress bar and the Pause mechanism, you can inspect these transactions in **real-time**! You wait only until the next one is found! To use it you would do something like this:

```python
def reconcile_transactions():
    qs = Transaction.objects.filter()  # django example, or in sqlalchemy: session.query(Transaction).filter()
    with alive_bar(qs.count()) as bar:
        for transaction in qs:
            if not validate(transaction):
                with bar.pause():
                    yield transaction
            bar()
```

That's it! Then you could use it in ipython (or your preferred _REPL_)! Just call the function to instantiate the generator and `next()` with it. The progress bar will run as usual, but as soon as an inconsistency is found, the bar pauses itself and you get the prompt back! 😃

```text
In [11]: gen = reconcile_transactions()

In [12]: next(gen, None)
|█████████████████████                   | 105/200 [52%] in 5s (18.8/s, eta: 4s)
Out[12]: Transaction<#123>
```

How cool is that?! You have the transaction to debug and fix any way you want, and when you're done, continue the process with the same `next` as before... The bar returns like nothing happened!! :)

```text
In [21]: next(gen, None)
|█████████████████████                   | ▁▃▅ 105/200 [52%] in 5s (18.8/s, eta: 4s)
```


### Forcing animations on non-interactive consoles (like Pycharm's)

Pycharm's python console for instance do not report itself as "interactive", so I've included a `force_tty` argument to be able to use the alive-progress bar in it.

So, just start it as:

```python
with alive_bar(1000, force_tty=True) as bar:
    for i in range(1000):
        time.sleep(.01)
        bar()
```

You can also set it system-wide in `config_handler`.

Do note that this console is heavily instrumented and has more overhead, so the outcome may not be as fluid as you would expect.


## To do

- ~~create an unknown mode for bars (without a known total and eta)~~
- ~~implement a pausing mechanism~~
- ~~change spinner styles~~
- ~~change bar styles~~
- ~~include a global configuration system~~
- ~~create generators for scrolling, bouncing, delayed and compound spinners~~
- ~~create an exhibition of spinners and bars, to see them all in motion~~
- ~~include theme support in configuration~~
- include colors in spinners and bars
- try some adaptive algorithm for ETA, like moving average, exponential smoothing or Kalman Filter
- any other ideas welcome!


## Interesting facts

- This whole project was implemented in functional style;
- It does not declare even a single class;
- It uses extensively (and very creatively) python _Closures_ and _Generators_, they're in almost all modules (look for instance the [spinners factories and spinner_player](https://github.com/rsalmei/alive-progress/blob/master/alive_progress/spinners.py) 😜);
- It does not have any dependencies.


## Python 2 EOL

The versions 1.4.x are the last ones to support Python 2. Just implementing unit tests, that are long overdue.


## Changelog highlights:
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
<br>If you appreciate my work you can sponsor me, buy me a coffee! The button is on the top right of the page (the big orange one, it's hard to miss 😊)
