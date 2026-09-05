#!/usr/bin/env python3
"""R10 figure build: embed ../data/lattice.json (written by the gate) verbatim into
tetoct-render.template.html -> tetoct-render.html. Pure substitution, no data edits."""
from pathlib import Path

here = Path(__file__).parent
data = (here / ".." / "data" / "lattice.json").read_text().strip()
tpl = (here / "tetoct-render.template.html").read_text()
assert "__LATTICE_JSON__" in tpl
(here / "tetoct-render.html").write_text(tpl.replace("__LATTICE_JSON__", data))
print("wrote", here / "tetoct-render.html", "with", len(data), "bytes of lattice data")
