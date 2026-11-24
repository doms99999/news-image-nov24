// The entry is a single pre-made image, entry.png, sitting beside this file.
// The program's whole job is to place it at /output/entry.png, where the
// scorer reads it. Outside the grading container, MAKEFUN_OUTPUT_DIR
// stands in for /output.

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(new URL('./entry.png', import.meta.url), join(outDir, 'entry.png'));
