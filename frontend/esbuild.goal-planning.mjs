import * as esbuild from 'esbuild';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));

const isWatch = process.argv.includes('--watch');

const buildOptions = {
  entryPoints: [resolve(__dirname, 'src/goal-planning.jsx')],
  bundle: true,
  outfile: resolve(__dirname, 'js/goal-planning-bundle.js'),
  format: 'iife',
  target: ['es2018'],
  minify: !isWatch,
  sourcemap: isWatch,
  define: {
    'process.env.NODE_ENV': isWatch ? '"development"' : '"production"'
  },
  loader: {
    '.jsx': 'jsx',
  },
  jsxFactory: 'React.createElement',
  jsxFragment: 'React.Fragment',
};

if (isWatch) {
  const ctx = await esbuild.context(buildOptions);
  await ctx.watch();
  console.log('⚡ esbuild watching for changes...');
} else {
  const result = await esbuild.build(buildOptions);
  console.log('✅ goal-planning-bundle.js built successfully');
  if (result.errors.length > 0) {
    console.error('Build errors:', result.errors);
  }
}
