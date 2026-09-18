// Saved exact experiments: input selection and rendering only. Rust computes both complete arms.
// FIREWALL: toy tetrahedron arithmetic; no claim about nature or exact physical-energy conservation.

export class Replay {
  constructor(engine) {
    this.engine = engine;
    this.load(JSON.stringify(engine.experimentExample()));
  }
  load(text) {
    // No JSON parse/stringify before the engine sees the original text: duplicate keys matter.
    const answer = this.engine.experiment(text);
    if (answer.status === "refused") throw new Error(answer.reason);
    if (!answer.resolved_experiment) throw new Error("The engine did not return an experiment.");
    this.answer = answer;
    this.request = structuredClone(answer.resolved_experiment);
    return answer;
  }
  change(fields) { return this.load(JSON.stringify({ ...this.request, ...fields })); }
  save() { return JSON.stringify(this.request, null, 2) + "\n"; }
  rows() {
    const tick = this.request.selected_tick;
    return this.answer.baseline.history[tick].map((value, index) => ({
      vertex: index, baseline: value, experiment: this.answer.experiment.history[tick][index],
    }));
  }
}

function element(tag, text = "") {
  const node = document.createElement(tag);
  node.textContent = text;
  return node;
}
function button(text, action) {
  const node = element("button", text);node.type="button";node.addEventListener("click",action);return node;
}

