// The page: the steps, the controls, and nothing that explains itself.
//
// FIREWALL: these pages run a toy DEC lattice. Nothing they draw or print is a claim about nature.
// See ../FIREWALL.md.
//
// This file used to be the demos entire — some seven hundred lines of exact rational arithmetic and
// a paraphrase of every beat's chapter. Both are gone. The arithmetic is the vendored engine's
// (`engine.mjs`), the drawings are `draw.mjs`, the steps are `steps.mjs`, and the beat numbers and
// questions are `steps.json`, which `tools/demo_steps.py` derives from `OUTLINE.md` and the
// chapters. What is left here is the part that is genuinely a page: mount the steps, wire up the
// controls, and get out of the way.

import { openEngine } from "./engine.mjs";
import { drawings } from "./draw.mjs";
import { chapterSteps } from "./steps.mjs";

export { openEngine } from "./engine.mjs";
export { drawings } from "./draw.mjs";
export { chapterSteps } from "./steps.mjs";

/**
 * Join one chapter's step definitions to the generated scaffolding.
 *
 * This is where a renumber would show up as a failure rather than as a wrong number on a page: every
 * step declares the chapter sections it covers by **anchor**, and the join insists that the anchors
 * partition the chapter's marked sections exactly — each section covered once, none left over, none
 * named that the chapter has not got. The beat numbers and the questions come off the scaffolding.
 */
export function joinSteps(slug, steps, scaffold) {
  const chapter = scaffold.chapters[slug];
  if (!chapter) throw new Error(`steps.json has no chapter ${slug}`);
  const byAnchor = new Map(chapter.sections.map((section) => [section.anchor, section]));
  const seen = new Set();
  const joined = steps.map((step) => {
    const sections = step.anchors.map((anchor) => {
      const section = byAnchor.get(anchor);
      if (!section) {
        throw new Error(`${slug}: the step for "${anchor}" has no such section in the chapter`);
      }
      if (seen.has(anchor)) throw new Error(`${slug}: two steps claim the section "${anchor}"`);
      seen.add(anchor);
      return section;
    });
    const titleAnchor = step.titleFrom || step.anchors[0];
    const titled = sections.find((section) => section.anchor === titleAnchor);
    if (!titled) throw new Error(`${slug}: "${titleAnchor}" is not one of this step's own sections`);
    const beats = sections.map((section) => section.beat);
    return {
      ...step,
      sections,
      beats,
      beat: beats[0],
      title: titled.question,
      label: beats.length === 1
        ? `beat ${beats[0]}`
        : `beats ${beats[0]}–${beats[beats.length - 1]}`,
    };
  });
  const missing = chapter.sections.filter((section) => !seen.has(section.anchor));
  if (missing.length) {
    throw new Error(`${slug}: no step covers ${missing.map((s) => s.anchor).join(", ")}`);
  }
  return { chapter, steps: joined };
}

/** The state one step starts in: nothing pressed, no tick taken, the engine's own numbers typed. */
export function initialState(step, view) {
  const state = { tick: 0, pressed: false, yaw: view.yaw, pitch: view.pitch };
  for (const control of step.controls) {
    if (control.kind === "numbers") state.numbers = [...control.initial];
    if (control.kind === "choose") state.choice = { ...control.options[0], index: 0 };
  }
  return state;
}

/** Every state a step can be driven into — what `core.test.mjs` walks, and what a reader can reach. */
export function statesOf(step, view) {
  const base = initialState(step, view);
  const out = [base];
  for (const control of step.controls) {
    if (control.kind === "tick") {
      for (let tick = 1; tick <= control.count; tick += 1) out.push({ ...base, tick });
    }
    if (control.kind === "press") out.push({ ...base, pressed: true });
    if (control.kind === "choose") {
      control.options.forEach((option, index) => {
        out.push({ ...base, choice: { ...option, index } });
      });
    }
  }
  return out;
}

// ── the still ─────────────────────────────────────────────────────────────────────────────────────

