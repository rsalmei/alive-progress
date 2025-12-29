/**
 * Configuration system for alive-progress.
 *
 * Supports global defaults and per-bar overrides.
 */

import type { BarFactory } from "../animations/bars.js";
import type { SpinnerFactory } from "../animations/spinners.js";
import {
  getBar,
  getSpinner,
  getTheme,
  type Theme,
} from "../styles/internal.js";

/**
 * All configurable options for the progress bar.
 */
export interface AliveBarOptions {
  // Display
  /** Total width of the progress bar in characters */
  length?: number;
  /** Spinner style (name or factory) */
  spinner?: string | SpinnerFactory;
  /** Bar style (name or factory) */
  bar?: string | BarFactory;
  /** Unknown mode spinner (for indeterminate progress) */
  unknown?: string | SpinnerFactory;
  /** Theme name (sets spinner, bar, and unknown) */
  theme?: string;
  /** Title displayed before the bar */
  title?: string;

  // Output
  /** Output stream */
  file?: NodeJS.WriteStream;
  /** Force TTY mode (true/false) or auto-detect (null) */
  forceTty?: boolean | null;
  /** Disable all output */
  disable?: boolean;

  // Widgets
  /** Show progress monitor (count/total [percent]) */
  monitor?: boolean | string;
  /** Show elapsed time */
  elapsed?: boolean | string;
  /** Show rate and ETA */
  stats?: boolean | string;
  /** Show final receipt */
  receipt?: boolean;
  /** Include last message in receipt */
  receiptText?: boolean;

  // Behavior
  /** Manual mode (set percentage directly) */
  manual?: boolean;
  /** Allow Ctrl+C to interrupt */
  ctrlC?: boolean;
  /** Show text below bar */
  dualLine?: boolean;
  /** Fixed refresh rate in seconds (0 for auto) */
  refreshSecs?: number;

  // Calibration
  /** Calibration value for FPS calculation */
  calibrate?: number;
  /** ETA smoothing factor (0-1). Higher = more responsive to rate changes */
  etaAlpha?: number;

  // Units
  /** Unit label (e.g., 'B', 'bytes') */
  unit?: string;
  /** Scale type ('SI', 'IEC', 'SI2') */
  scale?: "SI" | "IEC" | "SI2" | null;
  /** Decimal precision when scaling */
  precision?: number;

  // Enrichment
  /** Add position to print() calls */
  enrichPrint?: boolean;
  /** Starting position for enrichment */
  enrichOffset?: number;
}

/**
 * Resolved configuration with all options filled in.
 */
export interface ResolvedConfig {
  length: number;
  spinner: SpinnerFactory;
  bar: BarFactory;
  unknown: SpinnerFactory;
  title: string;
  file: NodeJS.WriteStream;
  forceTty: boolean | null;
  disable: boolean;
  monitor: boolean | string;
  elapsed: boolean | string;
  stats: boolean | string;
  receipt: boolean;
  receiptText: boolean;
  manual: boolean;
  ctrlC: boolean;
  dualLine: boolean;
  refreshSecs: number;
  calibrate: number;
  etaAlpha: number;
  unit: string;
  scale: "SI" | "IEC" | "SI2" | null;
  precision: number;
  enrichPrint: boolean;
  enrichOffset: number;
}

/**
 * Default configuration values.
 */
const DEFAULT_CONFIG: ResolvedConfig = {
  length: 40,
  spinner: getSpinner("default"),
  bar: getBar("default"),
  unknown: getSpinner("default"),
  title: "",
  file: process.stdout,
  forceTty: null,
  disable: false,
  monitor: true,
  elapsed: true,
  stats: true,
  receipt: true,
  receiptText: false,
  manual: false,
  ctrlC: true,
  dualLine: false,
  refreshSecs: 0,
  calibrate: 1_000_000,
  etaAlpha: 0.1,
  unit: "",
  scale: null,
  precision: 1,
  enrichPrint: true,
  enrichOffset: 0,
};

/**
 * Global configuration store.
 */
let globalConfig: Partial<AliveBarOptions> = {};

/**
 * Set global configuration defaults.
 */
export function setGlobalConfig(options: Partial<AliveBarOptions>): void {
  globalConfig = { ...globalConfig, ...options };
}

/**
 * Get current global configuration.
 */
export function getGlobalConfig(): Partial<AliveBarOptions> {
  return { ...globalConfig };
}

/**
 * Reset global configuration to defaults.
 */
export function resetGlobalConfig(): void {
  globalConfig = {};
}

/**
 * Resolve options by merging defaults, global config, and local options.
 */
export function resolveConfig(options: AliveBarOptions = {}): ResolvedConfig {
  const merged = { ...globalConfig, ...options };

  // Apply theme if specified
  let theme: Theme | undefined;
  if (merged.theme) {
    theme = getTheme(merged.theme);
  }

  return {
    length: merged.length ?? DEFAULT_CONFIG.length,
    spinner: getSpinner(merged.spinner ?? theme?.spinner ?? "default"),
    bar: getBar(merged.bar ?? theme?.bar ?? "default"),
    unknown: getSpinner(merged.unknown ?? theme?.unknown ?? "default"),
    title: merged.title ?? DEFAULT_CONFIG.title,
    file: merged.file ?? DEFAULT_CONFIG.file,
    forceTty: merged.forceTty ?? DEFAULT_CONFIG.forceTty,
    disable: merged.disable ?? DEFAULT_CONFIG.disable,
    monitor: merged.monitor ?? DEFAULT_CONFIG.monitor,
    elapsed: merged.elapsed ?? DEFAULT_CONFIG.elapsed,
    stats: merged.stats ?? DEFAULT_CONFIG.stats,
    receipt: merged.receipt ?? DEFAULT_CONFIG.receipt,
    receiptText: merged.receiptText ?? DEFAULT_CONFIG.receiptText,
    manual: merged.manual ?? DEFAULT_CONFIG.manual,
    ctrlC: merged.ctrlC ?? DEFAULT_CONFIG.ctrlC,
    dualLine: merged.dualLine ?? DEFAULT_CONFIG.dualLine,
    refreshSecs: merged.refreshSecs ?? DEFAULT_CONFIG.refreshSecs,
    calibrate: merged.calibrate ?? DEFAULT_CONFIG.calibrate,
    etaAlpha: merged.etaAlpha ?? DEFAULT_CONFIG.etaAlpha,
    unit: merged.unit ?? DEFAULT_CONFIG.unit,
    scale: merged.scale ?? DEFAULT_CONFIG.scale,
    precision: merged.precision ?? DEFAULT_CONFIG.precision,
    enrichPrint: merged.enrichPrint ?? DEFAULT_CONFIG.enrichPrint,
    enrichOffset: merged.enrichOffset ?? DEFAULT_CONFIG.enrichOffset,
  };
}

/**
 * Configuration handler for convenient access.
 */
export const config = {
  set: setGlobalConfig,
  get: getGlobalConfig,
  reset: resetGlobalConfig,
  resolve: resolveConfig,
};
