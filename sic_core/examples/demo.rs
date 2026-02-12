//! SIC Metalanguage — Demo
//!
//! Run with: cargo run --example demo
//!
//! Demonstrates:
//!   1. Entity creation with lifetimes (compile-time safety)
//!   2. Contextual composition ⊕
//!   3. Coherence metrics
//!   4. Universal Coherence Matrix with friction and clustering
//!   5. Nested Learning system with event propagation

use sic_core::coherence::{coherence, CoherenceMatrix};
use sic_core::context::*;
use sic_core::entity::Entity;
use sic_core::nested_learning::NestedLearningSystem;
use sic_core::operators;

fn main() {
    println!("=================================================");
    println!("  SIC Metalanguage — Rust Formalization Demo");
    println!("=================================================\n");

    // -------------------------------------------------------
    // 1. Contextual Entities with Lifetimes
    // -------------------------------------------------------
    println!("--- 1. Contextual Entities E{{C, S, P}} ---\n");

    let ctx_thermal = Context::with_params(
        ContextKind::Thermal,
        &[("temperature", 25.0), ("pressure", 1.0)],
    );
    let ctx_quantum = Context::with_params(
        ContextKind::Quantum,
        &[("energy", 3.2), ("momentum", 1.1)],
    );

    // Entities borrow their context — lifetime enforced by compiler
    let water = Entity::new(
        &ctx_thermal,
        Scale::Human,
        Perspective::new(PerspectiveKind::Objective),
    );
    let photon = Entity::new(
        &ctx_quantum,
        Scale::Quantum,
        Perspective::new(PerspectiveKind::Statistical),
    );

    println!("  Water:  E{{thermal, human, objective}}");
    println!("    context params: {:?}", water.context.params);
    println!("  Photon: E{{quantum, quantum, statistical}}");
    println!("    context params: {:?}", photon.context.params);

    // -------------------------------------------------------
    // 2. Coherence between contexts
    // -------------------------------------------------------
    println!("\n--- 2. Coherence Coh(C₁, C₂) ---\n");

    let coh_self = coherence(&ctx_thermal, &ctx_thermal);
    let coh_diff = coherence(&ctx_thermal, &ctx_quantum);
    println!("  Coh(thermal, thermal) = {:.4}  (Axiom 4: reflexivity = 1)", coh_self);
    println!("  Coh(thermal, quantum) = {:.4}  (different contexts)", coh_diff);

    let ctx_thermal2 = Context::with_params(
        ContextKind::Thermal,
        &[("temperature", 27.0), ("pressure", 1.1)],
    );
    let coh_similar = coherence(&ctx_thermal, &ctx_thermal2);
    println!("  Coh(thermal@25°, thermal@27°) = {:.4}  (similar contexts)", coh_similar);

    // -------------------------------------------------------
    // 3. Contextual Composition ⊕
    // -------------------------------------------------------
    println!("\n--- 3. Composition ⊕ ---\n");

    let composed = operators::compose(&water, &photon);
    println!("  Water ⊕ Photon = E{{C₁∪C₂, S₁∩S₂, P₁ ⊕_P P₂}}");
    println!("    context params: {:?}", composed.context.params);
    println!("    scale: {:?}", composed.scale);
    println!("    intensity: {:.2}", composed.intensity);

    // -------------------------------------------------------
    // 4. Scalar Modulation ×
    // -------------------------------------------------------
    println!("\n--- 4. Modulation α × E ---\n");

    let amplified = operators::modulate(2.5, &water);
    println!("  2.5 × Water → intensity = {:.2}", amplified.intensity);

    // -------------------------------------------------------
    // 5. Context Transformation T
    // -------------------------------------------------------
    println!("\n--- 5. Transformation T ---\n");

    let transformed = operators::transform(&water, &ctx_quantum);
    println!("  T(Water → quantum context)");
    println!("    new context: {:?}", transformed.context.kind);
    println!(
        "    intensity: {:.4} (attenuated by Coh = {:.4})",
        transformed.intensity, coh_diff
    );

    // -------------------------------------------------------
    // 6. Universal Coherence Matrix & Clusters
    // -------------------------------------------------------
    println!("\n--- 6. Universal Coherence Matrix 𝕄 ---\n");

    // Create a set of diverse contexts
    let contexts: Vec<Context> = vec![
        // Cluster 1: thermal contexts (close parameters)
        Context::with_params(ContextKind::Thermal, &[("temperature", 20.0)]),
        Context::with_params(ContextKind::Thermal, &[("temperature", 22.0)]),
        Context::with_params(ContextKind::Thermal, &[("temperature", 21.0)]),
        Context::with_params(ContextKind::Thermal, &[("temperature", 23.0)]),
        // Cluster 2: quantum contexts (far from thermal)
        Context::with_params(ContextKind::Quantum, &[("energy", 100.0)]),
        Context::with_params(ContextKind::Quantum, &[("energy", 102.0)]),
        Context::with_params(ContextKind::Quantum, &[("energy", 101.0)]),
        // Cluster 3: social contexts (different dimension entirely)
        Context::with_params(ContextKind::Social, &[("density", 50.0)]),
        Context::with_params(ContextKind::Social, &[("density", 52.0)]),
    ];

    let mut matrix = CoherenceMatrix::from_contexts(&contexts);
    println!("  Built 𝕄 for {} contexts", contexts.len());

    let gamma_before = matrix.global_coherence();
    println!("  Γ (before friction) = {:.4}", gamma_before);

    // Apply friction
    let epsilon = 0.1;
    matrix.apply_friction(epsilon);
    let clusters = matrix.find_clusters();
    let n_clusters = *clusters.iter().max().unwrap_or(&0) + 1;
    let gamma_after = matrix.global_coherence();

    println!("  Applied friction ε = {}", epsilon);
    println!("  Γ (after friction)  = {:.4}", gamma_after);
    println!("  Clusters found: {}", n_clusters);
    println!("  Cluster assignments: {:?}", clusters);

    // Local collapse per cluster
    println!("\n  Local collapse analysis (θ = 0.5):");
    for k in 0..n_clusters {
        let indices: Vec<usize> = clusters
            .iter()
            .enumerate()
            .filter(|(_, &c)| c == k)
            .map(|(i, _)| i)
            .collect();
        let (gamma_k, collapsed) = matrix.local_collapse(&indices, 0.5);
        let status = if collapsed { "COLLAPSED" } else { "superposition" };
        println!(
            "    Cluster {} (size {}): Γ_k = {:.4} → {}",
            k,
            indices.len(),
            gamma_k,
            status
        );
    }

    // -------------------------------------------------------
    // 7. Nested Learning System
    // -------------------------------------------------------
    println!("\n--- 7. Nested Learning System ---\n");

    let mut system = NestedLearningSystem::new();

    // Simulate sensor readings
    let readings = [100.0, -50.0, 200.0, -150.0, 80.0, -30.0, 10.0, -5.0];
    for (i, &reading) in readings.iter().enumerate() {
        system.process_sensor(reading);
        println!(
            "  Step {}: sensor={:>6.1} → pos={:.1}, gain={:.3}, energy={:.1}",
            i,
            reading,
            system.reactive.position,
            system.reactive.gain,
            system.adaptive.accumulated_energy,
        );
    }

    println!("\n=================================================");
    println!("  Demo complete. Install Rust: https://rustup.rs");
    println!("  Then: cargo run --example demo");
    println!("=================================================");
}
