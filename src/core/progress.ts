/**
 * Core progress bar implementation.
 *
 * Provides:
 * - aliveBar(): Async iterator/callback-based progress bar
 * - aliveIt(): Auto-iterating progress wrapper
 */

import type { Bar } from "../animations/bars.js";
import type { Spinner } from "../animations/spinners.js";
import { getStringWidth } from "../utils/cells.js";
import { cursor } from "../utils/colors.js";
import {
  createTerminal,
  type TerminalWriter,
} from "../utils/terminal/index.js";
import {
  ETACalculator,
  formatDuration,
  formatRate,
  Timer,
} from "../utils/timing.js";
import { calculateRefreshInterval, getFixedInterval } from "./calibration.js";
import {
  type AliveBarOptions,
  type ResolvedConfig,
  resolveConfig,
} from "./configuration.js";
import {
  installHooks,
  pauseHooks,
  resumeHooks,
  uninstallHooks,
  updatePosition,
} from "./hook-manager.js";

/**
 * Receipt data returned after progress completion.
 */
export interface Receipt {
  total: number | null;
  count: number;
  percent: number;
  elapsed: number;
  rate: number;
  success: boolean;
  overflow: boolean;
  underflow: boolean;
}

/**
 * Progress bar handler returned by aliveBar.
 */
export interface ProgressBar {
  /** Increment the progress counter */
  (count?: number, options?: { skipped?: boolean }): void;

  /** Current progress count */
  current: number;

  /** Get/set situational message */
  text: string;
  /** Set situational message (method form) */
  setText(text: string): void;

  /** Get/set title */
  title: string;
  /** Set title (method form) */
  setTitle(title: string): void;

  /** Pause processing (returns a function to resume) */
  pause(): () => void;

  /** Elapsed time in seconds */
  elapsed: number;

  /** Monitor widget text */
  monitor: string;

  /** Rate widget text */
  rate: string;

  /** ETA widget text */
  eta: string;

  /** Get receipt data */
  receipt: Receipt | null;
}

/**
 * Internal state for the progress bar.
 */
interface ProgressState {
  config: ResolvedConfig;
  total: number | null;
  current: number;
  text: string;
  title: string;
  terminal: TerminalWriter;
  spinner: Spinner;
  bar: Bar;
  unknownSpinner: Spinner;
  timer: Timer;
  etaCalculator: ETACalculator;
  refreshInterval: NodeJS.Timeout | null;
  isRunning: boolean;
  isPaused: boolean;
  lastFrame: string;
  lastWasDualLine: boolean;
  receipt: Receipt | null;
  skipped: number;
  printBuffer: string[];
}

/**
 * Format a number with optional scaling.
 */
function formatNumber(
  value: number,
  scale: "SI" | "IEC" | "SI2" | null,
  precision: number,
  unit: string
): string {
  if (!scale) {
    const formatted = Number.isInteger(value)
      ? value.toString()
      : value.toFixed(precision);
    return unit ? `${formatted}${unit}` : formatted;
  }

  const scales =
    scale === "IEC"
      ? { factor: 1024, suffixes: ["", "Ki", "Mi", "Gi", "Ti", "Pi"] }
      : { factor: 1000, suffixes: ["", "k", "M", "G", "T", "P"] };

  let scaled = value;
  let suffixIndex = 0;

  while (scaled >= scales.factor && suffixIndex < scales.suffixes.length - 1) {
    scaled /= scales.factor;
    suffixIndex++;
  }

  const formatted = scaled.toFixed(precision);
  return `${formatted}${scales.suffixes[suffixIndex]}${unit}`;
}

/**
 * Build the widgets part of the display.
 */
