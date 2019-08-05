[![PyPI version](https://img.shields.io/pypi/v/alive-progress.svg)](https://pypi.python.org/pypi/alive-progress/)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/alive-progress.svg)](https://pypi.python.org/pypi/alive-progress/)
[![PyPI status](https://img.shields.io/pypi/status/alive-progress.svg)](https://pypi.python.org/pypi/alive-progress/)

# alive-progress :)
## An animated and smart Progress Bar for python!

Ever found yourself in a remote ssh session, doing some lengthy operations, and every now and then you feel the need to hit [enter] just to ensure you didn't lose the connection? Ever wondered where your processing is in, and when will it finish? Ever needed to *pause* the progress bar for a while, return to the python REPL for a manual inspection or fixing an item, and then *resume* the process like it never happened? I did...

I've made this thinking about all that, the Alive-Progress bar! :)

[![asciicast](https://asciinema.org/a/eOxk1RqJd0AlSNONgoAtR0CLz.svg)](https://asciinema.org/a/eOxk1RqJd0AlSNONgoAtR0CLz)

I like to think of it as a new kind of progress bar for python, as it has among other things:
  - a cool live spinner, which makes it clear the process did not hang and your terminal/connection is healthy;
  - a visual feedback of the current speed/throughput, as the spinner runs faster or slower according to the actual processing speed;
  - an efficient multi-threaded bar, which updates itself at a fraction of the actual speed (1,000,000 iterations per second equates to roughly 60fps refresh rate) to keep CPU usage low and avoid terminal spamming;
  - an expected time of arrival (eta), that shows the remaining processing time in a friendly way, not anything like `eta: 1584s`, it will nicely show `eta: 0:26:24` as you would expect (but anything less than a minute is indeed `eta: 42s`;
  - a `print()` hook, which allows print statements in the midst of an alive-bar context, nicely cleaning the output of any garbage, and even enriching with the current count when it occurred;
  - after your processing has finished, a nice receipt is printed with the statistics of that run, including the elapsed time and observed throughput;
  - it tracks the actual count in regard of the expected count, so it will look different if you send in more or less than expected;
  - it automatically detects if there's really an allocated tty, and if there isn't, only the final receipt is printed, so you can safely include the alive-bar in all and any code and rest assure your log file won't get 60fps garbage;
  - you can pause the alive-bar! I think that's an unprecedented feature for a progress-bar, it's incredible to orchestrate operations that request manual interaction on some items;
  - it is customizable, with a growing smorgasbord of different bar and spinner styles, as well as several factories to easily generate yours!

Wondering what styles does it have bundled? It's `showtime`! ;)

[![asciicast](https://asciinema.org/a/OR83rcm8J06w0OC9pkgnaJmYG.svg)](https://asciinema.org/a/OR83rcm8J06w0OC9pkgnaJmYG)

I've made these styles to test all combinations of parameters of the factories, but I think some of them ended up very very cool! Use them, or create your own.


## Get it

Just install with pip:

```bash
$ pip install alive-progress
```


## How to use

Use it in a `with` context manager like this:

```python
from alive_progress import alive_bar
qs = <query or iterable>            # usually some queryset or iterable
with alive_bar(qs.count()) as bar:  # or `len(iterable)`: declare your expected total
    for item in qs:                 # iterate over your items
        # process an item
        bar()                       # call after consuming one item
```

The `bar()` call is what makes the bar go forward. You usually call it after consuming an item and in every iteration, but you can get creative! Call it only when you find something for example, depending on what you want to monitor.
It returns the current count if you'd like to know where you are.


### Messages

While in an alive progress bar context, you have two ways to output messages:
  - calling `bar('message')`, which besides incrementing the counter, also sets/overwrites an inline message within the bar line;
  - calling `print('message')`, which prints an enriched message that includes the current position of the alive bar, thus leaving behind a log and continuing the bar below it.
Both methods always clear the line appropriately to remove any garbage of previous messages on screen.

[![asciicast](https://asciinema.org/a/lDM5zGPvPWFHHZOw0DMAMMH5F.svg)](https://asciinema.org/a/lDM5zGPvPWFHHZOw0DMAMMH5F)


### Customization

All of the components are individually customizable, both globally and per use!
And you can mix and match them.

[![asciicast](https://asciinema.org/a/j392MaLz1w0zDw6EVHw4QbLAO.svg)](https://asciinema.org/a/j392MaLz1w0zDw6EVHw4QbLAO)

#### Advanced

Make your own spinners and bars!
There's builtin support for frames, scrolling, bouncing, delayed and compound spinners! Be creative!

[![asciicast](https://asciinema.org/a/mK9rbzLC1xkMRfRDk5QJMy8xc.svg)](https://asciinema.org/a/mK9rbzLC1xkMRfRDk5QJMy8xc)


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
- try some adaptive algorithm for ETA, like moving average or exponential smoothing
- any other ideas welcome!


## Changelog highlights:
- 1.0: first public release, already very complete and mature


## License
This software is licensed under the MIT License. See the LICENSE file in the top distribution directory for the full license text.


## Did you like it?

Thank you for your interest!
I've put much ❤️ and effort into this.
Hope you'll like it.
