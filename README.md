# SiliconBadgers planning

The shared technical and organizational plan for a Qwen3.5-2B accelerator with
four-bit weights. It brings together inference-stage tradeoffs, numerical
choices, resource budgets and the charters of eleven engineering teams.

**Start with [the complete plan](PLAN.md).** The baseline is Qwen3.5-2B;
INT4, MXFP4 and NVFP4 are explicit alternatives. Performance figures are
analytical estimates until supported by measured evidence.

| Material | Where to find it |
|---|---|
| Complete readable plan | [PLAN.md](PLAN.md) |
| Offline HTML reader | [index.html](index.html), opened locally after cloning |
| Technical discussion source | [technical-plan.md](technical-plan.md) |
| Organizational direction source | [plan-source.md](plan-source.md) |
| Calculated budgets and assumptions | [budget-tables.md](budget-tables.md) and [model-budget.json](model-budget.json) |
| Calculation implementation | [model_budget.py](model_budget.py) |
| Checkpoint and reference provenance | [sources/README.md](sources/README.md) |
| Included team charter snapshots | [sources/team-charters/README.md](sources/team-charters/README.md) |

The plan supplies context and high-level objectives. Members choose their
contributions, which can include research, design reasoning, experiments,
implementation, documentation and teaching. Each team's repository remains
authoritative for its own charter and accepted technical work.

## Read and rebuild

Clone this private repository using your organization access:

```sh
gh repo clone SiliconBadgers/planning
cd planning
python3 build.py
python3 serve.py
```

Python 3.11 or newer is the only build dependency. Open the loopback address
printed by `serve.py`; press Ctrl+C to stop it. The server binds only to
`127.0.0.1`. You can also open `index.html` directly from disk. GitHub displays
the HTML source, so use `PLAN.md` to read the plan on GitHub.

The HTML contains its styles and scripts and works offline. It includes chapter
navigation, a searchable library of all eleven charters, expand/collapse,
Markdown download and print/PDF support. Links to private source repositories
require access. The local preview server provides no public hosting.

The build uses included source files and pinned snapshots. No sibling checkout,
model weights, package installation or network connection is needed to rebuild.
It regenerates `PLAN.md`, `index.html`, `model-budget.json`, `budget-tables.md`
and `source-hashes.json`.

## Develop the plan

Edit `technical-plan.md` for the Qwen baseline, inference stages, numerical
tradeoffs and hardware discussion. Edit `plan-source.md` for organization,
team objectives and shared decisions. Placeholders assemble the technical
chapters, calculated tables, charter library and recorded revision table.
Edit `reader.css` or `reader.js` to change the HTML reader, then rebuild.

Run `python3 build.py`, inspect the readable outputs, and include both the
edited sources and regenerated files in a proposed revision. Direct edits to
generated files are replaced on the next build. Keep facts, adopted decisions,
proposals and estimates clearly distinguished, and retain source attribution.

The renderer supports headings, paragraphs, links, inline code and bold, flat
lists, tables and fenced code. Embedded HTML is escaped. The builder and local
server do not create commits, push changes or deploy the reading view.

## Maintain provenance

`repository-snapshot.json` records the eleven team repositories at their
verified initial revisions. It describes those revisions, not the current
history of every repository. The included charter/objective files and
`sources/team-manifest.json` make this repository independently rebuildable.
See [snapshot maintenance](sources/team-charters/README.md) before refreshing
them. This repository is the separate planning home, not a twelfth team charter.

`source-hashes.json` records the plan and charter inputs used by the latest
build. `model-budget.json` also records hashes of source metadata. Refresh the
model configuration, tensor inventory, calculations and affected contracts
together when adopting another checkpoint or numerical policy.
