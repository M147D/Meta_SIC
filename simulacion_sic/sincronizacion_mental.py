"""
SIC — Mental Synchronization & Contextual Friction Simulation
==============================================================
Demonstrates three regimes of reality transit (Section 7.6):

  Case 1: Brute Force     — misaligned mind, maximum friction, impossible
  Case 2: Gradual Synchrony — mind rotates phase, friction drops, collapse occurs
  Case 3: Tunnel Effect    — perfect alignment sustained, barrier penetrated

Also demonstrates why certain realities are invisible to most observers
(ghost/perception explanation via cluster disconnection in M).

Usage:
    python sincronizacion_mental.py
    python sincronizacion_mental.py --no-plot
    python sincronizacion_mental.py --output sincronizacion.png

Developed as part of the SIC Metalanguage — Miguel and Claude.
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


# ─── SIC Core Functions ───────────────────────────────────────────

def coherence(angle_diff: float) -> float:
    """Coh(A,B) based on angular alignment. cos²(θ/2) maps [0,π] → [1,0]."""
    return np.cos(angle_diff / 2) ** 2


def friction(coh: float) -> float:
    """Φ(A,B) = 1 - Coh(A,B) — the ontological incompatibility."""
    return 1.0 - coh


def energy_required(phi: float, s_sync: float) -> float:
    """E_req ∝ Φ / S_synchrony. Clamped to avoid division by zero."""
    return phi / max(s_sync, 0.01)


def tunnel_probability(t: float, coh: float, tau: float = 5.0) -> float:
    """P_tunnel(t) = 1 - exp(-t · Coh² / τ_tunnel)."""
    return 1.0 - np.exp(-t * coh ** 2 / tau)


# ─── Simulation Cases ────────────────────────────────────────────

def simulate_brute_force(steps: int = 100) -> dict:
    """Case 1: Mind is misaligned (opposite direction). No phase adjustment."""
    t = np.linspace(0, 10, steps)
    angle = np.full(steps, np.pi * 0.9)  # ~162° misalignment, constant

    coh = np.array([coherence(a) for a in angle])
    phi = np.array([friction(c) for c in coh])
    e_req = np.array([energy_required(p, 0.1) for p in phi])
    e_available = np.full(steps, 1.0)  # fixed energy budget

    return {
        "t": t, "angle": angle, "coh": coh, "phi": phi,
        "e_req": e_req, "e_available": e_available,
        "collapse_t": None,
        "title": "Caso 1: Fuerza Bruta\n(Mente desalineada)",
        "title_en": "Case 1: Brute Force\n(Misaligned mind)",
    }


def simulate_synchrony(steps: int = 100) -> dict:
    """Case 2: Mind gradually rotates to align with target."""
    t = np.linspace(0, 10, steps)
    # Phase rotation: starts at π (opposite), smoothly approaches 0 (aligned)
    angle = np.pi * np.exp(-0.35 * t)

    coh = np.array([coherence(a) for a in angle])
    phi = np.array([friction(c) for c in coh])
    s_sync = coh  # synchrony grows with coherence
    e_req = np.array([energy_required(p, s) for p, s in zip(phi, s_sync)])
    e_available = np.full(steps, 1.0)

    # Find collapse point (where e_req < e_available)
    collapse_idx = np.where(e_req < e_available)[0]
    collapse_t = t[collapse_idx[0]] if len(collapse_idx) > 0 else None

    return {
        "t": t, "angle": angle, "coh": coh, "phi": phi,
        "e_req": e_req, "e_available": e_available,
        "collapse_t": collapse_t,
        "title": "Caso 2: Sincronía Gradual\n(Alineación de fase)",
        "title_en": "Case 2: Gradual Synchrony\n(Phase alignment)",
    }


def simulate_tunnel(steps: int = 100) -> dict:
    """Case 3: Perfect alignment sustained through a high barrier."""
    t = np.linspace(0, 10, steps)
    # Mind is perfectly aligned from the start
    angle = np.full(steps, 0.1)  # near-perfect alignment

    coh = np.array([coherence(a) for a in angle])
    phi_barrier = 2.0  # artificially high external barrier
    phi = np.full(steps, phi_barrier)
    e_req = phi.copy()  # high barrier
    e_available = np.full(steps, 1.0)

    # Tunnel probability accumulates over time
    p_tunnel = np.array([tunnel_probability(ti, coh[0], tau=3.0) for ti in t])

    # Collapse when P_tunnel > theta_collapse
    theta_collapse = 0.7
    collapse_idx = np.where(p_tunnel > theta_collapse)[0]
    collapse_t = t[collapse_idx[0]] if len(collapse_idx) > 0 else None

    return {
        "t": t, "angle": angle, "coh": coh, "phi": phi,
        "e_req": e_req, "e_available": e_available,
        "p_tunnel": p_tunnel, "theta_collapse": theta_collapse,
        "collapse_t": collapse_t,
        "title": "Caso 3: Efecto Túnel\n(Certeza absoluta)",
        "title_en": "Case 3: Tunnel Effect\n(Absolute certainty)",
    }


# ─── Perception / Ghost Explanation ──────────────────────────────

def simulate_perception_ranges() -> dict:
    """
    Demonstrates why some realities are invisible:
    Different observers have different coherence thresholds (perception ranges).
    Clusters below the threshold are "ghosts" — they exist but can't be seen.
    """
    np.random.seed(123)
    n = 40
    # Create a coherence matrix with distinct clusters
    M = np.zeros((n, n))
    # Cluster 1: "Physical reality" (strong coherence)
    for i in range(20):
        for j in range(20):
            M[i, j] = 0.8 + 0.2 * np.random.random()
    # Cluster 2: "Subtle reality" (moderate coherence)
    for i in range(20, 30):
        for j in range(20, 30):
            M[i, j] = 0.5 + 0.3 * np.random.random()
    # Cluster 3: "Ultra-subtle reality" (weak coherence)
    for i in range(30, 40):
        for j in range(30, 40):
            M[i, j] = 0.3 + 0.2 * np.random.random()
    # Cross-cluster weak links
    for i in range(20):
        for j in range(20, 30):
            v = 0.15 + 0.1 * np.random.random()
            M[i, j] = v
            M[j, i] = v
    for i in range(20, 30):
        for j in range(30, 40):
            v = 0.08 + 0.07 * np.random.random()
            M[i, j] = v
            M[j, i] = v
    for i in range(20):
        for j in range(30, 40):
            v = 0.03 + 0.05 * np.random.random()
            M[i, j] = v
            M[j, i] = v
    np.fill_diagonal(M, 1.0)
    M = (M + M.T) / 2

    # Three observer types with different perception thresholds
    observers = {
        "Adulto humano\n(Adult human)": {"epsilon": 0.4, "color": "#e74c3c"},
        "Niño / Animal\n(Child / Animal)": {"epsilon": 0.2, "color": "#2ecc71"},
        "Percepción expandida\n(Expanded perception)": {"epsilon": 0.08, "color": "#9b59b6"},
    }

    return {"M": M, "observers": observers, "n": n}


# ─── Visualization ───────────────────────────────────────────────

def visualize(case1, case2, case3, perception, save_path="sincronizacion.png"):
    """Generate comprehensive 2-row visualization."""
    fig = plt.figure(figsize=(22, 14))
    gs = gridspec.GridSpec(2, 4, figure=fig, height_ratios=[1, 1],
                           hspace=0.35, wspace=0.3)

    fig.suptitle(
        "SIC — Fricción Contextual, Sincronización Mental y Percepción\n"
        "Contextual Friction, Mental Synchronization & Perception",
        fontsize=15, fontweight="bold", y=0.98,
    )

    # ─── Row 1: Three synchronization cases ───
    cases = [case1, case2, case3]
    for idx, case in enumerate(cases):
        ax = fig.add_subplot(gs[0, idx])
        t = case["t"]

        # Plot coherence and friction
        ax.plot(t, case["coh"], "b-", linewidth=2, label="Coh (Coherencia)")
        ax.plot(t, case["phi"], "r--", linewidth=2, label="Φ (Fricción)")

        if "p_tunnel" in case:
            ax.plot(t, case["p_tunnel"], "g:", linewidth=2.5,
                    label=f"P_túnel (θ={case['theta_collapse']})")
        else:
            # Plot energy comparison
            e_req_clipped = np.clip(case["e_req"], 0, 5)
            ax.plot(t, e_req_clipped, "m-", linewidth=1.5, alpha=0.7,
                    label="E_req (costo)")
            ax.plot(t, case["e_available"], "g--", linewidth=1.5, alpha=0.7,
                    label="E_disp (presupuesto)")

        # Mark collapse
        if case["collapse_t"] is not None:
            ax.axvline(x=case["collapse_t"], color="gold", linewidth=3,
                       alpha=0.8, linestyle="-", label="COLAPSO")
            ax.fill_betweenx([0, 1], case["collapse_t"], t[-1],
                             alpha=0.1, color="gold")

        ax.set_xlim(t[0], t[-1])
        ax.set_ylim(-0.05, 1.5 if "p_tunnel" not in case else 1.1)
        ax.set_xlabel("Tiempo (t)")
        ax.set_ylabel("Magnitud")
        ax.set_title(case["title"], fontsize=11, fontweight="bold")
        ax.legend(fontsize=7, loc="upper right")
        ax.grid(True, alpha=0.3)

        # Add result annotation
        if case["collapse_t"] is None:
            ax.text(0.5, 0.95, "IMPOSIBLE", transform=ax.transAxes,
                    fontsize=14, color="red", fontweight="bold",
                    ha="center", va="top",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                              edgecolor="red", alpha=0.8))
        else:
            ax.text(0.5, 0.95, f"COLAPSO en t={case['collapse_t']:.1f}",
                    transform=ax.transAxes, fontsize=11, color="darkgreen",
                    fontweight="bold", ha="center", va="top",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white",
                              edgecolor="green", alpha=0.8))

    # ─── Row 1, Col 4: Phase diagram ───
    ax_phase = fig.add_subplot(gs[0, 3])
    angles = np.linspace(0, np.pi, 200)
    coh_curve = np.array([coherence(a) for a in angles])
    phi_curve = np.array([friction(c) for c in coh_curve])

    ax_phase.plot(np.degrees(angles), coh_curve, "b-", linewidth=2.5,
                  label="Coh(θ)")
    ax_phase.plot(np.degrees(angles), phi_curve, "r-", linewidth=2.5,
                  label="Φ(θ) = 1 - Coh")
    ax_phase.fill_between(np.degrees(angles), coh_curve, phi_curve,
                          alpha=0.15, color="purple")
    ax_phase.set_xlabel("Ángulo de desalineación (°)")
    ax_phase.set_ylabel("Magnitud")
    ax_phase.set_title("Φ(A,B) = 1 - Coh(A,B)\nDiagrama de Fase",
                       fontsize=11, fontweight="bold")
    ax_phase.legend(fontsize=9)
    ax_phase.grid(True, alpha=0.3)
    ax_phase.set_xlim(0, 180)
    ax_phase.set_ylim(0, 1)

    # ─── Row 2: Perception / Ghost explanation ───
    M = perception["M"]
    observers = perception["observers"]

    for obs_idx, (name, config) in enumerate(observers.items()):
        ax = fig.add_subplot(gs[1, obs_idx])
        epsilon = config["epsilon"]
        color = config["color"]

        # Apply friction threshold
        M_eff = M.copy()
        M_eff[M_eff < epsilon] = 0
        np.fill_diagonal(M_eff, 1.0)

        # Count visible clusters
        from scipy.sparse import csr_matrix
        from scipy.sparse.csgraph import connected_components
        n_clusters, labels = connected_components(csr_matrix(M_eff),
                                                  directed=False)

        ax.imshow(M_eff, cmap="hot", vmin=0, vmax=1, aspect="equal")
        ax.set_title(f"{name}\nε={epsilon} → {n_clusters} realidades visibles",
                     fontsize=10, fontweight="bold", color=color)
        ax.set_xlabel("Entidad")
        ax.set_ylabel("Entidad")

        # Draw cluster boundaries
        sorted_idx = np.argsort(labels)
        # Annotate regions
        cluster_sizes = [np.sum(labels == k) for k in range(n_clusters)]
        visible_text = f"Ve {sum(1 for s in cluster_sizes if s > 1)} clusters"
        ax.text(0.02, 0.02, visible_text, transform=ax.transAxes,
                fontsize=9, color="white", fontweight="bold",
                bbox=dict(boxstyle="round", facecolor="black", alpha=0.6))

    # ─── Row 2, Col 4: Perception explanation text ───
    ax_text = fig.add_subplot(gs[1, 3])
    ax_text.axis("off")

    explanation = (
        "¿Por qué no vemos fantasmas?\n"
        "Why can't we see ghosts?\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "La Matriz de Coherencia M contiene\n"
        "TODAS las realidades posibles.\n\n"
        "Cada observador tiene un umbral de\n"
        "percepción (ε) que actúa como filtro:\n\n"
        "• Adulto humano (ε alto):\n"
        "  Solo ve la realidad física densa.\n"
        "  Clusters sutiles son invisibles.\n\n"
        "• Niño pequeño (ε bajo):\n"
        "  Su filtro perceptual es más amplio.\n"
        "  Puede percibir clusters adicionales\n"
        "  que el adulto no ve.\n\n"
        "• Animales (ε variable):\n"
        "  Gatos, perros y otros animales tienen\n"
        "  rangos sensoriales diferentes que les\n"
        "  permiten detectar clusters que los\n"
        "  humanos adultos no perciben.\n\n"
        "Los 'fantasmas' no son imaginación:\n"
        "son clusters de M que EXISTEN pero\n"
        "están debajo del umbral ε del\n"
        "observador adulto típico."
    )

    ax_text.text(0.05, 0.95, explanation, transform=ax_text.transAxes,
                 fontsize=9, verticalalignment="top", fontfamily="monospace",
                 bbox=dict(boxstyle="round,pad=0.5", facecolor="#f0f0f0",
                           edgecolor="#333", alpha=0.9))

    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"[saved to {save_path}]")


def print_report(case1, case2, case3):
    """Print textual summary."""
    print("=" * 65)
    print("  SIC — Contextual Friction & Mental Synchronization Report")
    print("=" * 65)

    for i, case in enumerate([case1, case2, case3], 1):
        print(f"\n  Case {i}: {case['title_en'].replace(chr(10), ' — ')}")
        print(f"    Final coherence:  {case['coh'][-1]:.4f}")
        print(f"    Final friction:   {case['phi'][-1]:.4f}")
        if case["collapse_t"] is not None:
            print(f"    Collapse at t =   {case['collapse_t']:.2f}")
        else:
            print(f"    Collapse:         IMPOSSIBLE (friction too high)")
        if "p_tunnel" in case:
            print(f"    Tunnel prob:      {case['p_tunnel'][-1]:.4f}")

    print("\n" + "=" * 65)
    print("  Perception Analysis:")
    print("  - Adult human (eps=0.4): sees only dense physical reality")
    print("  - Child / Animal (eps=0.2): sees subtle reality clusters")
    print("  - Expanded perception (eps=0.08): sees ultra-subtle clusters")
    print("  'Ghosts' = clusters in M below the observer's eps threshold")
    print("=" * 65)


def main():
    parser = argparse.ArgumentParser(
        description="SIC Contextual Friction & Mental Synchronization Simulation"
    )
    parser.add_argument("-o", "--output", type=str,
                        default="sincronizacion.png",
                        help="Output image path (default: sincronizacion.png)")
    parser.add_argument("--no-plot", action="store_true",
                        help="Skip visualization (text report only)")
    args = parser.parse_args()

    # Run three synchronization cases
    case1 = simulate_brute_force()
    case2 = simulate_synchrony()
    case3 = simulate_tunnel()

    # Perception simulation
    perception = simulate_perception_ranges()

    # Report
    print_report(case1, case2, case3)

    # Visualize
    if not args.no_plot:
        visualize(case1, case2, case3, perception, args.output)


if __name__ == "__main__":
    main()
