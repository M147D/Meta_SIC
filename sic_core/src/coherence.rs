//! Coherence metrics, Universal Coherence Matrix, and collapse — Sections 9, 11
//!
//! Coh(C₁, C₂) ∈ [0, 1]  — compatibility between contexts.
//! 𝕄ᵢⱼ = Coh(Cᵢ, Cⱼ)    — the Universal Coherence Matrix.
//! Friction ε truncates weak entanglements to zero.

use crate::context::Context;

/// Compute coherence between two contexts (Section 9.2).
///
/// Coh(C₁, C₂) = exp(-d(C₁, C₂)² / σ²)
///
/// This satisfies all coherence axioms:
///   - Axiom 4 (Reflexivity): Coh(C, C) = exp(0) = 1
///   - Axiom 5 (Symmetry): d is symmetric → Coh is symmetric
///   - Range [0, 1]: exponential of negative value
pub fn coherence(c1: &Context, c2: &Context) -> f64 {
    let d = c1.distance(c2);
    let sigma = 5.0; // characteristic coherence length
    (-d * d / (sigma * sigma)).exp()
}

/// The Universal Coherence Matrix 𝕄 (Section 11.1).
///
/// A symmetric N×N matrix where 𝕄ᵢⱼ = Coh(Cᵢ, Cⱼ).
#[derive(Debug, Clone)]
pub struct CoherenceMatrix {
    pub data: Vec<Vec<f64>>,
    pub n: usize,
}

impl CoherenceMatrix {
    /// Build 𝕄 from a set of contexts.
    pub fn from_contexts(contexts: &[Context]) -> Self {
        let n = contexts.len();
        let mut data = vec![vec![0.0; n]; n];
        for i in 0..n {
            data[i][i] = 1.0; // Axiom 4: reflexivity
            for j in (i + 1)..n {
                let coh = coherence(&contexts[i], &contexts[j]);
                data[i][j] = coh;
                data[j][i] = coh; // Axiom 5: symmetry
            }
        }
        Self { data, n }
    }

    /// Apply entanglement friction ε (Section 11.4).
    /// Truncates coherences below ε to zero, producing a sparse matrix.
    pub fn apply_friction(&mut self, epsilon: f64) {
        for i in 0..self.n {
            for j in 0..self.n {
                if i != j && self.data[i][j] < epsilon {
                    self.data[i][j] = 0.0;
                }
            }
        }
    }

    /// Find connected clusters via BFS (Section 11.4 - Cluster Decomposition).
    ///
    /// Returns a vector where labels[i] = cluster index for entity i.
    pub fn find_clusters(&self) -> Vec<usize> {
        let mut labels = vec![usize::MAX; self.n];
        let mut current_cluster = 0;

        for start in 0..self.n {
            if labels[start] != usize::MAX {
                continue;
            }
            // BFS from this node
            let mut queue = vec![start];
            labels[start] = current_cluster;

            while let Some(node) = queue.pop() {
                for neighbor in 0..self.n {
                    if labels[neighbor] == usize::MAX && self.data[node][neighbor] > 0.0 {
                        labels[neighbor] = current_cluster;
                        queue.push(neighbor);
                    }
                }
            }
            current_cluster += 1;
        }

        labels
    }

    /// Count the number of distinct clusters.
    pub fn num_clusters(&self) -> usize {
        let labels = self.find_clusters();
        labels.iter().copied().max().map(|m| m + 1).unwrap_or(0)
    }

    /// Compute global coherence Γ = λ_max / N (Section 11.6).
    ///
    /// Uses power iteration to approximate the dominant eigenvalue.
    pub fn global_coherence(&self) -> f64 {
        if self.n == 0 {
            return 0.0;
        }

        // Power iteration for dominant eigenvalue
        let mut v = vec![1.0 / (self.n as f64).sqrt(); self.n];
        let mut lambda = 0.0;

        for _ in 0..100 {
            // Matrix-vector multiply
            let mut w = vec![0.0; self.n];
            for i in 0..self.n {
                for j in 0..self.n {
                    w[i] += self.data[i][j] * v[j];
                }
            }

            // Compute eigenvalue estimate
            lambda = 0.0;
            for i in 0..self.n {
                lambda += w[i] * v[i];
            }

            // Normalize
            let norm: f64 = w.iter().map(|x| x * x).sum::<f64>().sqrt();
            if norm > 0.0 {
                for x in &mut w {
                    *x /= norm;
                }
            }
            v = w;
        }

        lambda / self.n as f64
    }

    /// Local collapse analysis for a specific cluster (Section 11.5).
    ///
    /// Returns (gamma_k, collapsed) where gamma_k = λ₁⁽ᵏ⁾ / Tr(𝕄ₖ).
    pub fn local_collapse(&self, cluster_indices: &[usize], theta: f64) -> (f64, bool) {
        let n_k = cluster_indices.len();
        if n_k <= 1 {
            return (1.0, true);
        }

        // Extract submatrix
        let mut sub = vec![vec![0.0; n_k]; n_k];
        for (si, &i) in cluster_indices.iter().enumerate() {
            for (sj, &j) in cluster_indices.iter().enumerate() {
                sub[si][sj] = self.data[i][j];
            }
        }

        // Power iteration on submatrix
        let mut v = vec![1.0 / (n_k as f64).sqrt(); n_k];
        let mut lambda = 0.0;

        for _ in 0..100 {
            let mut w = vec![0.0; n_k];
            for i in 0..n_k {
                for j in 0..n_k {
                    w[i] += sub[i][j] * v[j];
                }
            }
            lambda = w.iter().zip(v.iter()).map(|(a, b)| a * b).sum();
            let norm: f64 = w.iter().map(|x| x * x).sum::<f64>().sqrt();
            if norm > 0.0 {
                for x in &mut w {
                    *x /= norm;
                }
            }
            v = w;
        }

        let trace: f64 = (0..n_k).map(|i| sub[i][i]).sum();
        let gamma_k = if trace > 0.0 { lambda / trace } else { 0.0 };
        (gamma_k, gamma_k > theta)
    }
}
