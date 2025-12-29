# alive-progress

A beautiful, animated progress bar for TypeScript/Node.js CLI applications.

This is a TypeScript port of the popular Python [alive-progress](https://github.com/rsalmei/alive-progress) library.

## Features

- **Live spinners** that react to your actual processing speed
- **Smooth progress bars** with sub-character precision
- **Accurate ETA** calculation with exponential smoothing
- **Auto-iteration** with `aliveIt()` for easy integration
- **Console interception** that enriches `console.log()` with progress position
- **40+ built-in spinners** and **15+ bar styles**
- **Themes** for quick styling
- **Manual mode** for API-driven progress
- **Unknown mode** for indeterminate progress
- **Pause/resume** support
- **Dual-line mode** for detailed messages
- **Full TypeScript support** with type definitions

## Installation

```bash
npm install alive-progress
```

## Quick Start

### Basic Usage

```typescript
import { aliveBar } from 'alive-progress';

const { bar, done } = aliveBar(100);

for (let i = 0; i < 100; i++) {
  await doWork();
  bar();  // Increment progress
}

done();  // Finalize and show receipt
```

### Auto-Iterating

```typescript
import { aliveIt } from 'alive-progress';

const items = ['a', 'b', 'c', 'd', 'e'];

for await (const item of aliveIt(items)) {
  await processItem(item);
  // Progress automatically increments
}
```

### With Options

```typescript
import { aliveBar } from 'alive-progress';

const { bar, done } = aliveBar(100, {
  title: 'Processing',
  spinner: 'dots',
  bar: 'smooth',
  theme: 'modern'
});

for (let i = 0; i < 100; i++) {
  bar.text = `Working on item ${i}`;
  await doWork();
  bar();
}

done();
```

## Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `length` | number | 40 | Width of the progress bar |
| `spinner` | string | 'dots' | Spinner style name |
| `bar` | string | 'smooth' | Bar style name |
| `theme` | string | - | Theme name (sets spinner, bar, unknown) |
| `title` | string | - | Title displayed before the bar |
| `manual` | boolean | false | Manual percentage mode |
| `dualLine` | boolean | false | Show text below bar |
| `monitor` | boolean | true | Show count/total [percent] |
| `elapsed` | boolean | true | Show elapsed time |
| `stats` | boolean | true | Show rate and ETA |
| `receipt` | boolean | true | Show final receipt |
| `enrichPrint` | boolean | true | Enrich console.log with position |
| `disable` | boolean | false | Disable all output |
| `forceTty` | boolean | null | Force TTY mode |
| `etaAlpha` | number | 0.1 | ETA smoothing factor (0-1). Higher = more responsive to rate changes |

## Built-in Styles

### Spinners

```
dots, dots2, dots3, classic, line, bounce, arrows, circle,
square, triangle, grow, pulse, star, moon, hearts, weather,
clock, earth, aesthetic, breathing, toggle, arc, pipe, noise,
shark, and many more...
```

### Bars

```
smooth, classic, blocks, bubbles, fish, halloween, arrow,
solid, squares, circles, ascii, fancy, minimal
```

### Themes

```
smooth, classic, ascii, scuba, musical, halloween, minimal, modern
```

## Manual Mode

For progress that doesn't follow a linear path:

```typescript
const { bar, done } = aliveBar(100, { manual: true });

bar(0.25);  // Jump to 25%
bar(0.50);  // Jump to 50%
bar(0.75);  // Jump to 75%
bar(1.0);   // Complete

done();
```

## Unknown Mode

When you don't know the total:

```typescript
const { bar, done } = aliveBar(null);  // No total

for (const item of items) {
  await process(item);
  bar();  // Just count up
}

done();
```

## Custom Spinners and Bars

### Custom Spinner

```typescript
import { frameSpinner, aliveBar } from 'alive-progress';

const mySpinner = frameSpinner(['🌑', '🌒', '🌓', '🌔', '🌕', '🌖', '🌗', '🌘']);

const { bar, done } = aliveBar(100, { spinner: mySpinner });
```

### Custom Bar

```typescript
import { barFactory, aliveBar } from 'alive-progress';

const myBar = barFactory({
  chars: '▰',
  background: '▱',
  borders: ['⟨', '⟩']
});

const { bar, done } = aliveBar(100, { bar: myBar });
```

## The Bar Handler

The `bar` function returned by `aliveBar` has several properties:

```typescript
const { bar, done } = aliveBar(100);

bar();           // Increment by 1
bar(5);          // Increment by 5
bar(10, { skipped: true });  // Skip items (for accurate ETA)

bar.text = 'Status message';   // Set situational text
bar.title = 'New Title';       // Change title

console.log(bar.current);      // Current count
console.log(bar.elapsed);      // Elapsed seconds
console.log(bar.monitor);      // Monitor widget text
console.log(bar.rate);         // Rate text
console.log(bar.eta);          // ETA text

const resume = bar.pause();    // Pause processing
// ... do something ...
resume();                      // Resume

const receipt = done();        // Finalize and get receipt
console.log(receipt);          // { total, count, elapsed, rate, success, ... }
```

## Global Configuration

Set defaults for all progress bars:

```typescript
import { setGlobalConfig } from 'alive-progress';

setGlobalConfig({
  length: 50,
  theme: 'modern',
  enrichPrint: true
});
```

## Console Enrichment

When `enrichPrint` is enabled (default), `console.log()` calls are enriched with the current position:

```typescript
const { bar, done } = aliveBar(100);

for (let i = 0; i < 100; i++) {
  if (i === 50) console.log('Halfway there!');
  bar();
}

done();

// Output: "on 50: Halfway there!"
```

## Demo

Run the built-in demo:

```bash
npx alive-progress-demo
```

Or:

```typescript
import { listSpinners, listBars, listThemes } from 'alive-progress';

console.log('Spinners:', listSpinners());
console.log('Bars:', listBars());
console.log('Themes:', listThemes());
```

## Acknowledgments

This is a TypeScript port of the excellent [alive-progress](https://github.com/rsalmei/alive-progress) Python library created by [Rogério Sampaio de Almeida (@rsalmei)](https://github.com/rsalmei).

The original Python library is a fantastic piece of work with beautiful animations and thoughtful design. All credit for the core concepts, animation designs, and API patterns goes to the original author.

## License

MIT License - see [LICENSE](LICENSE) for details.

Both the original Python library and this TypeScript port are MIT licensed.
