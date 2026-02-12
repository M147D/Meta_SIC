//! SIC Operators — Section 6
//!
//! ⊕  Contextual Composition (consumes both operands → monoid, not group)
//! ×  Scalar Modulation
//! T  Context Transformation

use crate::coherence::coherence;
use crate::context::Context;
use crate::entity::{Entity, OwnedEntity};

/// Contextual Composition ⊕ (Section 6.1.2).
///
/// E₁{C₁,S₁,P₁} ⊕ E₂{C₂,S₂,P₂} = E₃{C₁∪C₂, S₁∩S₂, P₁ ⊕_P P₂}
///
/// This CONSUMES both entities and produces a new owned entity.
/// The irreversibility models the commutative monoid structure:
/// you can compose freely, but cannot always decompose.
pub fn compose(e1: &Entity, e2: &Entity) -> OwnedEntity {
    let coh = coherence(e1.context, e2.context);

    OwnedEntity {
        context: e1.context.union(e2.context),
        scale: e1.scale.intersect(&e2.scale),
        perspective: e1.perspective.compose(&e2.perspective, coh),
        intensity: e1.intensity + e2.intensity,
    }
}

/// Scalar Modulation α × E (Section 6.2).
///
/// α × E{C,S,P} = E{C,S,P, I:α}
pub fn modulate<'a>(alpha: f64, entity: &Entity<'a>) -> Entity<'a> {
    entity.modulate(alpha)
}

/// Context Transformation T (Section 2.2).
///
/// Transforms an entity from one context to another,
/// with a coherence factor measuring information loss.
pub fn transform(entity: &Entity, target_context: &Context) -> OwnedEntity {
    let coh = coherence(entity.context, target_context);

    OwnedEntity {
        context: target_context.clone(),
        scale: entity.scale.clone(),
        perspective: entity.perspective.clone(),
        // Intensity attenuated by coherence (information loss)
        intensity: entity.intensity * coh,
    }
}

/// Contextual Equivalence ≡{C} (Section 3.2).
///
/// Two entities are contextually equivalent if they have the same
/// context kind and their parameter distance is below a threshold.
pub fn contextually_equivalent(e1: &Entity, e2: &Entity, threshold: f64) -> bool {
    e1.context.kind == e2.context.kind && e1.context.distance(e2.context) < threshold
}
