import { afterEach, beforeEach, describe, expect, test } from "bun:test";
import { barFactory } from "../src/animations/bars";
import { frameSpinner } from "../src/animations/spinners";
import {
  config,
  getGlobalConfig,
  resetGlobalConfig,
  resolveConfig,
  setGlobalConfig,
} from "../src/core/configuration";

describe("global configuration", () => {
  beforeEach(() => {
    resetGlobalConfig();
  });

  afterEach(() => {
    resetGlobalConfig();
  });

  test("getGlobalConfig returns empty object initially", () => {
    const config = getGlobalConfig();
    expect(config).toEqual({});
  });

  test("setGlobalConfig sets values", () => {
    setGlobalConfig({ length: 50 });
    const config = getGlobalConfig();
    expect(config.length).toBe(50);
  });

  test("setGlobalConfig merges with existing config", () => {
    setGlobalConfig({ length: 50 });
    setGlobalConfig({ title: "Test" });

    const config = getGlobalConfig();
    expect(config.length).toBe(50);
    expect(config.title).toBe("Test");
  });

  test("resetGlobalConfig clears all settings", () => {
    setGlobalConfig({ length: 50, title: "Test" });
    resetGlobalConfig();

    const config = getGlobalConfig();
    expect(config).toEqual({});
  });
});

describe("resolveConfig", () => {
  beforeEach(() => {
    resetGlobalConfig();
  });

  afterEach(() => {
    resetGlobalConfig();
  });

  test("uses default values when no options provided", () => {
    const resolved = resolveConfig();

    expect(resolved.length).toBe(40);
    expect(resolved.disable).toBe(false);
    expect(resolved.monitor).toBe(true);
    expect(resolved.elapsed).toBe(true);
    expect(resolved.stats).toBe(true);
    expect(resolved.receipt).toBe(true);
    expect(resolved.manual).toBe(false);
    expect(resolved.ctrlC).toBe(true);
    expect(resolved.dualLine).toBe(false);
    expect(resolved.refreshSecs).toBe(0);
    expect(resolved.enrichPrint).toBe(true);
    expect(resolved.enrichOffset).toBe(0);
  });

  test("uses provided options over defaults", () => {
    const resolved = resolveConfig({
      length: 50,
      disable: true,
      manual: true,
    });

    expect(resolved.length).toBe(50);
    expect(resolved.disable).toBe(true);
    expect(resolved.manual).toBe(true);
  });

  test("uses global config when no local options", () => {
    setGlobalConfig({ length: 60, title: "Global" });

    const resolved = resolveConfig();

    expect(resolved.length).toBe(60);
    expect(resolved.title).toBe("Global");
  });

  test("local options override global config", () => {
    setGlobalConfig({ length: 60, title: "Global" });

    const resolved = resolveConfig({ length: 30, title: "Local" });

    expect(resolved.length).toBe(30);
    expect(resolved.title).toBe("Local");
  });

  test("resolves spinner by name", () => {
    const resolved = resolveConfig({ spinner: "dots" });

    expect(typeof resolved.spinner).toBe("function");
  });

  test("resolves spinner by factory", () => {
    const customSpinner = frameSpinner(["X", "O"]);
    const resolved = resolveConfig({ spinner: customSpinner });

    expect(resolved.spinner).toBe(customSpinner);
  });

  test("resolves bar by name", () => {
    const resolved = resolveConfig({ bar: "classic" });

    expect(typeof resolved.bar).toBe("function");
  });

  test("resolves bar by factory", () => {
    const customBar = barFactory({ chars: "#" });
    const resolved = resolveConfig({ bar: customBar });

    expect(resolved.bar).toBe(customBar);
  });

  test("applies theme settings", () => {
    const resolved = resolveConfig({ theme: "classic" });

    // Theme should set spinner and bar
    expect(typeof resolved.spinner).toBe("function");
    expect(typeof resolved.bar).toBe("function");
  });

  test("local spinner overrides theme", () => {
    const customSpinner = frameSpinner(["A", "B"]);
    const resolved = resolveConfig({
      theme: "classic",
      spinner: customSpinner,
    });

    expect(resolved.spinner).toBe(customSpinner);
  });

  test("resolves file to stdout by default", () => {
    const resolved = resolveConfig();
    expect(resolved.file).toBe(process.stdout);
  });

  test("resolves forceTty to null by default", () => {
    const resolved = resolveConfig();
    expect(resolved.forceTty).toBeNull();
  });

  test("handles scale option", () => {
    const resolved = resolveConfig({ scale: "SI" });
    expect(resolved.scale).toBe("SI");
  });

  test("handles unit option", () => {
    const resolved = resolveConfig({ unit: "MB" });
    expect(resolved.unit).toBe("MB");
  });

  test("handles precision option", () => {
    const resolved = resolveConfig({ precision: 2 });
    expect(resolved.precision).toBe(2);
  });

  test("uses default etaAlpha of 0.1", () => {
    const resolved = resolveConfig();
    expect(resolved.etaAlpha).toBe(0.1);
  });

  test("handles custom etaAlpha option", () => {
    const resolved = resolveConfig({ etaAlpha: 0.3 });
    expect(resolved.etaAlpha).toBe(0.3);
  });
});

describe("config object", () => {
  beforeEach(() => {
    config.reset();
  });

  afterEach(() => {
    config.reset();
  });

  test("config.set sets global config", () => {
    config.set({ length: 50 });
    expect(config.get().length).toBe(50);
  });

  test("config.get returns global config", () => {
    config.set({ title: "Test" });
    expect(config.get().title).toBe("Test");
  });

  test("config.reset clears global config", () => {
    config.set({ length: 50 });
    config.reset();
    expect(config.get()).toEqual({});
  });

  test("config.resolve resolves configuration", () => {
    config.set({ length: 50 });
    const resolved = config.resolve({ title: "Test" });

    expect(resolved.length).toBe(50);
    expect(resolved.title).toBe("Test");
  });
});

describe("widget format strings", () => {
  test("monitor can be a format string", () => {
    const resolved = resolveConfig({ monitor: "{count}/{total}" });
    expect(resolved.monitor).toBe("{count}/{total}");
  });

  test("elapsed can be a format string", () => {
    const resolved = resolveConfig({ elapsed: "Time: {elapsed}" });
    expect(resolved.elapsed).toBe("Time: {elapsed}");
  });

  test("stats can be a format string", () => {
    const resolved = resolveConfig({ stats: "Rate: {rate}" });
    expect(resolved.stats).toBe("Rate: {rate}");
  });
});

describe("boolean widget options", () => {
  test("monitor can be disabled", () => {
    const resolved = resolveConfig({ monitor: false });
    expect(resolved.monitor).toBe(false);
  });

  test("elapsed can be disabled", () => {
    const resolved = resolveConfig({ elapsed: false });
    expect(resolved.elapsed).toBe(false);
  });

  test("stats can be disabled", () => {
    const resolved = resolveConfig({ stats: false });
    expect(resolved.stats).toBe(false);
  });

  test("receipt can be disabled", () => {
    const resolved = resolveConfig({ receipt: false });
    expect(resolved.receipt).toBe(false);
  });
});
