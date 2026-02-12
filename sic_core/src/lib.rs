//! # SIC Core — Integrative Contextual Synthesis Metalanguage
//!
//! Rust formalization of the SIC metalanguage. The type system enforces
//! the axioms at compile time:
//!
//! - **Ownership** = Contextual exclusivity (one owner per entity)
//! - **Lifetimes** = Temporal decay (entities die when their context dies)
//! - **Borrow checker** = Safe event propagation (no dangling references)
//! - **Traits** = Context interfaces (activation conditions, processing)

pub mod context;
pub mod entity;
pub mod coherence;
pub mod operators;
pub mod events;
pub mod nested_learning;
