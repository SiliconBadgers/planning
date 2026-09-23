# Planning and current team work

Track current assignments and accepted decisions while preserving the dated technical plan, model budgets and original charter snapshots as historical evidence.

## Start here

1. Read [the current assignment and artifact locations](docs/START-HERE.md).
2. Complete [AI setup and the capture check](docs/git-ai.md) before AI edits or
   your first commit. Every clone needs its local hook activated.
3. Work on a branch and open a PR for `@abhinavnandwani` using
   [CONTRIBUTING.md](CONTRIBUTING.md). Main requires a code-owner approval;
   admins can bypass.

## Repository structure

| Location | Purpose |
|---|---|
| [docs/](docs/README.md) | Current team map and planning updates. Historical plan sources and snapshots remain at their existing locations. |

## Current material and scope

The historical plan and offline reader are reproducible. The current team map supersedes historical organization guidance for active assignments.

[Shared diagram](https://github.com/SiliconBadgers/architecture/blob/main/docs/accelerator-diagram.md) · [Software evidence](https://github.com/SiliconBadgers/software/tree/main/experiments/llama-cpp/2026-09-22)

Read [the current seven-team map](docs/team-start.md). The [dated plan](PLAN.md),
[technical source](technical-plan.md), [organization source](plan-source.md),
[budgets](budget-tables.md), and [source snapshots](sources/README.md) preserve
historical context. The eleven-charter snapshot is not today's team structure.

## Rebuild the historical plan

```sh
gh repo clone SiliconBadgers/planning
cd planning
python3 build.py
python3 serve.py
```

Python 3.11+ is sufficient; no model weights or network are needed for the build.
The server binds to 127.0.0.1 only. Edit the source Markdown or reader assets, run
`build.py`, and include regenerated PLAN.md, index.html, budgets and hashes in
the PR. Preserve provenance in repository-snapshot.json and sources/.