export function mountReplay(engine) {
  const replay = new Replay(engine);
  const root=element("details");root.className="replay";
  root.append(element("summary","Save and replay a comparison"));
  root.append(element("p","Choose the starting numbers and line weights. Both arms restart from that same beginning whenever you change an input. The baseline counts every line equally. This saved experiment uses the choices shown here."));
  const form=element("form");form.addEventListener("submit",event=>event.preventDefault());
  const inputs=element("fieldset");inputs.append(element("legend","Starting numbers and weights"));
  const initial=[],weights=[];
  function field(label,input) { const wrap=element("label",label);wrap.append(input);inputs.append(wrap);return input; }
  function select(choices) {const input=element("select");for(const value of choices){const option=element("option",value);option.value=value;input.append(option);}return input;}
  let timer=null;
  const stop=()=>{if(timer!==null){clearInterval(timer);timer=null;}play.textContent="play";};
  const message=element("p");message.setAttribute("role","status");message.setAttribute("aria-live","polite");
  const output=element("div");output.className="replay-output";
  function change(fields) {stop();try{replay.change(fields);sync();draw();message.textContent="Recomputed from the starting state.";}catch(error){sync();message.textContent=`Not loaded: ${error.message}. Previous experiment kept.`;}}
  replay.request.initial.forEach((value,index)=>{
    const input=field(`Dot ${index}`,element("input"));input.type="text";input.value=value;input.size=5;
    input.addEventListener("change",()=>change({initial:initial.map(input=>input.value),selected_tick:0}));initial.push(input);
  });
  replay.request.edge_order.forEach((edge,index)=>{
    const input=field(`Line ${edge.join("–")}`,select(["1/2","1","3/2","2"]));input.value=replay.request.edge_weights[index];
    input.addEventListener("change",()=>change({edge_weights:weights.map(input=>input.value),selected_tick:0}));weights.push(input);
  });
  const k=field("Tick setting k = c²dt²",select(["1/16","1/8","1/4"]));
  k.addEventListener("change",()=>change({k:k.value,selected_tick:0}));
  const horizon=field("Ticks to compute (at most 64)",element("input"));horizon.type="number";horizon.min="0";horizon.max="64";
  horizon.addEventListener("change",()=>change({ticks:Number(horizon.value),selected_tick:0}));
  form.append(inputs);
  const controls=element("div");controls.className="replay-controls";
  const tick=element("span");tick.setAttribute("aria-live","polite");
  const back=button("one back",()=>change({selected_tick:replay.request.selected_tick-1}));
  const next=button("one on",()=>change({selected_tick:replay.request.selected_tick+1}));
  const play=button("play",()=>{if(timer!==null){stop();return;}play.textContent="stop";timer=setInterval(()=>{
    if(replay.request.selected_tick===replay.request.ticks){stop();return;}
    try{replay.change({selected_tick:replay.request.selected_tick+1});draw();}catch(error){stop();message.textContent=error.message;}
  },900);});
  const reset=button("again",()=>change({selected_tick:0}));
  controls.append(back,tick,next,play,reset);
  const saved=element("div");saved.className="replay-controls";
  let downloadUrl=null;
  saved.append(button("Export experiment",()=>{
    stop();if(downloadUrl)URL.revokeObjectURL(downloadUrl);
    downloadUrl=URL.createObjectURL(new Blob([replay.save()],{type:"application/json"}));
    const a=element("a");a.href=downloadUrl;a.download="tetrahedron-experiment.json";a.click();
    message.textContent="Saved the initial experiment and selected tick. Imported histories are never trusted.";
  }));
  const file=element("input");file.type="file";file.accept=".json,application/json";
  const fileLabel=element("label","Load experiment ");fileLabel.append(file);saved.append(fileLabel);
  file.addEventListener("change",async()=>{
    stop();const selected=file.files[0];if(!selected)return;
    // Bound the read before allocating file contents; Rust also enforces its own UTF-8 byte cap.
    if(selected.size>8192){message.textContent="Not loaded: experiment file exceeds 8192 bytes.";file.value="";return;}
    try{replay.load(await selected.text());sync();draw();message.textContent="Loaded and recomputed both arms.";}
    catch(error){message.textContent=`Not loaded: ${error.message}`;}
    file.value="";
  });
  const exact=element("details");exact.append(element("summary","Exact rows and experiment choices"));const raw=element("pre");exact.append(raw);
  root.append(form,controls,saved,message,output,exact);
  function sync(){initial.forEach((input,i)=>{input.value=replay.request.initial[i];});weights.forEach((input,i)=>{input.value=replay.request.edge_weights[i];});k.value=replay.request.k;horizon.value=replay.request.ticks;}
  function draw(){
    tick.textContent=`tick ${replay.request.selected_tick} of ${replay.request.ticks}`;
    back.disabled=replay.request.selected_tick===0;next.disabled=replay.request.selected_tick===replay.request.ticks;
    const table=element("table");const caption=element("caption","Both arms at the same tick");table.append(caption);
    const header=element("tr");for(const label of ["dot","baseline","changed weights"])header.append(element("th",label));table.append(header);
    for(const row of replay.rows()){const tr=element("tr");for(const value of [row.vertex,row.baseline,row.experiment])tr.append(element("td",String(value)));table.append(tr);}
    const changes=replay.request.edge_order.map((edge,i)=>`${edge.join("–")}: ${replay.request.edge_weights[i]}`).join("; ");
    const stability=replay.answer.experiment.checks.oscillatory_mode_stability;
    const baseline=replay.answer.baseline.checks.oscillatory_mode_stability;
    output.replaceChildren(element("p",`Initial: ${replay.request.initial.join(", ")}. k=${replay.request.k}. Previous state equals the initial state. No external flux, sources or damping.`),element("p",`Line weights: ${changes}. Baseline weights: ${replay.answer.baseline.edge_weights.join(", ")}.`),table,
      element("p",`Engine's sufficient stability check: baseline ${baseline.status} (k × bound = ${baseline.k_times_bound}); changed weights ${stability.status} (k × bound = ${stability.k_times_bound}). Physical-energy conservation: ${replay.answer.experiment.checks.physical_energy_conservation}.`),
      element("p",`Toy lattice arithmetic. Engine source: ${replay.answer.engine_source}`));
    raw.textContent=JSON.stringify({experiment:replay.request,baseline:replay.answer.baseline,changed:replay.answer.experiment},null,2);
  }
  sync();draw();
  return {element:root,setVisible(visible){root.hidden=!visible;if(!visible)stop();},replay};
}
