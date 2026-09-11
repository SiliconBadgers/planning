# System integration and shared project understanding: team charter

## Purpose

Help the separate teams form a coherent accelerator project and understand what the combined system can actually do. This repository holds the system-level context, integration knowledge and shared evidence that connect individual team contributions.

The system can have properties and limitations that are not visible in one repository. This team brings component work into a common context, makes dependencies understandable and helps the group interpret demonstrations and measurements. Integration tooling is one possible means of doing that; the charter is broader than infrastructure maintenance.

## Responsibilities

### Combined-system understanding

Maintain an accessible view of how capabilities, assumptions and interfaces from separate teams fit together. Explain system configurations and identify integration questions that cross repository boundaries.

### Shared evidence and demonstrations

Develop and interpret combined-system experiments that illuminate behavior or support agreed claims. Distinguish demonstrated capability from planned work and local component results.

### Coordination through clarity

Make cross-team dependencies and unresolved assumptions visible, helping the relevant teams agree on compatible changes and shared ambitions. Preserve the reasoning behind those agreements.

### Reproducible integration knowledge

Maintain the context needed to revisit system results, including configurations, methods, dependencies and limitations. Tooling and runbooks serve that understanding when they are useful.

## Boundaries and shared decisions

Accelerator owns the cross-repository system view and integration context. Architecture stewards intended system semantics and architectural tradeoffs; soc owns composed hardware; individual teams own their research and implementations; verification owns independent assessment. This repository does not assign work to other teams or centralize copies of their source. Shared milestones are selected together by the participating teams.

## Member autonomy

Members may investigate a system interaction, compare configurations, explain dependencies, design a demonstration, analyze system measurements or improve integration reproducibility. They choose the questions and methods within this charter. Demonstrations, priorities and claims that depend on other teams are agreed with those teams. The existing MAC runner is an optional example of integration and does not set a required project roadmap.

## Collaboration

| Partners | Shared concerns |
|---|---|
| architecture and all component teams | Connect intended behavior with actual capabilities and assumptions, and make incompatibilities visible to the teams able to resolve them. |
| ml-models, ml-compiler and verification | Relate workload meaning, software use and independent evidence to combined-system behavior. |
| fpga and physical-design | Interpret platform and implementation observations in their proper system context, including the limits of comparison between targets. |

## Possible directions

Members might explain the current dependency structure, compare a pair of system configurations, investigate a cross-block mismatch, develop a meaningful demonstration, study performance attribution or improve how results are communicated. Infrastructure work is useful when it enables one of these outcomes.

## What progress means

Progress means members can understand the combined system, reproduce and interpret meaningful results, and agree on changes without relying on hidden assumptions. A clarified dependency, a discovered integration limitation or a carefully scoped demonstration can all advance the charter.

Leads help members interpret this purpose, find collaborators, access resources
and share what they learn. Members choose their questions and contributions.
Research, design reasoning, experiments, implementation, documentation and
teaching can all advance the charter; success is not measured by the number of
code changes or completed tickets.

The team can revise this charter as its understanding evolves. Changes to a
shared boundary or commitment are discussed with the teams affected by them.
The [objectives](OBJECTIVES.md) describe durable outcomes, and the
[repository structure](README.md#repository-structure) provides places to develop
work without specifying a mandatory project or sequence.