function buildWidgets(state: ProgressState): string {
  const { config, total, current, timer, etaCalculator, skipped } = state;
  const parts: string[] = [];

  // Monitor widget: count/total [percent]
  if (config.monitor) {
    const actualCurrent = current - skipped;
    const percent = total ? Math.min(100, (actualCurrent / total) * 100) : 0;

    if (typeof config.monitor === "string") {
      // Custom format
      let format = config.monitor;
      format = format.replace(
        "{count}",
        formatNumber(actualCurrent, config.scale, config.precision, config.unit)
      );
      format = format.replace(
        "{total}",
        total
          ? formatNumber(total, config.scale, config.precision, config.unit)
          : "?"
      );
      format = format.replace("{percent}", `${percent.toFixed(0)}%`);
      parts.push(format);
    } else {
      // Default format
      const countStr = formatNumber(
        actualCurrent,
        config.scale,
        config.precision,
        config.unit
      );
      const totalStr = total
        ? formatNumber(total, config.scale, config.precision, config.unit)
        : "?";
      parts.push(`${countStr}/${totalStr} [${percent.toFixed(0)}%]`);
    }
  }

  // Elapsed widget
  if (config.elapsed) {
    const elapsed = timer.elapsed();
    if (typeof config.elapsed === "string") {
      parts.push(config.elapsed.replace("{elapsed}", formatDuration(elapsed)));
    } else {
      parts.push(`in ${formatDuration(elapsed)}`);
    }
  }

  // Stats widget: rate and ETA
  if (config.stats && total) {
    const rate = etaCalculator.getRate();
    const eta = total
      ? etaCalculator.update(current - skipped, total)
      : Number.POSITIVE_INFINITY;

    if (typeof config.stats === "string") {
      let format = config.stats;
      format = format.replace("{rate}", formatRate(rate, config.unit));
      format = format.replace(
        "{eta}",
        Number.isFinite(eta) ? formatDuration(eta, true) : "?"
      );
      parts.push(format);
    } else {
      const rateStr = formatRate(rate, config.unit);
      const etaStr = Number.isFinite(eta)
        ? `eta: ${formatDuration(eta, true)}`
        : "";
      parts.push(`(${rateStr}${etaStr ? `, ${etaStr}` : ""})`);
    }
  }

  return parts.join(" ");
}

/**
 * Render a single frame of the progress bar.
 */
function renderFrame(state: ProgressState): string {
  const {
    config,
    total,
    current,
    text,
    title,
    spinner,
    bar,
    unknownSpinner,
    skipped,
  } = state;
  const parts: string[] = [];

  // Title
  if (title) {
    parts.push(title);
  }

  // Determine mode and render bar/spinner
  const termWidth = state.terminal.getWidth();
  const actualCurrent = current - skipped;
  const percent = total ? Math.min(1, actualCurrent / total) : 0;
  const overflow = total ? actualCurrent > total : false;
  const underflow = false; // Will be set at completion

  if (total !== null) {
    // Determinate mode: show progress bar
    const barFrame = bar(percent, overflow, underflow);
    parts.push(barFrame.content);

    // Show spinner alongside when in progress
    if (percent < 1 && !overflow) {
      const spinnerFrame = spinner();
      parts.push(spinnerFrame.content);
    }
  } else {
    // Indeterminate mode: show spinner only
    const spinnerFrame = unknownSpinner();
    parts.push(spinnerFrame.content);
  }

  // Widgets
  const widgets = buildWidgets(state);
  if (widgets) {
    parts.push(widgets);
  }

  // Situational text
  if (text && !config.dualLine) {
    parts.push(text);
  }

  let line = parts.join(" ");

  // Truncate if too long
  const lineWidth = getStringWidth(line);
  if (lineWidth > termWidth) {
    line = `${line.slice(0, termWidth - 3)}...`;
  }

  // Dual line mode
  if (config.dualLine && text) {
    line += `\n${text}`;
  }

  return line;
}

/**
 * Print a line while preserving the progress bar.
 */
function printLine(state: ProgressState, text: string): void {
  if (!state.isRunning) {
    return;
  }

  pauseHooks();

  // Clear current line(s), print the text, then redraw the bar
  if (state.lastWasDualLine) {
    state.terminal.write(cursor.up(1));
    state.terminal.clearLine();
    state.terminal.write(cursor.down(1));
    state.terminal.clearLine();
    state.terminal.write(cursor.up(1));
  } else {
    state.terminal.clearLine();
  }

  state.terminal.writeLine(text);

  // Redraw the bar
  if (state.lastFrame) {
    state.terminal.write(state.lastFrame);
  }

  resumeHooks();
}