const SVG_STILL_STYLE = `
  .net .panel polygon, .ring .panel polygon { fill: #f4ead8; stroke: none; }
  .net .stroke, .ring .stroke, .wire .stroke { stroke: #20314a; stroke-width: 3; fill: none;
    stroke-linecap: round; stroke-linejoin: round; }
  .ring .stroke { stroke-width: 2; }
  .net .stroke .strong, .ring .stroke .strong { stroke-width: 6; }
  .ring .stroke .tip-line { stroke-width: 1.2; }
  .net .stroke .cut polygon { fill: none; stroke: #20314a; stroke-width: 1.5;
    stroke-dasharray: 7 6; }
  .net .walk .head { fill: #20314a; stroke: none; }
  .net .middle circle { fill: #20314a; stroke: none; }
  .ring .absent line { stroke: #20314a; stroke-width: 1; stroke-dasharray: 2 7; opacity: 0.45; }
  .ring .dots circle { fill: #20314a; stroke: none; }
  .ring .dots circle.tip { fill: none; stroke: #20314a; stroke-width: 2; }
  .wire .stroke line { stroke-width: 1.6; }
  .wire .stroke.second line { stroke-width: 1; opacity: 0.55; }
  .wire .stroke.octahedron line { stroke-width: 1.1; opacity: 0.75; }
  .wire .stroke line.strong { stroke-width: 3.2; opacity: 1; }
  .wire .dots circle { fill: #20314a; stroke: none; }
  .wire .dots circle.tip { fill: none; stroke: #20314a; stroke-width: 1.6; }
  .net .labels, .ring .labels, .wire .labels { fill: #20314a;
    font-family: ui-sans-serif, system-ui, "Helvetica Neue", Arial, sans-serif; }
  .ring .labels .tip { font-style: italic; }
`;

/**
 * The drawing on screen as a standalone SVG file — the "still".
 *
 * The stills are the point of the drawing code and not a side effect of it: they are the intended
 * replacement for the illustration studies in the chapters, one at a time, in a later PR the owner
 * judges. So a still stands on its own — its own stylesheet inlined, its own title and description,
 * and a line naming the beat it came from. `DEMOS.md` says how the replacement will go.
 */
export function stillFrom(svgText, { chapter, beat, title }) {
  const stamp = `<!-- Our Bubble demo still · ${chapter} · beat ${beat}. Computed in the browser `
    + `by the vendored napkin engine (engine/, pinned by engine.lock). A drawing of a toy: nothing `
    + `in it is a claim about nature. -->`;
  return svgText.replace(
    /^<svg([^>]*)>/,
    (_match, attributes) => `${stamp}\n<svg${attributes}>\n  <style>${SVG_STILL_STYLE}</style>`,
  ).replace(/<title>[^<]*<\/title>/, `<title>${title}</title>`);
}

// ── the page ──────────────────────────────────────────────────────────────────────────────────────

function element(tag, attributes = {}, children = []) {
  const node = document.createElement(tag);
  for (const [name, value] of Object.entries(attributes)) {
    if (value === undefined) continue;
    if (name === "class") node.className = value;
    else if (name === "text") node.textContent = value;
    else node.setAttribute(name, value);
  }
  for (const child of children) node.append(child);
  return node;
}

function renderTable(spec) {
  const figure = element("figure", { class: "numbers" });
  figure.append(element("figcaption", { text: spec.caption }));
  const table = element("table");
  const head = element("tr");
  for (const cell of spec.head) head.append(element("th", { text: cell }));
  const body = element("tbody");
  for (const row of spec.rows) {
    const tr = element("tr");
    row.forEach((cell, index) => {
      tr.append(element(index === 0 ? "th" : "td",
        { text: cell, scope: index === 0 ? "row" : undefined }));
    });
    body.append(tr);
  }
  table.append(element("thead", {}, [head]), body);
  figure.append(table);
  return figure;
}

const TURN_STEP = 0.12;
const DRAG_SPEED = 0.0055;   // the record's own drag sensitivity, radians per pixel
const PITCH_LIMIT = 1.55;

/**
 * Mount one chapter's demo.
 *
 * Every number a step shows is in a table as text, whether or not it is also in the drawing, so the
 * page reads correctly with the pictures ignored entirely and by a screen reader. Nothing on it is
 * loaded from anywhere but this site.
 */
