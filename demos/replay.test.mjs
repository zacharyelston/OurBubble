// Actual vendored Wasm, plus mutations of saved requests and rendered arm selection.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import * as glue from "../engine/napkin.js";
import { Engine } from "./engine.mjs";
import { Replay } from "./replay.mjs";
await glue.default({module_or_path:readFileSync(new URL("../engine/napkin_bg.wasm",import.meta.url))});
const payload=JSON.parse(readFileSync(new URL("../engine/napkin.json",import.meta.url)));
const rows=JSON.parse(readFileSync(new URL("../engine/rows.json",import.meta.url)));
const engine=()=>new Engine(glue,payload,rows);
const a=new Replay(engine());
a.change({edge_weights:["2","1/2","3/2","1","1","2"],selected_tick:9});
const exported=a.save();const fresh=new Replay(engine());fresh.load(exported);
assert.deepEqual(fresh.answer,a.answer,"export/fresh engine/replay must reproduce every exact row");
assert.equal(fresh.request.selected_tick,9);
const oracle=JSON.parse(glue.experiment_json(exported));
assert.deepEqual(fresh.rows(),oracle.baseline.history[9].map((value,i)=>({vertex:i,baseline:value,experiment:oracle.experiment.history[9][i]})));
assert.notDeepEqual(fresh.rows().map(r=>r.baseline),fresh.rows().map(r=>r.experiment),"this changed metric must distinguish both arms");
const stable=fresh.save();
const mutations=[
  {schema:"unsupported"},{topology:"triangle"},{engine_source:"stale"},
  {edge_order:[[9,10]]},{edge_weights:["bad"]},{initial:["99999999999999999999999999999999999999999999999999999999","0","0","0"]},
  {initial:["1/0","0","0","0"]},{k:"1/2"},{ticks:65},{selected_tick:99},{extra:true},
];
for(const fields of mutations){assert.throws(()=>fresh.load(JSON.stringify({...a.request,...fields})));assert.equal(fresh.save(),stable,"refusal must preserve the last replayable experiment");}
assert.throws(()=>fresh.load("{"));
assert.throws(()=>fresh.load(JSON.stringify({...a.request,initial:["13","0","0","0"]})), /initial/, "surface the engine's named refusal");
assert.throws(()=>fresh.load(" ".repeat(8193)));
assert.throws(()=>fresh.load(stable.replace('"ticks":', '"ticks": 1, "ticks":')),"duplicate keys must reach Rust unchanged");
assert.deepEqual(fresh.load(stable),a.answer,"engine must remain alive after every refusal");
fresh.change({edge_weights:["1","1","1","1","1","1"],selected_tick:0});
assert.deepEqual(fresh.answer.baseline.history,fresh.answer.experiment.history);
assert.equal(fresh.answer.experiment.checks.oscillatory_mode_stability.status,"verified:sufficient-bound");
assert.equal(fresh.answer.experiment.checks.physical_energy_conservation,"not-checked");
assert.ok(fresh.engine.calls.some(c=>c.startsWith("experiment_json(")),"all runs use Rust");
console.log("replay: exact fresh-load parity, arm selection, reset, weighted checks and 14 refusal mutations pass");
