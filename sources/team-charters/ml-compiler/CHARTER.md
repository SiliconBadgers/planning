# ML compiler and runtime: team charter

## Purpose

Make the accelerator understandable and usable for machine-learning workloads through software. The team connects intended workloads and algorithms to hardware capabilities through programming abstractions, mappings and runtime behavior that members can investigate, explain and develop.

An accelerator’s value depends in part on how people express useful work and understand its execution. This team explores that software/hardware relationship, from programming-model questions and algorithm mappings to compilers, libraries, runtimes and host tools when those approaches are appropriate.

## Responsibilities

### Programming experience

Study what users and workload developers need to express, observe and control. Develop explanations and abstractions that connect user intent to supported hardware behavior.

### Workload mapping

Investigate how operations, data layouts and execution choices map onto accelerator capabilities. Compare approaches using both numerical meaning and system constraints.

### Software realization

Own compiler, assembly, code generation, runtime and host software responsibilities selected by the team. Maintain a clear distinction between proposed abstractions, implemented capabilities and unsupported behavior.

### Software/hardware agreement

Participate in defining command and data semantics with architecture and hardware teams. Explain how software depends on those semantics and provide feedback when hardware choices affect usability.

## Boundaries and shared decisions

This team owns the software-facing path to accelerator use. Architecture stewards shared execution and data semantics; ml-models supplies numerical reference behavior; control realizes execution; SoC provides hardware-visible access. FPGA owns platform-specific transport integration, with the software API boundary agreed together. The team is free to choose a compiler, a smaller runtime, research artifacts or other approaches appropriate to the current questions.

## Member autonomy

Members can investigate programming abstractions, study lowering strategies, compare data layouts, build examples, improve diagnostics, prototype a runtime or develop compiler infrastructure. They choose methods and scope based on their interests and the charter. A language, framework, ISA encoding or software stack is not selected by this scaffold. Changes to shared semantics require agreement with their hardware and model counterparts.

## Collaboration

| Partners | Shared concerns |
|---|---|
| architecture and ml-models | Connect workload meaning, numerical expectations and user needs to shared operation and data definitions. |
| rtl-control and soc | Agree on execution and access behavior, including the information software needs to reason about progress and results. |
| fpga, verification and accelerator | Use platform feedback and system experiments to assess usability and correctness from the software side. |

## Possible directions

Members might explore a programming model, explain an operator mapping, compare layouts, develop a software example, study compiler techniques or investigate runtime observability. A useful result may be an analysis or design proposal before there is a reason to implement a full toolchain.

## What progress means

Progress means the path from user intent to accelerator behavior becomes clearer and more useful. Evidence can include workload mappings, usable examples, comparisons of abstractions, tested software or a documented limitation that changes a design decision.

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