export async function mount(slug) {
  const root = document.querySelector("#demo");
  if (!root) throw new Error("the page has no #demo to mount into");

  const [engine, scaffold] = await Promise.all([
    openEngine(),
    fetch("steps.json").then((answer) => answer.json()),
  ]);
  const draw = drawings(engine);
  const definitions = chapterSteps(engine, draw)[slug];
  if (!definitions) throw new Error(`no demo for ${slug}`);
  const { chapter, steps } = joinSteps(slug, definitions(), scaffold);
  const view = draw.wireDefaultView();

  document.querySelector("#chapter-title").textContent = chapter.title;
  document.querySelector("#chapter-beats").textContent =
    `beats ${chapter.first}–${chapter.last}`;
  const back = document.querySelector("#back-to-chapter");
  if (back) back.setAttribute("href", `../${slug}.html`);

  const nav = element("nav", { class: "steps", "aria-label": "the beats" });
  const list = element("ol");
  const chips = steps.map((step, index) => {
    const button = element("button", {
      type: "button", text: String(step.beat), "aria-label": `${step.label}: ${step.title}`,
      title: step.title,
    });
    button.addEventListener("click", () => show(index));
    const item = element("li");
    item.append(button);
    list.append(item);
    return button;
  });
  nav.append(list);

  const stage = element("section", { class: "stage" });
  const heading = element("h2");
  const act = element("p", { class: "act" });
  const drawing = element("div", { class: "drawing" });
  const controls = element("div", { class: "controls" });
  const numbers = element("div", { class: "tables" });
  const still = element("div", { class: "still" });
  stage.append(heading, act, drawing, controls, numbers, still);

  const previous = element("button", { type: "button", text: "back", class: "walk" });
  const onward = element("button", { type: "button", text: "on", class: "walk" });
  const place = element("p", { class: "place", role: "status" });
  const walkers = element("div", { class: "walkers" });
  walkers.append(previous, place, onward);

  root.append(nav, stage, walkers);

  let current = 0;
  let state = initialState(steps[0], view);
  let playing = null;

  const stop = () => { if (playing !== null) { clearInterval(playing); playing = null; } };

  function draw3dHandlers() {
    const svg = drawing.querySelector("svg.wire");
    if (!svg) return;
    let dragging = null;
    const turn = (dx, dy) => {
      state.yaw += dx;
      state.pitch = Math.max(-PITCH_LIMIT, Math.min(PITCH_LIMIT, state.pitch + dy));
      render();
    };
    svg.addEventListener("pointerdown", (event) => {
      dragging = [event.clientX, event.clientY];
      svg.setPointerCapture(event.pointerId);
      svg.classList.add("dragging");
    });
    svg.addEventListener("pointermove", (event) => {
      if (!dragging) return;
      turn((event.clientX - dragging[0]) * DRAG_SPEED, (event.clientY - dragging[1]) * DRAG_SPEED);
      dragging = [event.clientX, event.clientY];
    });
    const release = () => { dragging = null; svg.classList.remove("dragging"); };
    svg.addEventListener("pointerup", release);
    svg.addEventListener("pointercancel", release);
    svg.addEventListener("keydown", (event) => {
      const moves = {
        ArrowLeft: [-TURN_STEP, 0], ArrowRight: [TURN_STEP, 0],
        ArrowUp: [0, -TURN_STEP], ArrowDown: [0, TURN_STEP],
      };
      const move = moves[event.key];
      if (!move) return;
      event.preventDefault();
      event.stopPropagation();
      turn(move[0], move[1]);
    });
  }

  function renderControls(step) {
    controls.replaceChildren();
    for (const control of step.controls) {
      if (control.kind === "numbers") {
        const group = element("div", { class: "typed" });
        control.names.forEach((name, index) => {
          const id = `number-${slug}-${step.beat}-${index}`;
          const label = element("label", { for: id, text: name });
          const input = element("input", {
            id, type: "text", inputmode: "text", size: "6",
            value: state.numbers[index], "aria-label": name,
          });
          input.addEventListener("change", () => {
            // Her own number, handed straight to the engine, which echoes it back with everything
            // it worked out from it. What the page will not accept is something that is not an
            // exact rational, because the engine has nothing to say about one.
            const typed = input.value.trim().replace(/[−–]/g, "-");
            if (/^-?\d+(\/\d+)?$/.test(typed) && !/\/0+$/.test(typed)) {
              state.numbers[index] = typed;
            }
            input.value = state.numbers[index];
            render();
          });
          group.append(label, input);
        });
        controls.append(group);
      }
      if (control.kind === "tick") {
        const label = element("span", { class: "tick-label" });
        label.textContent = `${control.noun} ${state.tick} of ${control.count}`;
        const backward = element("button", { type: "button", text: "←", "aria-label": "one back" });
        const forward = element("button", { type: "button", text: "→", "aria-label": "one on" });
        const play = element("button", { type: "button", text: playing === null ? "play" : "stop" });
        const reset = element("button", { type: "button", text: "again" });
        backward.disabled = state.tick === 0;
        forward.disabled = state.tick === control.count;
        backward.addEventListener("click", () => { stop(); state.tick -= 1; render(); });
        forward.addEventListener("click", () => { stop(); state.tick += 1; render(); });
        play.addEventListener("click", () => {
          if (playing !== null) { stop(); render(); return; }
          // One tick, a pause, the next tick. No easing and no tweening: the rule has no in-between,
          // and a drawing that slid between two ticks would be inventing one.
          playing = setInterval(() => {
            state.tick = state.tick === control.count ? 0 : state.tick + 1;
            render();
          }, 900);
          render();
        });
        reset.addEventListener("click", () => { stop(); state.tick = 0; render(); });
        controls.append(backward, label, forward, play, reset);
      }
      if (control.kind === "press") {
        const button = element("button", {
          type: "button", text: control.label, "aria-pressed": String(state.pressed),
        });
        button.addEventListener("click", () => { state.pressed = !state.pressed; render(); });
        controls.append(button);
      }
      if (control.kind === "choose") {
        const group = element("div", { class: "choose", role: "group" });
        control.options.forEach((option, index) => {
          const button = element("button", {
            type: "button", text: option.label,
            "aria-pressed": String(state.choice.index === index),
          });
          button.addEventListener("click", () => {
            state.choice = { ...option, index };
            render();
          });
          group.append(button);
        });
        controls.append(group);
      }
      if (control.kind === "turn") {
        const reset = element("button", { type: "button", text: "straighten it" });
        reset.addEventListener("click", () => {
          state.yaw = view.yaw;
          state.pitch = view.pitch;
          render();
        });
        controls.append(reset);
      }
    }
  }

  function render() {
    const step = steps[current];
    const rendered = step.render(state);
    heading.textContent = step.title;
    act.textContent = step.act;
    drawing.innerHTML = rendered.drawing;
    draw3dHandlers();
    renderControls(step);
    numbers.replaceChildren(...rendered.tables.map(renderTable));

    still.replaceChildren();
    const button = element("button", { type: "button", text: "still" });
    button.addEventListener("click", () => {
      const svg = stillFrom(rendered.drawing, {
        chapter: slug, beat: step.beats.join("–"), title: `${chapter.title} — ${step.label}`,
      });
      const blob = new Blob([`${svg}\n`], { type: "image/svg+xml" });
      const link = element("a", {
        href: URL.createObjectURL(blob),
        download: `${slug}-beat-${step.beat}.svg`,
        text: "download",
      });
      const source = element("details");
      source.append(element("summary", { text: "read it" }), element("pre", { text: svg }));
      still.replaceChildren(button, link, source);
    });
    still.append(button);

    chips.forEach((chip, index) => {
      chip.setAttribute("aria-current", index === current ? "step" : "false");
    });
    previous.disabled = current === 0;
    onward.disabled = current === steps.length - 1;
    place.textContent = `${step.label} · ${current + 1} of ${steps.length}`;
    document.title = `${chapter.title} · ${step.label} · Our Bubble`;
  }

  function show(index) {
    stop();
    current = Math.max(0, Math.min(steps.length - 1, index));
    state = initialState(steps[current], view);
    render();
    const hash = `#beat-${steps[current].beat}`;
    if (window.location.hash !== hash) window.history.replaceState(null, "", hash);
  }

  previous.addEventListener("click", () => show(current - 1));
  onward.addEventListener("click", () => show(current + 1));
  document.addEventListener("keydown", (event) => {
    if (event.target instanceof HTMLElement
      && ["INPUT", "TEXTAREA", "SELECT", "BUTTON"].includes(event.target.tagName)) return;
    if (event.key === "ArrowRight" || event.key === "j") { show(current + 1); event.preventDefault(); }
    if (event.key === "ArrowLeft" || event.key === "k") { show(current - 1); event.preventDefault(); }
  });

  const requested = /^#beat-(\d+)$/.exec(window.location.hash || "");
  const start = requested
    ? steps.findIndex((step) => step.beats.includes(Number(requested[1])))
    : 0;
  show(start < 0 ? 0 : start);
  return { steps, show };
}

