//! Context, Scale, and Perspective — the three dimensions of E{C, S, P}
//!
//! Contexts are parametrized as continuous tuples (Section 7.1):
//!   C = (kind, θ₁, θ₂, ..., θₙ)  where θᵢ ∈ ℝ
//!
//! The parametrization is relative to a reference perspective P_ref (Section 7.2).

use std::collections::HashMap;

/// The kind of context — extensible classification.
#[derive(Debug, Clone, PartialEq)]
pub enum ContextKind {
    Physical,
    Social,
    Conceptual,
    Quantum,
    Thermal,
    Inertial,
    Accelerated,
    Custom(String),
}

/// A Context with continuous parametrization.
///
/// Owns its parameters — only one context can hold these values at a time.
/// This models contextual exclusivity via Rust's ownership system.
#[derive(Debug, Clone)]
pub struct Context {
    pub kind: ContextKind,
    /// Continuous parameters θᵢ ∈ ℝ (Section 7.1)
    pub params: HashMap<String, f64>,
}

impl Context {
    pub fn new(kind: ContextKind) -> Self {
        Self {
            kind,
            params: HashMap::new(),
        }
    }

    /// Create a context with parameters.
    /// Example: Context::with_params(Thermal, [("temperature", 25.0), ("pressure", 1.0)])
    pub fn with_params(kind: ContextKind, params: &[(&str, f64)]) -> Self {
        let mut map = HashMap::new();
        for (key, val) in params {
            map.insert(key.to_string(), *val);
        }
        Self { kind, params: map }
    }

    /// Get a parameter value, or 0.0 if not set.
    pub fn param(&self, name: &str) -> f64 {
        self.params.get(name).copied().unwrap_or(0.0)
    }

    /// Contextual distance to another context (Section 9.1).
    /// d(C₁, C₂) = √(Σ |θᵢ₁ - θᵢ₂|²) over shared parameters.
    pub fn distance(&self, other: &Context) -> f64 {
        let mut sum_sq = 0.0;
        // Compare shared parameters
        for (key, val) in &self.params {
            let other_val = other.params.get(key).copied().unwrap_or(0.0);
            sum_sq += (val - other_val).powi(2);
        }
        // Parameters in other but not in self
        for (key, val) in &other.params {
            if !self.params.contains_key(key) {
                sum_sq += val.powi(2);
            }
        }
        sum_sq.sqrt()
    }

    /// Context union C₁ ∪ C₂ — for the ⊕ operator.
    /// Takes the union of parameters, averaging shared ones.
    pub fn union(&self, other: &Context) -> Context {
        let mut params = self.params.clone();
        for (key, val) in &other.params {
            params
                .entry(key.clone())
                .and_modify(|v| *v = (*v + val) / 2.0)
                .or_insert(*val);
        }
        Context {
            kind: self.kind.clone(), // inherit from left operand
            params,
        }
    }
}

/// Scale — the observation level.
#[derive(Debug, Clone, PartialEq)]
pub enum Scale {
    Quantum,
    Microscopic,
    Mesoscopic,
    Human,
    Cosmic,
    /// Custom scale with a characteristic size parameter.
    Custom(String, f64),
}

impl Scale {
    /// Scale intersection S₁ ∩ S₂ — for the ⊕ operator.
    /// Returns the more restrictive (finer) scale.
    pub fn intersect(&self, other: &Scale) -> Scale {
        let rank = |s: &Scale| -> u8 {
            match s {
                Scale::Quantum => 0,
                Scale::Microscopic => 1,
                Scale::Mesoscopic => 2,
                Scale::Human => 3,
                Scale::Cosmic => 4,
                Scale::Custom(_, _) => 3,
            }
        };
        if rank(self) <= rank(other) {
            self.clone()
        } else {
            other.clone()
        }
    }
}

/// Perspective — the observer's viewpoint.
///
/// Axiom 3: Perspective is constitutive of manifested reality.
/// R{C,S,P₁} ≠ R{C,S,P₂} when P₁ ≠ P₂
#[derive(Debug, Clone)]
pub struct Perspective {
    pub kind: PerspectiveKind,
    /// Weight for composition (Section 6.1.1)
    pub weight: f64,
}

#[derive(Debug, Clone, PartialEq)]
pub enum PerspectiveKind {
    Objective,
    Subjective,
    Intersubjective,
    Deterministic,
    Statistical,
    Custom(String),
}

impl Perspective {
    pub fn new(kind: PerspectiveKind) -> Self {
        Self { kind, weight: 1.0 }
    }

    /// Perspective composition ⊕_P (Section 6.1.1).
    ///
    /// If Coh(P₁, P₂) > θ → weighted fusion (compatible)
    /// If Coh(P₁, P₂) ≤ θ → irreducible compound (coexist without fusing)
    pub fn compose(&self, other: &Perspective, coherence: f64) -> Perspective {
        let theta = 0.5; // fusion threshold
        if coherence > theta {
            // Weighted fusion
            let total = self.weight + other.weight;
            Perspective {
                kind: self.kind.clone(),
                weight: total * coherence,
            }
        } else {
            // Irreducible compound — keep the dominant one
            if self.weight >= other.weight {
                Perspective {
                    kind: self.kind.clone(),
                    weight: self.weight,
                }
            } else {
                Perspective {
                    kind: other.kind.clone(),
                    weight: other.weight,
                }
            }
        }
    }
}
