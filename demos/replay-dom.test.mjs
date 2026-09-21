// Exercise the mounted UI against the actual vendored Rust engine. This small DOM fixture
// implements only browser primitives; it performs no replay arithmetic or rendering itself.
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import * as glue from "../engine/napkin.js";
import {Engine} from "./engine.mjs";
import {mountReplay} from "./replay.mjs";
class Node {
  constructor(tag){this.tag=tag;this.children=[];this.listeners={};this.value="";this.files=[];}
  set textContent(text){this.text=String(text);this.children=[];}
  get textContent(){return (this.text||"")+this.children.map(n=>n.textContent).join("");}
  append(...nodes){this.children.push(...nodes);}
  replaceChildren(...nodes){this.text="";this.children=nodes;}
  setAttribute(key,value){this[key]=value;}
  addEventListener(event,fn){this.listeners[event]=fn;}
  async fire(event){return this.listeners[event]?.({preventDefault(){}});}
  click(){if(this.tag==="a")download=this.href;else return this.fire("click");}
}
globalThis.document={createElement:tag=>new Node(tag)};
let download;
await glue.default({module_or_path:readFileSync(new URL("../engine/napkin_bg.wasm",import.meta.url))});
const payload=JSON.parse(readFileSync(new URL("../engine/napkin.json",import.meta.url)));
const rows=JSON.parse(readFileSync(new URL("../engine/rows.json",import.meta.url)));
const mount=()=>mountReplay(new Engine(glue,payload,rows));
const all=(root,tag)=>[...(root.tag===tag?[root]:[]),...root.children.flatMap(n=>all(n,tag))];
const ui=mount();
const button=(ui,label)=>all(ui.element,"button").find(n=>n.textContent===label);
const select=all(ui.element,"select")[0];select.value="2";await select.fire("change");
await button(ui,"one on").click();
function checkRendered(ui){
  const actual=JSON.parse(glue.experiment_json(ui.replay.save()));
  const tick=actual.resolved_experiment.selected_tick;
  const table=all(ui.element,"table")[0];
  assert.deepEqual(all(table,"th").map(n=>n.textContent),["dot","baseline","changed weights"]);
  assert.deepEqual(all(table,"td").map(n=>n.textContent),actual.baseline.history[tick].flatMap((v,i)=>[String(i),v,actual.experiment.history[tick][i]]));
  const base=actual.baseline.checks.oscillatory_mode_stability;
  const changed=actual.experiment.checks.oscillatory_mode_stability;
  assert.ok(ui.element.textContent.includes(`baseline ${base.status} (k × bound = ${base.k_times_bound}); changed weights ${changed.status} (k × bound = ${changed.k_times_bound})`));
  assert.ok(ui.element.textContent.includes(`Physical-energy conservation: ${actual.experiment.checks.physical_energy_conservation}`));
  return actual;
}
const actual=checkRendered(ui);
assert.notDeepEqual(actual.baseline.history[1],actual.experiment.history[1]);
assert.notEqual(actual.baseline.checks.oscillatory_mode_stability.k_times_bound,actual.experiment.checks.oscillatory_mode_stability.k_times_bound);
const first=all(ui.element,"input").find(n=>n.type==="text");
first.value="13";await first.fire("change");
assert.equal(first.value,"12","refused input must restore the accepted displayed value");
assert.ok(ui.element.textContent.includes("Previous experiment kept"));
await button(ui,"Export experiment").click();
const saved=await (await fetch(download)).text();
assert.deepEqual(JSON.parse(saved),actual.resolved_experiment,"export wiring must save the displayed accepted experiment");
const fresh=mount();const file=all(fresh.element,"input").find(n=>n.type==="file");
file.files=[new File([saved],"replay.json")];await file.fire("change");
assert.deepEqual(checkRendered(fresh),actual,"file input must replay both arms and the selected tick");
file.files=[new File(["{"],"bad.json")];await file.fire("change");
assert.ok(fresh.element.textContent.includes("Not loaded:"));checkRendered(fresh);
first.value="6";await first.fire("change");
assert.equal(ui.replay.request.selected_tick,0,"initial-state edits restart both arms");
checkRendered(ui);
await button(fresh,"again").click();assert.equal(fresh.replay.request.selected_tick,0);checkRendered(fresh);
ui.setVisible(false);assert.equal(ui.element.hidden,true);
console.log("mounted replay: exact arm cells, labels, separate bounds, refused controls, export/import and restart pass");
