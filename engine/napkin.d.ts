/* tslint:disable */
/* eslint-disable */

/**
 * The census and coboundaries of the complete complex on `dots` dots.
 */
export function census_json(dots: number): string;

/**
 * The tick certificate for an object at a tick.
 */
export function certificate_json(object: string, k: string): string;

/**
 * The midpoint cut and the threaded pair, with their exact shares.
 */
export function cut_json(): string;

/**
 * The loop sums of one object from one set of numbers.
 */
export function loops_json(object: string, values: string[], degree: number): string;

/**
 * One exact rational, rendered the way a napkin does — or the refusal.
 */
export function number_json(value: string): string;

/**
 * A run of the one rule. `initial` is a JSON array of exact `"n/d"` strings.
 */
export function slosh_json(object: string, initial: string[], k: string, ticks: number): string;

export type InitInput = RequestInfo | URL | Response | BufferSource | WebAssembly.Module;

export interface InitOutput {
    readonly memory: WebAssembly.Memory;
    readonly census_json: (a: number) => [number, number];
    readonly certificate_json: (a: number, b: number, c: number, d: number) => [number, number];
    readonly cut_json: () => [number, number];
    readonly loops_json: (a: number, b: number, c: number, d: number, e: number) => [number, number];
    readonly number_json: (a: number, b: number) => [number, number];
    readonly slosh_json: (a: number, b: number, c: number, d: number, e: number, f: number, g: number) => [number, number];
    readonly __wbindgen_malloc: (a: number, b: number) => number;
    readonly __wbindgen_realloc: (a: number, b: number, c: number, d: number) => number;
    readonly __wbindgen_externrefs: WebAssembly.Table;
    readonly __wbindgen_free: (a: number, b: number, c: number) => void;
    readonly __externref_table_alloc: () => number;
    readonly __wbindgen_start: () => void;
}

export type SyncInitInput = BufferSource | WebAssembly.Module;

/**
 * Instantiates the given `module`, which can either be bytes or
 * a precompiled `WebAssembly.Module`.
 *
 * @param {{ module: SyncInitInput }} module - Passing `SyncInitInput` directly is deprecated.
 *
 * @returns {InitOutput}
 */
export function initSync(module: { module: SyncInitInput } | SyncInitInput): InitOutput;

/**
 * If `module_or_path` is {RequestInfo} or {URL}, makes a request and
 * for everything else, calls `WebAssembly.instantiate` directly.
 *
 * @param {{ module_or_path: InitInput | Promise<InitInput> }} module_or_path - Passing `InitInput` directly is deprecated.
 *
 * @returns {Promise<InitOutput>}
 */
export default function __wbg_init (module_or_path?: { module_or_path: InitInput | Promise<InitInput> } | InitInput | Promise<InitInput>): Promise<InitOutput>;
