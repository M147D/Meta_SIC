"""
SIC -- Graph Topology of the Coherence Matrix
===============================================
Simulates the graph-theoretic properties of the Universal Coherence
Matrix (Section 7.8), demonstrating:

  - Matrix-Graph duality: M as weighted graph G = (V, E, w)
  - Percolation: critical threshold eps_c where reality fragments
  - Laplacian spectrum: Fiedler value, algebraic connectivity
  - Centrality: bridge entities between reality clusters
  - Dynamic graph: topological evolution (fusion/fission of clusters)
  - Emergent properties: small-world, degree distribution

Usage:
    python grafo_coherencia.py
    python grafo_coherencia.py --entities 80 --seed 42
    python grafo_coherencia.py --no-plot

Developed as part of the SIC Metalanguage -- Miguel and Claude.
"""

import argparse
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import connected_components


# ---------------------------------------------------------------------------
# 1. Matrix construction (reuses logic from simulacion_sic.py)
# ---------------------------------------------------------------------------

def create_coherence_matrix(n: int, seed: int = 42) -> np.ndarray:
    """Create Universal Coherence Matrix M (Section 11.1).
    Symmetric, diagonal=1, entries in [0,1]."""
    rng = np.random.default_rng(seed)
    M = rng.random((n, n))
    M = (M + M.T) / 2
    np.fill_diagonal(M, 1.0)
    return M


# ---------------------------------------------------------------------------
# 2. Graph construction
# ---------------------------------------------------------------------------

def build_graph(M: np.ndarray, epsilon: float) -> nx.Graph:
    """Build NetworkX graph from M filtered by epsilon (Section 7.8.1)."""
    M_eff = M.copy()
    M_eff[M_eff < epsilon] = 0
    np.fill_diagonal(M_eff, 0)  # no self-loops in the graph
    G = nx.from_numpy_array(M_eff)
    return G


# ---------------------------------------------------------------------------
# 3. Topological metrics (Section 7.8.2)
# ---------------------------------------------------------------------------

def compute_topology(G: nx.Graph) -> dict:
    """Compute graph-theoretic metrics: degree, centrality, clustering, paths."""
    result = {}

    # Weighted degree
    degrees = dict(G.degree(weight='weight'))
    result['degrees'] = degrees
    result['avg_degree'] = np.mean(list(degrees.values())) if degrees else 0

    # Betweenness centrality (using friction = 1 - coherence as distance)
    # Invert weights: high coherence = short distance
    G_dist = G.copy()
    for u, v, d in G_dist.edges(data=True):
        d['distance'] = 1.0 - d['weight'] if d['weight'] > 0 else 1.0
    result['betweenness'] = nx.betweenness_centrality(
        G_dist, weight='distance', normalized=True
    )

    # Clustering coefficient
    result['clustering'] = nx.clustering(G, weight='weight')
    result['avg_clustering'] = nx.average_clustering(G, weight='weight')

    # Connected components
    components = list(nx.connected_components(G))
    result['n_components'] = len(components)
    result['giant_size'] = max(len(c) for c in components) if components else 0

    # Average shortest path (friction-weighted) within giant component
    if result['giant_size'] > 1:
        giant_nodes = max(components, key=len)
        G_giant = G_dist.subgraph(giant_nodes).copy()
        try:
            result['avg_path_length'] = nx.average_shortest_path_length(
                G_giant, weight='distance'
            )
        except nx.NetworkXError:
            result['avg_path_length'] = float('inf')
    else:
        result['avg_path_length'] = float('inf')

    # Top 5 bridge entities
    top_bridges = sorted(
        result['betweenness'].items(), key=lambda x: x[1], reverse=True
    )[:5]
    result['top_bridges'] = top_bridges

    return result


# ---------------------------------------------------------------------------
# 4. Laplacian spectrum (Section 7.8.3)
# ---------------------------------------------------------------------------