/** The index page's list of demos, built from the same scaffolding the pages are. */
export async function mountIndex() {
  const scaffold = await fetch("steps.json").then((answer) => answer.json());
  const list = document.querySelector("#demo-index");
  if (!list) return;
  for (const [slug, chapter] of Object.entries(scaffold.chapters)) {
    const item = element("li");
    const link = element("a", { href: `${slug}.html`, text: chapter.title });
    const beats = element("span", { class: "beats", text: `beats ${chapter.first}–${chapter.last}` });
    item.append(link, beats);
    list.append(item);
  }
}

/** The theme switch: the reader's system by default, her choice remembered for this site only. */
export function themeSwitch(host) {
  const key = "our-bubble-demo-theme";
  let stored = null;
  try { stored = window.localStorage.getItem(key); } catch { stored = null; }
  const apply = (value) => {
    if (value === "light" || value === "dark") document.documentElement.dataset.theme = value;
    else delete document.documentElement.dataset.theme;
  };
  apply(stored);
  const select = element("select", { "aria-label": "theme" });
  for (const [value, text] of [["system", "theme"], ["light", "light"], ["dark", "dark"]]) {
    const option = element("option", { value, text });
    if ((stored || "system") === value) option.selected = true;
    select.append(option);
  }
  select.addEventListener("change", () => {
    apply(select.value === "system" ? null : select.value);
    try {
      if (select.value === "system") window.localStorage.removeItem(key);
      else window.localStorage.setItem(key, select.value);
    } catch { /* a reader with storage off still gets the switch, just not the memory */ }
  });
  host.append(select);
}
