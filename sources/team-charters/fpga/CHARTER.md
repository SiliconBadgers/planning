# FPGA prototyping and hardware exploration: team charter

## Purpose

Use FPGA platforms to explore, demonstrate and understand accelerator behavior in a physical system. The team connects design ideas to practical hardware experience and feeds platform observations back into the wider project.

Prototyping helps reveal assumptions about clocks, IO, memory, software interaction and observability that may be difficult to see in isolated simulation. The team contributes through platform studies, experiments, system adaptation, measurement, demonstrations and explanations of what hardware evidence means.

## Responsibilities

### Platform understanding

Investigate available boards, tools, resources and interfaces in relation to the project’s interests and constraints. Explain the opportunities and limitations of a chosen platform.

### Board adaptation

Own board-specific shells, connections, constraints and host transport adaptation. Make the relationship between reusable accelerator logic and target-specific implementation explicit.

### Physical experimentation

Develop ways to observe and investigate behavior on hardware, including bring-up, measurement and reproducible demonstrations where useful. Distinguish simulated, built and observed hardware results.

### Shared practical knowledge

Preserve setup knowledge, experiments, limitations and lessons so members can learn from and extend physical prototypes without depending on undocumented experience.

## Boundaries and shared decisions

FPGA owns board-specific adaptation and prototyping. soc owns reusable chip-level composition; RTL teams own block implementations; ml-compiler owns software abstractions, with the transport boundary agreed together. Architecture interprets platform constraints as one input to system design. Physical-design studies ASIC implementation, whose results are distinct from FPGA resource and timing observations.

## Member autonomy

Members may investigate a board capability, compare platforms, study a transport, develop instrumentation, perform a hardware experiment or create a teaching demonstration. The team chooses the scale and form of its prototypes within available resources. New platform commitments and changes to shared hardware/software interfaces are discussed with the affected teams. No board, vendor toolchain or mandatory demonstration is selected by the scaffold.

## Collaboration

| Partners | Shared concerns |
|---|---|
| soc and RTL teams | Agree on the boundary between reusable design and board-specific behavior, and return feedback from target constraints and observations. |
| ml-compiler and verification | Connect host use and observed hardware behavior to software expectations and independent correctness evidence. |
| architecture and accelerator | Share platform capabilities, practical limits and interpreted measurements that can guide design choices and system demonstrations. |

## Possible directions

Members might investigate memory access on a board, compare transport choices, explore hardware observability, create a small physical demonstration, analyze timing reports or document platform behavior. A feasibility study can be a useful contribution even when hardware access limits implementation work.

## What progress means

Progress means the project learns something defensible from its interaction with hardware, can distinguish observation from assumption, and can reuse the practical knowledge gained. A clear platform comparison, a measured limitation or an accessible demonstration can all advance the charter.

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