def compute_laplacian(G: nx.Graph) -> dict:
    """Compute graph Laplacian eigenvalues and Fiedler value."""
    n = G.number_of_nodes()
    if n == 0:
        return {'eigenvalues': np.array([]), 'fiedler': 0, 'n_zeros': 0}

    L = nx.laplacian_matrix(G, weight='weight').toarray().astype(float)
    eigenvalues = np.sort(np.linalg.eigvalsh(L))

    # Count near-zero eigenvalues (connected components)
    n_zeros = np.sum(np.abs(eigenvalues) < 1e-8)

    # Fiedler value = second smallest eigenvalue
    fiedler = eigenvalues[1] if n > 1 else 0

    return {
        'eigenvalues': eigenvalues,
        'fiedler': fiedler,
        'n_zeros': int(n_zeros),
        'laplacian': L,
    }


# ---------------------------------------------------------------------------
# 5. Percolation curve (Section 7.8.4)
# ---------------------------------------------------------------------------

def percolation_curve(M: np.ndarray, n_steps: int = 100) -> dict:
    """Sweep epsilon from 0 to 1, tracking clusters and giant component."""
    epsilons = np.linspace(0.01, 0.99, n_steps)
    n_clusters_list = []
    giant_sizes = []
    fiedler_values = []
    n = M.shape[0]

    for eps in epsilons:
        G = build_graph(M, eps)
        components = list(nx.connected_components(G))
        n_clusters_list.append(len(components))
        giant = max(len(c) for c in components) if components else 0
        giant_sizes.append(giant / n)

        # Fiedler value
        if G.number_of_nodes() > 1 and G.number_of_edges() > 0:
            try:
                L = nx.laplacian_matrix(G, weight='weight').toarray().astype(float)
                eigs = np.sort(np.linalg.eigvalsh(L))
                fiedler_values.append(eigs[1] if len(eigs) > 1 else 0)
            except Exception:
                fiedler_values.append(0)
        else:
            fiedler_values.append(0)

    # Find critical epsilon (max derivative of n_clusters)
    n_arr = np.array(n_clusters_list, dtype=float)
    deriv = np.diff(n_arr)
    eps_c_idx = np.argmax(deriv) + 1
    eps_c = epsilons[eps_c_idx]

    return {
        'epsilons': epsilons,
        'n_clusters': n_clusters_list,
        'giant_sizes': giant_sizes,
        'fiedler_values': fiedler_values,
        'eps_c': eps_c,
    }


# ---------------------------------------------------------------------------
# 6. Dynamic graph simulation (Section 7.8.5)
# ---------------------------------------------------------------------------

def simulate_dynamic_graph(M_base: np.ndarray, n_steps: int = 30,
                           epsilon: float = 0.5, seed: int = 42) -> dict:
    """Evolve coherences over time with drift and noise.
    Track topological events (fusion, fission)."""
    rng = np.random.default_rng(seed + 100)
    n = M_base.shape[0]

    snapshots = []
    n_components_history = []
    events = []  # (time, type, detail)

    M_t = M_base.copy()
    prev_components = None

    for t in range(n_steps):
        # Add correlated noise + slow drift
        noise = rng.normal(0, 0.03, (n, n))
        noise = (noise + noise.T) / 2
        np.fill_diagonal(noise, 0)

        # Drift: some pairs strengthen, others weaken
        drift = rng.normal(0, 0.01, (n, n))
        drift = (drift + drift.T) / 2
        np.fill_diagonal(drift, 0)

        M_t = M_t + noise + drift
        M_t = np.clip(M_t, 0, 1)
        np.fill_diagonal(M_t, 1.0)
        # Ensure symmetry
        M_t = (M_t + M_t.T) / 2

        G = build_graph(M_t, epsilon)
        components = list(nx.connected_components(G))
        n_comp = len(components)
        n_components_history.append(n_comp)

        # Detect topological events
        if prev_components is not None:
            if n_comp < len(prev_components):
                events.append((t, 'FUSION', f'{len(prev_components)}->{n_comp}'))
            elif n_comp > len(prev_components):
                events.append((t, 'FISSION', f'{len(prev_components)}->{n_comp}'))
        prev_components = components

        # Save snapshots at key times
        if t == 0 or t == n_steps // 2 or t == n_steps - 1:
            snapshots.append({
                'time': t,
                'M': M_t.copy(),
                'G': G.copy(),
                'n_components': n_comp,
            })

    return {
        'snapshots': snapshots,
        'n_components_history': n_components_history,
        'events': events,
        'n_steps': n_steps,
    }