/**
 * Update the display.
 */
function updateDisplay(state: ProgressState): void {
  if (!state.isRunning || state.isPaused) {
    return;
  }

  pauseHooks();

  const frame = renderFrame(state);
  const isDualLine = state.config.dualLine && state.text !== "";

  // If previous frame was dual-line, we need to clear both lines
  if (state.lastWasDualLine) {
    // Move up to the first line, clear it
    state.terminal.write(cursor.up(1));
    state.terminal.clearLine();
    // Move down and clear the second line
    state.terminal.write(cursor.down(1));
    state.terminal.clearLine();
    // Move back up to write from the first line
    state.terminal.write(cursor.up(1));
  } else {
    state.terminal.clearLine();
  }

  state.terminal.write(frame);
  state.lastFrame = frame;
  state.lastWasDualLine = isDualLine;

  resumeHooks();
}

/**
 * Start the refresh loop.
 */
function startRefreshLoop(state: ProgressState): void {
  const fixedInterval = getFixedInterval(state.config.refreshSecs);

  const refresh = () => {
    if (!state.isRunning || state.isPaused) {
      return;
    }

    updateDisplay(state);

    // Calculate next interval based on current rate
    const rate = state.etaCalculator.getRate();
    const interval =
      fixedInterval ?? calculateRefreshInterval(rate, state.config.calibrate);

    state.refreshInterval = setTimeout(refresh, interval);
  };

  // Start immediately
  const initialInterval = fixedInterval ?? 50;
  state.refreshInterval = setTimeout(refresh, initialInterval);
}

/**
 * Stop the refresh loop.
 */
function stopRefreshLoop(state: ProgressState): void {
  if (state.refreshInterval) {
    clearTimeout(state.refreshInterval);
    state.refreshInterval = null;
  }
}

/**
 * Finalize the progress bar.
 */
function finalize(state: ProgressState): void {
  state.isRunning = false;
  stopRefreshLoop(state);
  uninstallHooks();

  // Calculate final stats
  const actualCurrent = state.current - state.skipped;
  const overflow = state.total !== null && actualCurrent > state.total;
  const underflow = state.total !== null && actualCurrent < state.total;
  const success = !(overflow || underflow);
  const elapsed = state.timer.elapsed();
  const rate = elapsed > 0 ? actualCurrent / elapsed : 0;

  state.receipt = {
    total: state.total,
    count: actualCurrent,
    percent: state.total ? (actualCurrent / state.total) * 100 : 100,
    elapsed,
    rate,
    success,
    overflow,
    underflow,
  };

  // Show final receipt
  if (state.config.receipt) {
    pauseHooks();

    // Build receipt line
    const parts: string[] = [];

    if (state.title) {
      parts.push(state.title);
    }

    // Final bar at 100% (or with overflow indicator)
    const barFrame = state.bar(overflow ? 1.1 : 1, overflow, underflow);
    parts.push(barFrame.content);

    // Final stats
    const countStr = formatNumber(
      actualCurrent,
      state.config.scale,
      state.config.precision,
      state.config.unit
    );
    const totalStr = state.total
      ? formatNumber(
          state.total,
          state.config.scale,
          state.config.precision,
          state.config.unit
        )
      : "?";
    const percentStr = state.total
      ? `${Math.round((actualCurrent / state.total) * 100)}%`
      : "100%";
    parts.push(`${countStr}/${totalStr} [${percentStr}]`);

    // Elapsed
    parts.push(`in ${formatDuration(elapsed)}`);

    // Rate
    parts.push(`(${formatRate(rate, state.config.unit)})`);

    // Success/failure indicator
    if (overflow) {
      parts.push("✗");
    } else if (underflow) {
      parts.push("⚠");
    } else {
      parts.push("✓");
    }

    // Optional text
    if (state.config.receiptText && state.text) {
      parts.push(state.text);
    }

    // Clear dual-line if necessary
    if (state.lastWasDualLine) {
      state.terminal.write(cursor.up(1));
      state.terminal.clearLine();
      state.terminal.write(cursor.down(1));
      state.terminal.clearLine();
      state.terminal.write(cursor.up(1));
    } else {
      state.terminal.clearLine();
    }

    state.terminal.writeLine(parts.join(" "));
    state.terminal.showCursor();

    resumeHooks();
  } else {
    // Clear dual-line if necessary
    if (state.lastWasDualLine) {
      state.terminal.write(cursor.up(1));
      state.terminal.clearLine();
      state.terminal.write(cursor.down(1));
      state.terminal.clearLine();
      state.terminal.write(cursor.up(1));
    } else {
      state.terminal.clearLine();
    }
    state.terminal.showCursor();
  }
}

