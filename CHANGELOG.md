# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-29

### Added

- Initial TypeScript port of [alive-progress](https://github.com/rsalmei/alive-progress)
- Core progress bar functionality with `aliveBar()` and `aliveIt()`
- 40+ built-in spinner animations (dots, bounce, arrows, moon, etc.)
- 15+ bar styles (smooth, classic, blocks, bubbles, etc.)
- 8 themes for quick styling (smooth, classic, ascii, modern, etc.)
- Accurate ETA calculation with exponential smoothing
- Console interception to enrich `console.log()` output
- Pause/resume support
- Manual mode for percentage-based progress
- Unknown mode for indeterminate progress
- Dual-line mode for detailed status messages
- Global configuration with `setGlobalConfig()`
- Configurable ETA smoothing with `etaAlpha` option
- Proper dual-line clearing for Windows compatibility
- Full TypeScript type definitions
- Comprehensive test suite (231 tests)
