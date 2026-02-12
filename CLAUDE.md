# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Metalenguaje de Síntesis Integrativa Contextual (SIC)** — a formal mathematical metalanguage for unifying phenomena across contexts, scales, and perspectives. Developed collaboratively by Miguel and Claude.

This is a theoretical/specification project with a working Arduino implementation. All content available in **Spanish** and **English**.

## File Structure

- **Definiciones.md** / **Definitions.md** (Sections 1–15): Core formal framework — axioms (including coherence axioms 4-7), operators (`⊕`, `×`, `∘`) with resolved `⊕_P` composition, contextual calculus with continuous parametrization, dynamic equations, metrics, theorems, contextual entanglement and reality collapse (§11), inference rules, and the Context Algebra (`E{C,S,P}` entities as commutative monoid).
- **Aplicaciones.md** / **Applications.md** (Section 16–17): Computational implementation — Nested Learning concept, event-driven architecture, Arduino/C++ light follower project, Rust formalization strategy, and implementation roadmap.
- **seguidor_luz_sic/seguidor_luz_sic.ino**: Working Arduino sketch — event-driven light follower with three nested contexts (reactive, adaptive, environmental). Compiles for Arduino Uno/Nano/ESP32.

The sections are numbered continuously across both files (Definiciones: 1–15, Aplicaciones: 16–17).

## Core Concepts

The metalanguage operates on **Contextual Entities** `E{C, S, P}` where:
- **C** = Context (physical, social, conceptual, quantum...)
- **S** = Scale (quantum, microscopic, human, cosmic...)
- **P** = Perspective (objective, subjective, deterministic, statistical...)

Seven foundational axioms:
- Axioms 1-3: Contextual Coherence, Transformability, Constitutive Perspective
- Axioms 4-7: Coherence properties (Reflexivity, Symmetry, Bounded Transitivity, Preservation under Transformation)

Key formalizations:
- **`⊕_P`**: Independent perspective composition (resolves circularity in `⊕`)
- **Continuous parametrization**: Contexts as `(type, θ₁, ..., θₙ)` tuples enabling computable derivatives
- **Perspectival dependency**: Parametrization is relative to `P_ref`; contextual curvature tensor `𝒦` (§7.2)
- **Phase transitions**: Jump operator `Δ` and distributional derivative for discontinuous contexts (§7.5)
- **Contextual entanglement**: Universal coherence matrix `𝕄`, local/percolative collapse with friction `ε` (§11)
- **Inference rules**: Modus ponens contextual, transfer, composition, scale change
- **Algebraic structure**: `(𝔈, ⊕)` is a commutative monoid (inverses exist conditionally)
- **Twin Paradox**: Time dilation derived as contextual friction without explicit relativity (§14.5)

## Architecture: Nested Learning System

The implementation architecture uses three nested contexts at different timescales:

```
Reactive Context  {C:immediate, S:ms, P:hardware}     — direct sensor→actuator
    ↕
Adaptive Context  {C:patterns, S:seconds, P:statistical} — adjusts reactive parameters
    ↕
Environmental Context {C:environment, S:minutes, P:strategic} — adjusts adaptive limits
```

Key design principle: **event-driven propagation** (no fixed-frequency loops, no `delay()`). Events propagate through contexts that "resonate" based on activation conditions, with memory that decays exponentially over time.

## Implementation Phases

| Phase | Language | Purpose | Status |
|-------|----------|---------|--------|
| 1: Tangible | C/C++ (Arduino) | Hardware validation — light follower robot | Working sketch |
| 2: Formalization | Rust | Formal metalanguage interpreter, type-safe context system | Pending |
| 3: Applications | Rust/WASM | Production systems (monitoring, security, data pipelines) | Pending |

## Arduino Sketch: seguidor_luz_sic

Hardware requirements:
- Arduino Uno/Nano/ESP32
- 2x LDR on A0, A1 (with 10kΩ pull-down)
- 1x Servo SG90 on Pin 9

The sketch outputs CSV data via Serial (9600 baud) for monitoring with Serial Plotter.

## Editing Guidelines

- Maintain continuous section numbering across both files
- Preserve mathematical notation (Unicode symbols: `⊕`, `×`, `∘`, `⟹`, `≡`, `∂`, `∫`, `∇`, `∮`, `Ψ`, `Ω`)
- Keep the event-driven paradigm consistent — no polling/fixed-frequency patterns
- Code examples in Aplicaciones.md are conceptual/pseudocode, not standalone runnable files
- The Arduino sketch in `seguidor_luz_sic/` is a compilable .ino file
- All .md files use UTF-8 encoding