# ---------------------------------------------------------------------------
# 7. Small-world detection (Section 7.8.6)
# ---------------------------------------------------------------------------

def check_small_world(G: nx.Graph, n_nodes: int) -> dict:
    """Check if graph has small-world properties."""
    result = {'is_small_world': False, 'sigma': 0}

    if G.number_of_edges() == 0 or G.number_of_nodes() < 4:
        return result

    # Average clustering
    C_actual = nx.average_clustering(G, weight='weight')

    # Random graph reference
    m = G.number_of_edges()
    n = G.number_of_nodes()
    if n < 2:
        return result
    p = 2.0 * m / (n * (n - 1)) if n > 1 else 0
    C_random = p  # expected clustering for Erdos-Renyi

    # Average path length (only in giant component)
    components = list(nx.connected_components(G))
    giant_nodes = max(components, key=len)
    if len(giant_nodes) < 4:
        return result

    G_giant = G.subgraph(giant_nodes).copy()
    try:
        L_actual = nx.average_shortest_path_length(G_giant)
    except nx.NetworkXError:
        return result

    L_random = np.log(len(giant_nodes)) / np.log(max(2, result.get('avg_degree', 2)))
    if L_random == 0:
        L_random = 1

    # Small-world coefficient sigma = (C/C_rand) / (L/L_rand)
    if C_random > 0 and L_actual > 0:
        gamma_sw = C_actual / C_random
        lambda_sw = L_actual / max(L_random, 0.01)
        sigma = gamma_sw / max(lambda_sw, 0.01)
        result['sigma'] = sigma
        result['is_small_world'] = sigma > 1.0
        result['C_ratio'] = gamma_sw
        result['L_ratio'] = lambda_sw
    else:
        result['sigma'] = 0

    return result


# ---------------------------------------------------------------------------
# 8. Text report
# ---------------------------------------------------------------------------

def print_report(n: int, eps_ref: float, topo: dict, lap: dict,
                 perc: dict, dyn: dict, sw: dict):
    """Print CLI report."""
    w = 70
    print("=" * w)
    print("  SIC -- Graph Topology & Percolation Report")
    print("=" * w)
    print()
    print(f"  Entities:                      {n}")
    print(f"  Reference epsilon:             {eps_ref:.2f}")
    print(f"  Percolation threshold (eps_c): {perc['eps_c']:.4f}")
    print(f"  Fiedler value (lambda_2):      {lap['fiedler']:.4f}")
    print(f"  Connected components:          {topo['n_components']}")
    print(f"  Giant component size:          {topo['giant_size']}/{n}")
    print(f"  Avg clustering coefficient:    {topo['avg_clustering']:.4f}")
    avg_path = topo['avg_path_length']
    if avg_path < float('inf'):
        print(f"  Avg shortest path (friction):  {avg_path:.4f}")
    else:
        print(f"  Avg shortest path (friction):  disconnected")
    print(f"  Small-world (sigma):           {sw.get('sigma', 0):.2f}"
          f" ({'YES' if sw.get('is_small_world') else 'NO'})")
    print()
    print("  Bridge entities (top 5 betweenness):")
    for node_id, btwn in topo['top_bridges']:
        print(f"    Entity {node_id:3d}  B={btwn:.4f}")
    print()
    print(f"  Dynamic graph ({dyn['n_steps']} steps):")
    print(f"    Topological events: {len(dyn['events'])}")
    for t, etype, detail in dyn['events'][:10]:
        print(f"      t={t:3d}  {etype:7s}  {detail}")
    if len(dyn['events']) > 10:
        print(f"      ... and {len(dyn['events']) - 10} more")
    print()
    print("=" * w)


