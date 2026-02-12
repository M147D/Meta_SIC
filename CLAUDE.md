# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Metalenguaje de Síntesis Integrativa Contextual (SIC)** — a formal mathematical metalanguage for unifying phenomena across contexts, scales, and perspectives. Developed collaboratively by Miguel and Claude.

This is a theoretical/specification project with implementations in Rust, Python, and Arduino. All content available in **Spanish** and **English**.

## File Structure

- **Definiciones.md** / **Definitions.md** (Sections 1–15): Core formal framework — axioms (including coherence axioms 4-7), operators (`⊕`, `×`, `∘`) with resolved `⊕_P` composition, contextual calculus with continuous parametrization, dynamic equations, metrics, theorems, contextual entanglement and reality collapse (§11), inference rules, and the Context Algebra (`E{C,S,P}` entities as commutative monoid).
- **Aplicaciones.md** / **Applications.md** (Section 16–17): Computational implementation — Nested Learning concept, event-driven architecture, Arduino/C++ light follower project, Rust formalization strategy, and implementation roadmap.
- **sic_core/**: Rust formalization — type-safe context system where ownership=contextual exclusivity, lifetimes=temporal decay, borrow checker=safe event propagation. Modules: `context`, `entity`, `coherence`, `operators`, `events`, `nested_learning`. Run: `cargo run --example demo`.
- **simulacion_sic/**: Python simulation of the Universal Coherence Matrix 𝕄 — builds coherence matrix, applies friction, finds clusters, computes collapse, visualizes results. Run: `python simulacion_sic.py --entities 20 --friction 0.15`.
- **seguidor_luz_sic/seguidor_luz_sic.ino**: Working Arduino sketch — event-driven light follower with three nested contexts (reactive, adaptive, environmental).

Sections are numbered continuously across both files (Definiciones: 1–15, Aplicaciones: 16–17).

## Core Concepts

The metalanguage operates on **Contextual Entities** `E{C, S, P}` where:
- **C** = Context (physical, social, conceptual, quantum...)
- **S** = Scale (quantum, microscopic, human, cosmic...)
- **P** = Perspective (objective, subjective, deterministic, statistical...)

Nine foundational axioms:
- Axioms 1-3: Contextual Coherence, Transformability, Constitutive Perspective
- Axioms 4-7: Coherence properties (Reflexivity, Symmetry, Bounded Transitivity, Preservation under Transformation)
- Axiom 8: Friction (every context change generates friction subtracted from internal update capacity)
- Axiom 9: Relative Perception (apparent reality topology depends on observer's friction threshold ε_obs)

Key formalizations:
- **`⊕_P`**: Independent perspective composition (resolves circularity in `⊕`)
- **Contextual Friction `Φ`**: `Φ(A,B) = 1 - Coh(A,B)`, Processing Budget, Resonant Efficiency Corollary, Tunnel Effect (§7.6)
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
| 2: Formalization | Rust (`sic_core/`) | Type-safe metalanguage formalization | In Progress |
| 2.5: Simulation | Python (`simulacion_sic/`) | Coherence matrix visualization & analysis | Working |
| 3: Applications | Rust/WASM | Production systems (monitoring, security, data pipelines) | Pending |

## Rust Crate: sic_core

Build: `cd sic_core && cargo build`
Run demo: `cargo run --example demo`
Modules: `context.rs` (Context, Scale, Perspective), `entity.rs` (Entity<'ctx>), `coherence.rs` (Coh, 𝕄, friction, clusters), `operators.rs` (⊕, ×, T), `events.rs` (EventQueue), `nested_learning.rs` (ContextProcessor trait, three nested contexts).

## Python Simulation: simulacion_sic

Install: `pip install -r simulacion_sic/requirements.txt`
Run: `python simulacion_sic/simulacion_sic.py --entities 20 --friction 0.15`
CLI-only: add `--no-plot`

## Arduino Sketch: seguidor_luz_sic

Hardware: Arduino Uno/Nano/ESP32, 2x LDR (A0/A1 with 10kΩ pull-down), 1x Servo SG90 (Pin 9).
The sketch outputs CSV data via Serial (9600 baud) for monitoring with Serial Plotter.

## Editing Guidelines

- Maintain continuous section numbering across both files
- Preserve mathematical notation (Unicode symbols: `⊕`, `×`, `∘`, `⟹`, `≡`, `∂`, `∫`, `∇`, `∮`, `Ψ`, `Ω`)
- Keep the event-driven paradigm consistent — no polling/fixed-frequency patterns
- Code examples in Aplicaciones.md are conceptual/pseudocode, not standalone runnable files
- The Arduino sketch in `seguidor_luz_sic/` is a compilable .ino file
- All .md files use UTF-8 encoding