/**
 * Create a progress bar.
 *
 * @example
 * // Basic usage with callback
 * const done = await aliveBar(100, async (bar) => {
 *   for (let i = 0; i < 100; i++) {
 *     await doWork();
 *     bar();
 *   }
 * });
 *
 * @example
 * // Manual control
 * const { bar, done } = aliveBar(100);
 * for (let i = 0; i < 100; i++) {
 *   await doWork();
 *   bar();
 * }
 * done();
 */
export function aliveBar(
  total: number | null = null,
  options: AliveBarOptions = {}
): { bar: ProgressBar; done: () => Receipt } {
  const config = resolveConfig(options);

  const state: ProgressState = {
    config,
    total,
    current: 0,
    text: "",
    title: config.title,
    terminal: createTerminal({
      stream: config.file,
      forceTty: config.forceTty,
      disable: config.disable,
    }),
    spinner: config.spinner(config.length),
    bar: config.bar(config.length),
    unknownSpinner: config.unknown(config.length),
    timer: new Timer(),
    etaCalculator: new ETACalculator(config.etaAlpha),
    refreshInterval: null,
    isRunning: true,
    isPaused: false,
    lastFrame: "",
    lastWasDualLine: false,
    receipt: null,
    skipped: 0,
    printBuffer: [],
  };

  // Install hooks for console interception
  if (config.enrichPrint && state.terminal.isInteractive()) {
    installHooks({
      enrichPrint: config.enrichPrint,
      enrichOffset: config.enrichOffset,
      printFn: (text: string) => printLine(state, text),
    });
  }

  // Hide cursor and start refresh
  state.terminal.hideCursor();
  updateDisplay(state);
  startRefreshLoop(state);

  // Setup Ctrl+C handler
  let sigintHandler: (() => void) | null = null;
  if (config.ctrlC) {
    sigintHandler = () => {
      finalize(state);
      process.exit(130);
    };
    process.on("SIGINT", sigintHandler);
  }

  // Create the progress bar handler as a callable function with properties
  const barFn = (count = 1, opts: { skipped?: boolean } = {}) => {
    if (!state.isRunning) {
      return;
    }

    if (opts.skipped) {
      state.skipped += count;
    }

    if (config.manual) {
      // Manual mode: count is the percentage (0-1)
      state.current = count * (state.total || 100);
    } else {
      state.current += count;
    }

    updatePosition(state.current);
  };

  // Define properties on the function using Object.defineProperties
  Object.defineProperties(barFn, {
    current: {
      get() {
        return state.current - state.skipped;
      },
      enumerable: true,
    },
    text: {
      get() {
        return state.text;
      },
      set(value: string) {
        state.text = value;
      },
      enumerable: true,
    },
    title: {
      get() {
        return state.title;
      },
      set(value: string) {
        state.title = value;
      },
      enumerable: true,
    },
    elapsed: {
      get() {
        return state.timer.elapsed();
      },
      enumerable: true,
    },
    monitor: {
      get() {
        const actualCurrent = state.current - state.skipped;
        const percent = state.total
          ? Math.min(100, (actualCurrent / state.total) * 100)
          : 0;
        const countStr = formatNumber(
          actualCurrent,
          config.scale,
          config.precision,
          config.unit
        );
        const totalStr = state.total
          ? formatNumber(
              state.total,
              config.scale,
              config.precision,
              config.unit
            )
          : "?";
        return `${countStr}/${totalStr} [${percent.toFixed(0)}%]`;
      },
      enumerable: true,
    },
    rate: {
      get() {
        return formatRate(state.etaCalculator.getRate(), config.unit);
      },
      enumerable: true,
    },
    eta: {
      get() {
        const actualCurrent = state.current - state.skipped;
        if (!state.total) {
          return "?";
        }
        const eta = state.etaCalculator.update(actualCurrent, state.total);
        return Number.isFinite(eta) ? formatDuration(eta, true) : "?";
      },
      enumerable: true,
    },
    receipt: {
      get() {
        return state.receipt;
      },
      enumerable: true,
    },
    setText: {
      value(value: string) {
        state.text = value;
      },
      enumerable: true,
    },
    setTitle: {
      value(value: string) {
        state.title = value;
      },
      enumerable: true,
    },
    pause: {
      value() {
        state.isPaused = true;
        state.timer.pause();

        // Clear dual-line if necessary
        if (state.lastWasDualLine) {
          state.terminal.write(cursor.up(1));
          state.terminal.clearLine();
          state.terminal.write(cursor.down(1));
          state.terminal.clearLine();
          state.terminal.write(cursor.up(1));
        } else {
          state.terminal.clearLine();
        }
        state.terminal.showCursor();

        return () => {
          state.isPaused = false;
          state.timer.resume();
          state.terminal.hideCursor();
          updateDisplay(state);
        };
      },
      enumerable: true,
    },
  });

  const bar = barFn as ProgressBar;

  const done = (): Receipt => {
    if (sigintHandler) {
      process.off("SIGINT", sigintHandler);
    }
    finalize(state);
    // Receipt is guaranteed to be set after finalize()
    return state.receipt as Receipt;
  };

  return { bar, done };
}