# ---------------------------------------------------------------------------
# 9. Visualization (6 panels, 2x3)
# ---------------------------------------------------------------------------

def visualize(M: np.ndarray, eps_ref: float, topo: dict, lap: dict,
              perc: dict, dyn: dict, output: str):
    """Generate 6-panel visualization."""
    fig = plt.figure(figsize=(20, 13))
    fig.suptitle("SIC -- Graph Topology of the Coherence Matrix\n"
                 "Topologia de Grafo de la Matriz de Coherencia",
                 fontsize=14, fontweight='bold', y=0.98)

    gs = gridspec.GridSpec(2, 3, hspace=0.35, wspace=0.3,
                           top=0.92, bottom=0.06, left=0.06, right=0.96)
    n = M.shape[0]

    # --- Panel 1: Graph at 3 epsilon values ---
    eps_values = [0.3, 0.6, 0.9]
    ax1 = fig.add_subplot(gs[0, 0])
    colors_map = ['#2196F3', '#FF9800', '#4CAF50']

    for idx, eps_val in enumerate(eps_values):
        G_sub = build_graph(M, eps_val)
        n_comp = nx.number_connected_components(G_sub)
        pos = nx.spring_layout(G_sub, k=0.3, iterations=30,
                               seed=42 + idx)
        # Offset each subgraph horizontally
        offset_x = (idx - 1) * 3.0
        pos = {k: (v[0] + offset_x, v[1]) for k, v in pos.items()}

        node_sizes = [max(5, G_sub.degree(node, weight='weight') * 3)
                      for node in G_sub.nodes()]
        nx.draw_networkx_nodes(G_sub, pos, node_size=node_sizes,
                               node_color=colors_map[idx], alpha=0.7,
                               ax=ax1)
        edges = [(u, v) for u, v, d in G_sub.edges(data=True)
                 if d.get('weight', 0) > 0]
        if edges:
            nx.draw_networkx_edges(G_sub, pos, edgelist=edges,
                                   alpha=0.15, ax=ax1)
        ax1.text(offset_x, -1.8,
                 f"eps={eps_val}\n{n_comp} comp",
                 ha='center', fontsize=8,
                 bbox=dict(boxstyle='round,pad=0.3',
                           facecolor=colors_map[idx], alpha=0.2))

    ax1.set_title("Perception-Filtered Graphs\n(same M, different eps)",
                  fontsize=10)
    ax1.set_xlim(-4.5, 4.5)
    ax1.axis('off')

    # --- Panel 2: Percolation curve ---
    ax2 = fig.add_subplot(gs[0, 1])
    ax2_twin = ax2.twinx()

    ax2.plot(perc['epsilons'], perc['n_clusters'], 'b-', linewidth=2,
             label='N clusters')
    ax2_twin.plot(perc['epsilons'], perc['giant_sizes'], 'r-', linewidth=2,
                  label='Giant component')
    ax2.axvline(x=perc['eps_c'], color='green', linestyle='--', alpha=0.8,
                label=f"eps_c = {perc['eps_c']:.3f}")

    ax2.set_xlabel('Friction threshold (eps)')
    ax2.set_ylabel('Number of clusters', color='blue')
    ax2_twin.set_ylabel('Giant component / N', color='red')
    ax2.set_title("Percolation Curve\n(Contextual Phase Transition)",
                  fontsize=10)

    # Combined legend
    lines1, labels1 = ax2.get_legend_handles_labels()
    lines2, labels2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines1 + lines2, labels1 + labels2, loc='center right',
               fontsize=7)

    # Shade regions
    ax2.axvspan(0, perc['eps_c'], alpha=0.05, color='green',
                label='Connected')
    ax2.axvspan(perc['eps_c'], 1.0, alpha=0.05, color='red',
                label='Fragmented')

    # --- Panel 3: Laplacian eigenvalues ---
    ax3 = fig.add_subplot(gs[0, 2])
    eigs = lap['eigenvalues']
    if len(eigs) > 0:
        ax3.bar(range(len(eigs)), eigs, color='purple', alpha=0.6, width=1.0)
        ax3.axhline(y=eigs[1] if len(eigs) > 1 else 0,
                    color='red', linestyle='--', linewidth=1.5,
                    label=f"lambda_2 (Fiedler) = {lap['fiedler']:.3f}")
        # Mark zero eigenvalues
        n_zeros = lap['n_zeros']
        ax3.axvspan(-0.5, n_zeros - 0.5, alpha=0.1, color='orange')
        ax3.text(n_zeros / 2, max(eigs) * 0.9,
                 f"{n_zeros} zeros\n= {n_zeros} realities",
                 ha='center', fontsize=8, color='darkorange',
                 fontweight='bold')

    ax3.set_xlabel('Eigenvalue index')
    ax3.set_ylabel('Eigenvalue')
    ax3.set_title("Laplacian Spectrum\n(Algebraic Connectivity)",
                  fontsize=10)
    ax3.legend(fontsize=8)

    # --- Panel 4: Centrality graph ---
    ax4 = fig.add_subplot(gs[1, 0])
    G_ref = build_graph(M, eps_ref)
    pos_ref = nx.spring_layout(G_ref, k=0.2, iterations=40, seed=42)

    betw = topo['betweenness']
    max_b = max(betw.values()) if betw and max(betw.values()) > 0 else 1
    node_sizes = [50 + 500 * (betw.get(n_id, 0) / max_b)
                  for n_id in G_ref.nodes()]
    node_colors = [betw.get(n_id, 0) for n_id in G_ref.nodes()]

    nodes_drawn = nx.draw_networkx_nodes(
        G_ref, pos_ref, node_size=node_sizes, node_color=node_colors,
        cmap=plt.cm.YlOrRd, alpha=0.8, ax=ax4
    )
    edges = [(u, v) for u, v, d in G_ref.edges(data=True)
             if d.get('weight', 0) > 0]
    if edges:
        edge_weights = [G_ref[u][v]['weight'] for u, v in edges]
        nx.draw_networkx_edges(G_ref, pos_ref, edgelist=edges,
                               alpha=0.2, width=1, ax=ax4)

    # Label top bridges
    for node_id, btwn_val in topo['top_bridges'][:3]:
        if node_id in pos_ref:
            x, y = pos_ref[node_id]
            ax4.annotate(f"E{node_id}", (x, y), fontsize=7,
                        fontweight='bold', color='darkred',
                        ha='center', va='bottom')

    if nodes_drawn:
        plt.colorbar(nodes_drawn, ax=ax4, shrink=0.6, label='Betweenness')
    ax4.set_title(f"Bridge Entities (eps={eps_ref})\n"
                  f"(node size = betweenness centrality)",
                  fontsize=10)
    ax4.axis('off')

    # --- Panel 5: Degree distribution ---
    ax5 = fig.add_subplot(gs[1, 1])
    deg_values = list(topo['degrees'].values())
    if deg_values:
        ax5.hist(deg_values, bins=20, color='teal', alpha=0.7,
                 edgecolor='white', density=True)
        ax5.axvline(x=np.mean(deg_values), color='red', linestyle='--',
                    label=f"Mean = {np.mean(deg_values):.1f}")
        ax5.axvline(x=np.median(deg_values), color='orange', linestyle='--',
                    label=f"Median = {np.median(deg_values):.1f}")

        # Check skewness (proxy for power-law tendency)
        skew = (np.mean(deg_values) - np.median(deg_values)) / max(
            np.std(deg_values), 0.01)
        dist_type = "heavy-tailed" if skew > 0.3 else "symmetric"
        ax5.text(0.95, 0.95, f"Skew indicator: {skew:.2f}\n({dist_type})",
                 transform=ax5.transAxes, ha='right', va='top', fontsize=8,
                 bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

    ax5.set_xlabel('Weighted Degree')
    ax5.set_ylabel('Density')
    ax5.set_title(f"Degree Distribution\n(Contextual Richness)", fontsize=10)
    ax5.legend(fontsize=8)

    # --- Panel 6: Dynamic graph snapshots ---
    ax6 = fig.add_subplot(gs[1, 2])
    snapshots = dyn['snapshots']
    n_snaps = len(snapshots)

    for idx, snap in enumerate(snapshots):
        G_snap = snap['G']
        offset_x = (idx - (n_snaps - 1) / 2) * 3.5
        pos_snap = nx.spring_layout(G_snap, k=0.3, iterations=25,
                                    seed=42)
        pos_snap = {k: (v[0] + offset_x, v[1]) for k, v in pos_snap.items()}

        # Color by connected component
        components = list(nx.connected_components(G_snap))
        node_to_comp = {}
        for ci, comp in enumerate(components):
            for node in comp:
                node_to_comp[node] = ci

        node_colors_snap = [node_to_comp.get(node, 0)
                           for node in G_snap.nodes()]
        nx.draw_networkx_nodes(G_snap, pos_snap, node_size=20,
                               node_color=node_colors_snap,
                               cmap=plt.cm.Set3, alpha=0.8, ax=ax6)
        edges_snap = [(u, v) for u, v, d in G_snap.edges(data=True)
                      if d.get('weight', 0) > 0]
        if edges_snap:
            nx.draw_networkx_edges(G_snap, pos_snap, edgelist=edges_snap,
                                   alpha=0.15, ax=ax6)

        ax6.text(offset_x, -1.8,
                 f"t={snap['time']}\n{snap['n_components']} comp",
                 ha='center', fontsize=8,
                 bbox=dict(boxstyle='round,pad=0.3',
                           facecolor='lightyellow'))

    # Mark events
    event_text = ""
    fusions = sum(1 for _, et, _ in dyn['events'] if et == 'FUSION')
    fissions = sum(1 for _, et, _ in dyn['events'] if et == 'FISSION')
    if fusions or fissions:
        event_text = f"Events: {fusions} fusions, {fissions} fissions"
    ax6.text(0.5, 1.02, event_text, transform=ax6.transAxes,
             ha='center', fontsize=8, color='darkblue')

    ax6.set_title("Dynamic Graph Evolution\n(Topological Fusion/Fission)",
                  fontsize=10)
    ax6.axis('off')

    plt.savefig(output, dpi=150, bbox_inches='tight')
    plt.show()
    print(f"[saved to {output}]")


# ---------------------------------------------------------------------------
# 10. Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="SIC -- Graph Topology of the Coherence Matrix (Section 7.8)"
    )
    parser.add_argument("-n", "--entities", type=int, default=50,
                        help="Number of entities (default: 50)")
    parser.add_argument("-e", "--epsilon", type=float, default=0.5,
                        help="Reference epsilon for metrics (default: 0.5)")
    parser.add_argument("-s", "--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    parser.add_argument("-o", "--output", type=str,
                        default="grafo_coherencia.png",
                        help="Output image path")
    parser.add_argument("--no-plot", action="store_true",
                        help="Skip visualization, text report only")
    args = parser.parse_args()

    # Build coherence matrix
    M = create_coherence_matrix(args.entities, args.seed)

    # Build reference graph
    G_ref = build_graph(M, args.epsilon)

    # Compute metrics
    topo = compute_topology(G_ref)
    lap = compute_laplacian(G_ref)
    perc = percolation_curve(M)

    # Dynamic graph uses epsilon near percolation threshold for interesting events
    eps_dynamic = perc['eps_c'] * 0.95  # slightly below critical threshold
    dyn = simulate_dynamic_graph(M, n_steps=30, epsilon=eps_dynamic,
                                 seed=args.seed)
    sw = check_small_world(G_ref, args.entities)

    # Report
    print_report(args.entities, args.epsilon, topo, lap, perc, dyn, sw)

    # Visualize
    if not args.no_plot:
        visualize(M, args.epsilon, topo, lap, perc, dyn, args.output)


if __name__ == "__main__":
    main()
