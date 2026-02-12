"""
SIC Universal Coherence Matrix Simulation
==========================================
Simulates the Universal Coherence Matrix (M) from Section 11 of the SIC
Metalanguage, demonstrating:

  - Entanglement friction (epsilon truncation) -> sparse matrix
  - Cluster decomposition -> quasi-independent reality blocks
  - Local collapse per cluster (eigenvalue analysis)
  - Percolation visualization

Usage:
    python simulacion_sic.py
    python simulacion_sic.py --entities 200 --friction 0.82

Developed as part of the SIC Metalanguage — Miguel and Claude.
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
import seaborn as sns
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components


def create_coherence_matrix(n: int, seed: int = 42) -> np.ndarray:
    """
    Create the Universal Coherence Matrix M (Section 11.1).

    Properties (from Axioms 4-6):
      - Diagonal = 1 (Axiom 4: Reflexivity)
      - Symmetric (Axiom 5: Symmetry)
      - Entries in [0, 1]
      - Positive semidefinite
    """
    rng = np.random.default_rng(seed)

    # Generate random coherences and enforce symmetry
    M = rng.random((n, n))
    M = (M + M.T) / 2
    np.fill_diagonal(M, 1.0)

    return M


def apply_friction(M: np.ndarray, epsilon: float) -> np.ndarray:
    """
    Apply entanglement friction (Section 11.4).

    Truncates coherences below epsilon to zero, producing a sparse
    effective matrix. This models decoherence: extremely weak
    entanglements are indistinguishable from noise.

    M_ij^eff = M_ij  if M_ij > epsilon
    M_ij^eff = 0     if M_ij <= epsilon
    """
    M_eff = M.copy()
    M_eff[M_eff < epsilon] = 0
    # Preserve diagonal (self-coherence is always 1)
    np.fill_diagonal(M_eff, 1.0)
    return M_eff


def find_clusters(M_eff: np.ndarray) -> tuple[int, np.ndarray]:
    """
    Decompose the effective matrix into quasi-independent clusters
    (Section 11.4 - Cluster Decomposition).

    Returns (num_clusters, labels) where labels[i] is the cluster
    index for entity i.
    """
    sparse = csr_matrix(M_eff)
    n_clusters, labels = connected_components(sparse, directed=False)
    return n_clusters, labels


def local_collapse(M_eff: np.ndarray, labels: np.ndarray, n_clusters: int) -> list[dict]:
    """
    Perform local collapse within each cluster (Section 11.5).

    For each cluster, compute:
      - Local coherence matrix M_k
      - Eigenvalues and eigenvectors
      - Local coherence measure Gamma_k = lambda_max / Tr(M_k)
      - Whether collapse occurs (Gamma_k > theta)
    """
    results = []
    theta_collapse = 0.5  # collapse threshold

    for k in range(n_clusters):
        indices = np.where(labels == k)[0]
        n_k = len(indices)

        if n_k < 2:
            results.append({
                "cluster": k,
                "size": n_k,
                "gamma": 1.0,
                "collapsed": True,
                "dominant_eigenvalue": 1.0,
            })
            continue

        # Extract local submatrix
        M_k = M_eff[np.ix_(indices, indices)]

        # Spectral analysis
        eigenvalues = np.linalg.eigvalsh(M_k)
        lambda_max = eigenvalues[-1]
        trace = np.trace(M_k)

        gamma_k = lambda_max / trace if trace > 0 else 0

        results.append({
            "cluster": k,
            "size": n_k,
            "gamma": gamma_k,
            "collapsed": gamma_k > theta_collapse,
            "dominant_eigenvalue": lambda_max,
        })

    return results


def global_coherence(M_eff: np.ndarray) -> float:
    """
    Compute global coherence measure Gamma (Section 11.6).

    Gamma = lambda_max(M) / Tr(M) = lambda_1 / N

    Gamma = 1/N -> minimum coherence (fragmented reality)
    Gamma ~ 1  -> maximum coherence (unified reality)
    """
    eigenvalues = np.linalg.eigvalsh(M_eff)
    N = M_eff.shape[0]
    return eigenvalues[-1] / N


def visualize(
    M_raw: np.ndarray,
    M_eff: np.ndarray,
    labels: np.ndarray,
    n_clusters: int,
    cluster_results: list[dict],
    gamma: float,
    friction: float,
    save_path: str = "simulacion_sic.png",
):
    """Generate the diagnostic visualization."""
    fig, axes = plt.subplots(1, 3, figsize=(20, 6))
    fig.suptitle(
        f"SIC — Universal Coherence Matrix Simulation\n"
        f"N={M_raw.shape[0]} entities | friction ε={friction} | "
        f"{n_clusters} clusters | Γ_global={gamma:.4f}",
        fontsize=13,
        fontweight="bold",
    )

    # -- Plot 1: Raw matrix (pure potentiality) --
    sns.heatmap(M_raw, ax=axes[0], cmap="viridis", cbar=False,
                xticklabels=False, yticklabels=False)
    axes[0].set_title("M (Pure Potentiality)\nAll-to-all coherence")

    # -- Plot 2: Effective matrix reordered by clusters (emergent order) --
    order = np.argsort(labels)
    M_ordered = M_eff[order][:, order]
    sns.heatmap(M_ordered, ax=axes[1], cmap="magma", cbar=False,
                xticklabels=False, yticklabels=False)

    # Draw cluster boundaries
    boundaries = []
    sorted_labels = labels[order]
    for k in range(n_clusters):
        idx = np.where(sorted_labels == k)[0]
        if len(idx) > 0:
            boundaries.append(idx[-1] + 1)
    for b in boundaries[:-1]:
        axes[1].axhline(y=b, color="cyan", linewidth=0.8, alpha=0.7)
        axes[1].axvline(x=b, color="cyan", linewidth=0.8, alpha=0.7)

    axes[1].set_title(
        f"M_eff (Post-Friction, Block Diagonal)\n"
        f"{n_clusters} Disjoint Realities"
    )

    # -- Plot 3: Cluster topology graph --
    G = nx.from_numpy_array(M_eff)
    pos = nx.spring_layout(G, k=0.15, iterations=30, seed=42)
    nx.draw_networkx_nodes(
        G, pos, node_size=30, node_color=labels,
        cmap=plt.cm.tab20, ax=axes[2],
    )
    edges = [(u, v) for u, v, d in G.edges(data=True) if d["weight"] > 0]
    nx.draw_networkx_edges(G, pos, edgelist=edges, alpha=0.15, ax=axes[2])
    axes[2].set_title("Cluster Topology\n(Reality Bubbles)")
    axes[2].axis("off")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"[saved to {save_path}]")


def print_report(n_clusters, cluster_results, gamma, friction, N):
    """Print a textual report of the simulation."""
    print("=" * 60)
    print("  SIC — Universal Coherence Matrix Simulation Report")
    print("=" * 60)
    print(f"  Entities (N):           {N}")
    print(f"  Friction (epsilon):     {friction}")
    print(f"  Clusters found:         {n_clusters}")
    print(f"  Global coherence (Gamma): {gamma:.4f}")
    print(f"  Theoretical range:      [{1/N:.4f}, 1.0]")
    print()

    # Sort by size descending
    sorted_results = sorted(cluster_results, key=lambda r: r["size"], reverse=True)

    print("  Cluster | Size | Gamma_k  | Collapsed | lambda_max")
    print("  " + "-" * 54)
    for r in sorted_results[:15]:  # show top 15
        mark = "YES" if r["collapsed"] else " no"
        print(
            f"  {r['cluster']:>7} | {r['size']:>4} | {r['gamma']:>8.4f} | "
            f"   {mark}   | {r['dominant_eigenvalue']:>10.4f}"
        )
    if len(sorted_results) > 15:
        print(f"  ... and {len(sorted_results) - 15} more clusters")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="SIC Universal Coherence Matrix Simulation"
    )
    parser.add_argument("-n", "--entities", type=int, default=100,
                        help="Number of contextual entities (default: 100)")
    parser.add_argument("-f", "--friction", type=float, default=0.82,
                        help="Entanglement friction epsilon (default: 0.82)")
    parser.add_argument("-s", "--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    parser.add_argument("-o", "--output", type=str, default="simulacion_sic.png",
                        help="Output image path (default: simulacion_sic.png)")
    parser.add_argument("--no-plot", action="store_true",
                        help="Skip visualization (text report only)")
    args = parser.parse_args()

    # 1. Create Universal Coherence Matrix
    M = create_coherence_matrix(args.entities, args.seed)

    # 2. Apply entanglement friction
    M_eff = apply_friction(M, args.friction)

    # 3. Find clusters (disjoint reality blocks)
    n_clusters, labels = find_clusters(M_eff)

    # 4. Local collapse analysis per cluster
    cluster_results = local_collapse(M_eff, labels, n_clusters)

    # 5. Global coherence
    gamma = global_coherence(M_eff)

    # 6. Report
    print_report(n_clusters, cluster_results, gamma, args.friction, args.entities)

    # 7. Visualize
    if not args.no_plot:
        visualize(M, M_eff, labels, n_clusters, cluster_results,
                  gamma, args.friction, args.output)


if __name__ == "__main__":
    main()
