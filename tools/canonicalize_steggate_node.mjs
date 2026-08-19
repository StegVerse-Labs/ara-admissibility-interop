#!/usr/bin/env node
/** Independent Node.js implementation of stegverse.jcs.v1 canonicalization. */
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

export const PROFILE = 'stegverse.jcs.v1';
export const MAX_SAFE_INTEGER = Number.MAX_SAFE_INTEGER;

export class CanonicalizationError extends Error {}

function validateString(value) {
  for (let i = 0; i < value.length; i += 1) {
    const unit = value.charCodeAt(i);
    if (unit >= 0xd800 && unit <= 0xdbff) {
      if (i + 1 >= value.length) throw new CanonicalizationError('unpaired surrogate is outside stegverse.jcs.v1');
      const low = value.charCodeAt(i + 1);
      if (low < 0xdc00 || low > 0xdfff) throw new CanonicalizationError('unpaired surrogate is outside stegverse.jcs.v1');
      i += 1;
    } else if (unit >= 0xdc00 && unit <= 0xdfff) {
      throw new CanonicalizationError('unpaired surrogate is outside stegverse.jcs.v1');
    }
  }
}

function compareUtf16(a, b) {
  validateString(a);
  validateString(b);
  const limit = Math.min(a.length, b.length);
  for (let i = 0; i < limit; i += 1) {
    const av = a.charCodeAt(i);
    const bv = b.charCodeAt(i);
    if (av !== bv) return av - bv;
  }
  return a.length - b.length;
}

function serialize(value) {
  if (value === null) return 'null';
  if (value === true) return 'true';
  if (value === false) return 'false';
  if (typeof value === 'number') {
    if (!Number.isFinite(value) || !Number.isInteger(value)) {
      throw new CanonicalizationError('floating-point values are outside stegverse.jcs.v1');
    }
    if (!Number.isSafeInteger(value)) {
      throw new CanonicalizationError('integer exceeds stegverse.jcs.v1 interoperable range');
    }
    return Object.is(value, -0) ? '0' : String(value);
  }
  if (typeof value === 'string') {
    validateString(value);
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) return `[${value.map(serialize).join(',')}]`;
  if (typeof value === 'object') {
    const keys = Object.keys(value).sort(compareUtf16);
    return `{${keys.map((key) => `${serialize(key)}:${serialize(value[key])}`).join(',')}}`;
  }
  throw new CanonicalizationError(`unsupported value type: ${typeof value}`);
}

export function canonicalize(value) {
  return Buffer.from(serialize(value), 'utf8');
}

export function contentId(value) {
  return `sha256:${createHash('sha256').update(canonicalize(value)).digest('hex')}`;
}

function sourceHasNonIntegerNumberToken(source) {
  let inString = false;
  let escaped = false;
  for (let i = 0; i < source.length; i += 1) {
    const ch = source[i];
    if (inString) {
      if (escaped) escaped = false;
      else if (ch === '\\') escaped = true;
      else if (ch === '"') inString = false;
      continue;
    }
    if (ch === '"') {
      inString = true;
      continue;
    }
    if (ch === '-' || (ch >= '0' && ch <= '9')) {
      let j = i;
      if (source[j] === '-') j += 1;
      while (j < source.length && source[j] >= '0' && source[j] <= '9') j += 1;
      if (source[j] === '.' || source[j] === 'e' || source[j] === 'E') return true;
      i = j - 1;
    }
  }
  return false;
}

export function parseCanonicalizableJson(source) {
  if (sourceHasNonIntegerNumberToken(source)) {
    throw new CanonicalizationError('floating-point values are outside stegverse.jcs.v1');
  }
  return JSON.parse(source);
}

function main(argv) {
  const hashOnly = argv.includes('--hash-only');
  const path = argv.find((arg) => !arg.startsWith('--'));
  if (!path) throw new Error('usage: canonicalize_steggate_node.mjs <path> [--hash-only]');
  const value = parseCanonicalizableJson(readFileSync(path, 'utf8'));
  const data = canonicalize(value);
  if (hashOnly) process.stdout.write(`sha256:${createHash('sha256').update(data).digest('hex')}\n`);
  else process.stdout.write(`${data.toString('utf8')}\n`);
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    main(process.argv.slice(2));
  } catch (error) {
    process.stderr.write(`canonicalization failed: ${error.message}\n`);
    process.exitCode = 2;
  }
}
