//! Contextual Entity E{C, S, P} — Section 2.1
//!
//! The fundamental object of SIC. An entity exists relative to a Context,
//! Scale, and Perspective.
//!
//! KEY DESIGN: Entity borrows its Context with a lifetime 'ctx.
//! When the Context is dropped, all Entities referencing it become invalid.
//! This is enforced at COMPILE TIME by Rust's borrow checker — modeling
//! the SIC axiom that entities cannot outlive their context.

use crate::context::{Context, Perspective, Scale};

/// A Contextual Entity E{C, S, P}.
///
/// The lifetime `'ctx` ties the entity to its context. The entity cannot
/// outlive the context — if the context is dropped, the entity is invalid.
/// This is the Rust embodiment of "temporal decay" (Section 7.5).
#[derive(Debug, Clone)]
pub struct Entity<'ctx> {
    /// Borrowed reference to the context — entity does NOT own its context.
    /// Multiple entities can share a context (immutable borrow).
    pub context: &'ctx Context,
    pub scale: Scale,
    pub perspective: Perspective,
    /// Intensity parameter I:α (Section 6.2)
    pub intensity: f64,
}

impl<'ctx> Entity<'ctx> {
    /// Create a new contextual entity.
    pub fn new(
        context: &'ctx Context,
        scale: Scale,
        perspective: Perspective,
    ) -> Self {
        Self {
            context,
            scale,
            perspective,
            intensity: 1.0,
        }
    }

    /// Create an entity with intensity.
    pub fn with_intensity(
        context: &'ctx Context,
        scale: Scale,
        perspective: Perspective,
        intensity: f64,
    ) -> Self {
        Self {
            context,
            scale,
            perspective,
            intensity,
        }
    }

    /// Scalar modulation α × E (Section 6.2).
    /// α × E{C,S,P} = E{C,S,P, I:α}
    pub fn modulate(&self, alpha: f64) -> Entity<'ctx> {
        Entity {
            context: self.context,
            scale: self.scale.clone(),
            perspective: self.perspective.clone(),
            intensity: self.intensity * alpha,
        }
    }
}

/// An owned entity that holds its own context.
/// Used when composition (⊕) creates a new entity with a new context
/// that doesn't exist as a separate borrowed reference.
#[derive(Debug, Clone)]
pub struct OwnedEntity {
    pub context: Context,
    pub scale: Scale,
    pub perspective: Perspective,
    pub intensity: f64,
}

impl OwnedEntity {
    pub fn new(context: Context, scale: Scale, perspective: Perspective) -> Self {
        Self {
            context,
            scale,
            perspective,
            intensity: 1.0,
        }
    }

    /// Borrow as a regular Entity (with lifetime tied to self).
    pub fn as_entity(&self) -> Entity<'_> {
        Entity {
            context: &self.context,
            scale: self.scale.clone(),
            perspective: self.perspective.clone(),
            intensity: self.intensity,
        }
    }
}