/**
 * Create an auto-iterating progress bar.
 *
 * @example
 * for await (const item of aliveIt(items)) {
 *   await processItem(item);
 * }
 *
 * @example
 * // With options
 * for await (const item of aliveIt(items, { title: 'Processing' })) {
 *   await processItem(item);
 * }
 */
export async function* aliveIt<T>(
  iterable: Iterable<T> | AsyncIterable<T>,
  options: AliveBarOptions = {}
): AsyncGenerator<T, void, unknown> {
  // Get total if possible
  let total: number | null = null;
  if (Array.isArray(iterable)) {
    total = iterable.length;
  } else if (
    "length" in iterable &&
    typeof (iterable as { length: number }).length === "number"
  ) {
    total = (iterable as { length: number }).length;
  } else if (
    "size" in iterable &&
    typeof (iterable as { size: number }).size === "number"
  ) {
    total = (iterable as { size: number }).size;
  }

  const { bar, done } = aliveBar(total, options);

  try {
    if (Symbol.asyncIterator in iterable) {
      for await (const item of iterable as AsyncIterable<T>) {
        yield item;
        bar();
      }
    } else {
      for (const item of iterable as Iterable<T>) {
        yield item;
        bar();
      }
    }
  } finally {
    done();
  }
}

/**
 * Synchronous version of aliveIt for sync iterables.
 */
export function* aliveItSync<T>(
  iterable: Iterable<T>,
  options: AliveBarOptions = {}
): Generator<T, void, unknown> {
  // Get total if possible
  let total: number | null = null;
  if (Array.isArray(iterable)) {
    total = iterable.length;
  } else if (
    "length" in iterable &&
    typeof (iterable as { length: number }).length === "number"
  ) {
    total = (iterable as { length: number }).length;
  } else if (
    "size" in iterable &&
    typeof (iterable as { size: number }).size === "number"
  ) {
    total = (iterable as { size: number }).size;
  }

  const { bar, done } = aliveBar(total, options);

  try {
    for (const item of iterable) {
      yield item;
      bar();
    }
  } finally {
    done();
  }
}
