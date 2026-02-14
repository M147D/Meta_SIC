"""
SIC -- Dynamic Consciousness & Cognitive Friction Simulation
==============================================================
Two simulations demonstrating emergent consciousness through
self-regulated contextual friction (epsilon_obs as dynamic variable).

  Part 1: Consciousness Thermostat
    - Agent auto-regulates epsilon_obs based on prediction error
    - High error (surprise) -> lower friction (open mind, learn fast)
    - Low error (calm) -> raise friction (efficient, habitual)
    - Demonstrates homeostatic cognition

  Part 2: SIC v3 -- Three-Layer Nested Consciousness
    - Environmental: day/night cycle modulates sensitivity
    - Reactive: feels friction from events (pain signal)
    - Adaptive: predicts via Hebbian synapses, discovers causality
    - Prevention Paradox: rewards preventive action with 0.5x strength
    - Emergent urgency: fuzzy logic combining friction + coherence

Usage:
    python conciencia_dinamica.py
    python conciencia_dinamica.py --no-plot
    python conciencia_dinamica.py --output conciencia.png

Developed as part of the SIC Metalanguage -- Miguel and Claude.
"""

import argparse
import random
import math
from collections import deque
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec


# =====================================================================
# PART 1: CONSCIOUSNESS THERMOSTAT
# =====================================================================

def simulate_consciousness_thermostat(steps=200, seed=42):
    """
    An agent that auto-regulates its perception threshold epsilon_obs.

    The key insight: epsilon is not a constant -- it's a DYNAMIC variable
    that the system adjusts based on prediction error (surprise).

    This transforms Axiom 9 from static property to dynamic process:
    the difference between a thermometer and a thermostat.
    """
    rng = np.random.default_rng(seed)

    # Environment: stable -> chaotic -> stable
    noise_base = rng.normal(0, 0.1, steps)
    chaos_event = np.zeros(steps)
    chaos_event[50:120] = rng.normal(0, 2.0, 70)  # Conceptual earthquake
    reality = np.sin(np.linspace(0, 10, steps)) + noise_base + chaos_event

    # Agent state
    prediction = 0.0
    friction = 0.5  # Initial epsilon (balanced)
    base_learning_rate = 0.1

    # History
    hist_friction = []
    hist_error = []
    hist_prediction = []

    for t in range(steps):
        obs = reality[t]

        # A. Prediction error (surprise / free energy)
        error = abs(obs - prediction)

        # B. CONSCIOUSNESS MECHANISM: Self-modulation of friction
        # High error (stress) -> lower friction (open mind, neuroplasticity)
        # Low error (calm) -> raise friction (efficient, habitual)
        delta_friction = (0.2 - error) * 0.1  # Homeostatic rule
        friction += delta_friction
        friction = np.clip(friction, 0.05, 0.95)  # Biological limits

        # C. Update internal model
        # Friction controls how much reality changes our mind
        # High friction = slow learning (resistance to change)
        # Low friction = fast learning (plasticity)
        learning_rate = base_learning_rate * (1.0 - friction)
        prediction = prediction + learning_rate * (obs - prediction)

        hist_friction.append(friction)
        hist_error.append(error)
        hist_prediction.append(prediction)

    return {
        "reality": reality,
        "prediction": np.array(hist_prediction),
        "friction": np.array(hist_friction),
        "error": np.array(hist_error),
        "chaos_start": 50,
        "chaos_end": 120,
    }


# =====================================================================
# PART 2: SIC v3 -- THREE-LAYER NESTED CONSCIOUSNESS
# =====================================================================

DECAY_RATE = 0.02
LEARNING_RATE = 0.3
ACTION_THRESHOLD = 0.6


class Event:
    """An event in the SIC universe."""
    def __init__(self, kind, value, time):
        self.kind = kind
        self.value = value
        self.time = time

    def __repr__(self):
        return f"[{self.time}] {self.kind}={self.value}"


class Synapse:
    """A Hebbian synapse between two event types."""
    def __init__(self, origin, target):
        self.origin = origin
        self.target = target
        self.weight = 0.4  # Initial low confidence

    def decay(self):
        self.weight *= (1.0 - DECAY_RATE)

    def reinforce(self, intensity=1.0):
        # Hebbian with asymptote: delta = rate * intensity * (1 - weight)
        # Prevents saturation -- self-limiting like biological systems
        delta = LEARNING_RATE * intensity * (1.0 - self.weight)
        self.weight += delta


class EnvironmentalContext:
    """
    Layer 3: Environmental Context (Strategic)
    Scale (S): Cyclic (Day/Night)
    Perspective (P): Sensitivity Modulator

    Modulates how the reactive layer perceives friction.
    Same CPU_LOAD at 85% generates DIFFERENT friction depending
    on whether it's day (high demand) or night (maintenance).
    This IS Axiom 3 (Constitutive Perspective) in code.
    """
    def __init__(self):
        self.phase = "DAY"
        self.friction_modifier = 1.0

    def update(self, time):
        cycle = time % 20
        if cycle < 10:
            self.phase = "DAY (High Demand)"
            self.friction_modifier = 1.2  # More sensitive to pain
        else:
            self.phase = "NIGHT (Maintenance)"
            self.friction_modifier = 0.8  # Tolerates more chaos
        return self.friction_modifier


class ReactiveContext:
    """
    Layer 1: Reactive Context (Instinctive)
    Direct sensor -> friction mapping.
    Pain threshold modulated by environmental context.
    """
    def __init__(self):
        self.pain_threshold = 80.0

    def feel(self, event, env_modifier):
        friction = 0.0
        if event.kind == "CPU_LOAD":
            excess = max(0, event.value - self.pain_threshold)
            friction = (excess / 20.0) * env_modifier
        return min(friction, 1.0)


class AdaptiveContext:
    """
    Layer 2: Adaptive Context (Predictive)
    Discovers causal relationships via Hebbian learning.
    Solves the Prevention Paradox: rewards preventive success
    with 0.5x strength (like dopamine -- uncertain causality).
    """
    def __init__(self):
        self.memory = {}  # {(origin, target): Synapse}
        self.buffer = deque(maxlen=5)  # Working memory

    def predict(self, current_event):
        """Returns (predicted_event_type, coherence)."""
        best_prediction = None
        max_coherence = 0.0

        for (origin, target), synapse in self.memory.items():
            if origin == current_event.kind:
                if synapse.weight > max_coherence:
                    max_coherence = synapse.weight
                    best_prediction = target

        return best_prediction, max_coherence

    def learn(self, current_event, real_friction, action_taken):
        # 1. ENTROPY: All synapses decay
        dead_keys = []
        for k in self.memory:
            self.memory[k].decay()
            if self.memory[k].weight < 0.1:
                dead_keys.append(k)
        for k in dead_keys:
            del self.memory[k]

        # 2. PREVENTION PARADOX SOLUTION
        # If we acted preventively and friction is low -> SUCCESS!
        internal_reward = False
        if action_taken == "PREVENT" and real_friction < 0.1:
            internal_reward = True  # Dopamine hit

        # 3. ASSOCIATION (Hebbian)
        # Learn from Pain (high friction) OR from Preventive Success
        if real_friction > 0.5 or internal_reward:
            for past_event in self.buffer:
                key = (past_event.kind, current_event.kind)
                if key not in self.memory:
                    self.memory[key] = Synapse(past_event.kind, current_event.kind)

                # Preventive success reinforces with 0.5x (uncertain causality)
                strength = 1.0 if real_friction > 0.5 else 0.5
                self.memory[key].reinforce(strength)

        self.buffer.append(current_event)


class SICv3:
    """
    Complete SIC v3 system with three genuinely nested layers.
    Environmental modulates Reactive, Adaptive predicts using
    continuous coherence, decisions emerge from fuzzy composition.
    """
    def __init__(self):
        self.environmental = EnvironmentalContext()
        self.reactive = ReactiveContext()
        self.adaptive = AdaptiveContext()
        self.prevention_active = False

    def cycle(self, event, time):
        # 1. ENVIRONMENTAL (modulates everything)
        modifier = self.environmental.update(time)

        # 2. PERCEPTION
        real_value = event.value
        if self.prevention_active and event.kind == "CPU_LOAD":
            real_value = max(0, real_value - 40)  # Autoscaling reduced load

        perceived = Event(event.kind, real_value, time)

        # 3. FEEL (Reactive)
        friction = self.reactive.feel(perceived, modifier)

        # 4. THINK (Adaptive)
        prediction, coherence = self.adaptive.predict(perceived)

        # 5. ACT (Emergent decision)
        action = "MONITOR"

        # Fuzzy logic: combine Friction (Present) + Coherence (Future)
        # Urgency = Friction + (Coherence * weight)
        # This is contextual composition in code
        urgency = friction + (coherence * 0.8)

        if urgency > ACTION_THRESHOLD:
            if friction > 0.5:
                action = "REACT (Restart)"  # Too late
                self.prevention_active = False
            else:
                action = "PREVENT (Autoscale)"  # In time
                self.prevention_active = True
        else:
            self.prevention_active = False

        # 6. LEARN (with corrected feedback)
        self.adaptive.learn(perceived, friction, action.split()[0])

        return {
            "phase": self.environmental.phase,
            "friction": friction,
            "action": action,
            "coherence": coherence,
            "prediction": prediction,
            "urgency": urgency,
        }


class World:
    """
    Chaotic world with hidden causality.
    The system does NOT know that LOGIN causes CPU_LOAD.
    It must discover this through experience.
    20% false negatives (login without load) make learning
    genuinely probabilistic.
    """
    def __init__(self, seed=42):
        self.time = 0
        self.login_recent = False
        self.rng = random.Random(seed)

    def tick(self):
        self.time += 1
        r = self.rng.random()

        # Hidden causal physics: LOGIN -> CPU_LOAD (80% of the time)
        if self.login_recent:
            self.login_recent = False
            if r < 0.8:
                return Event("CPU_LOAD", self.rng.randint(85, 99), self.time)
            else:
                return Event("PING", self.rng.randint(10, 20), self.time)

        # Spontaneous events
        if r < 0.3:
            self.login_recent = True
            return Event("LOGIN", self.rng.randint(1, 5), self.time)
        elif r < 0.6:
            return Event("PING", self.rng.randint(5, 15), self.time)
        else:
            return Event("IDLE", 0, self.time)


def simulate_sic_v3(n_ticks=60, seed=42):
    """Run the full SIC v3 simulation and collect history."""
    sic = SICv3()
    world = World(seed=seed)

    history = []
    for _ in range(n_ticks):
        event = world.tick()
        result = sic.cycle(event, world.time)

        # Track LOGIN->CPU_LOAD synapse weight
        lc_weight = 0.0
        key = ("LOGIN", "CPU_LOAD")
        if key in sic.adaptive.memory:
            lc_weight = sic.adaptive.memory[key].weight

        history.append({
            "time": world.time,
            "event_type": event.kind,
            "event_value": event.value,
            "phase": result["phase"],
            "friction": result["friction"],
            "coherence": result["coherence"],
            "action": result["action"],
            "urgency": result["urgency"],
            "lc_synapse": lc_weight,
        })

    return history


# =====================================================================
# VISUALIZATION
# =====================================================================

def visualize(thermostat, sic_history, save_path="conciencia.png"):
    """Generate comprehensive 2-row visualization."""
    fig = plt.figure(figsize=(22, 14))
    gs = gridspec.GridSpec(2, 3, figure=fig, height_ratios=[1, 1],
                           hspace=0.35, wspace=0.3)

    fig.suptitle(
        "SIC -- Dynamic Consciousness & Cognitive Friction\n"
        "Conciencia Dinamica y Friccion Cognitiva",
        fontsize=15, fontweight="bold", y=0.98,
    )

    # ─── Row 1: Consciousness Thermostat ───

    # Panel 1: Reality vs Mind
    ax1 = fig.add_subplot(gs[0, 0])
    steps = len(thermostat["reality"])
    t = np.arange(steps)

    ax1.plot(t, thermostat["reality"], color="cyan", alpha=0.5,
             linewidth=0.8, label="Reality (chaotic)")
    ax1.plot(t, thermostat["prediction"], color="blue", linewidth=2,
             label="Mind (prediction)")
    ax1.axvspan(thermostat["chaos_start"], thermostat["chaos_end"],
                alpha=0.1, color="yellow")
    ax1.text(85, ax1.get_ylim()[1] * 0.85, "CRISIS",
             ha="center", color="orange", fontweight="bold", fontsize=10)
    ax1.set_xlabel("Time")
    ax1.set_ylabel("Context Value")
    ax1.set_title("Consciousness Thermostat\nReality vs Internal Model",
                  fontsize=11, fontweight="bold")
    ax1.legend(fontsize=8, loc="upper left")
    ax1.grid(True, alpha=0.3)

    # Panel 2: Dynamic Friction
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot(t, thermostat["friction"], color="red", linewidth=2,
             label="epsilon_obs (self-regulated)")
    ax2.fill_between(t, thermostat["friction"], alpha=0.15, color="red")
    ax2.axvspan(thermostat["chaos_start"], thermostat["chaos_end"],
                alpha=0.1, color="yellow")
    ax2.axhline(y=0.5, color="gray", linestyle=":", alpha=0.5,
                label="Initial epsilon")
    ax2.set_xlabel("Time")
    ax2.set_ylabel("Cognitive Friction (epsilon)")
    ax2.set_ylim(0, 1)
    ax2.set_title("Dynamic Perception (Axiom 9+)\nepsilon as thermostat",
                  fontsize=11, fontweight="bold")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)

    # Add phase annotations
    ax2.annotate("Dogma\n(efficient)", xy=(25, thermostat["friction"][25]),
                 fontsize=8, ha="center", color="darkred",
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="red", alpha=0.7))
    crisis_min_idx = thermostat["chaos_start"] + np.argmin(
        thermostat["friction"][thermostat["chaos_start"]:thermostat["chaos_end"]])
    ax2.annotate("Plasticity\n(learning)", xy=(crisis_min_idx, thermostat["friction"][crisis_min_idx]),
                 fontsize=8, ha="center", color="darkgreen",
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="green", alpha=0.7))
    ax2.annotate("Wisdom\n(recovered)", xy=(170, thermostat["friction"][170]),
                 fontsize=8, ha="center", color="darkblue",
                 bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="blue", alpha=0.7))

    # Panel 3: Prediction Error
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot(t, thermostat["error"], color="orange", alpha=0.6, linewidth=0.8,
             label="Prediction Error")
    # Moving average
    window = 10
    if len(thermostat["error"]) > window:
        error_ma = np.convolve(thermostat["error"], np.ones(window)/window, mode="valid")
        ax3.plot(np.arange(window-1, steps), error_ma, color="darkorange",
                 linewidth=2, label=f"Moving avg ({window})")
    ax3.axvspan(thermostat["chaos_start"], thermostat["chaos_end"],
                alpha=0.1, color="yellow")
    ax3.set_xlabel("Time")
    ax3.set_ylabel("Prediction Error (Surprise)")
    ax3.set_title("Free Energy (Surprise)\nDrives friction adjustment",
                  fontsize=11, fontweight="bold")
    ax3.legend(fontsize=8)
    ax3.grid(True, alpha=0.3)

    # ─── Row 2: SIC v3 Three-Layer System ───

    times = [h["time"] for h in sic_history]
    frictions = [h["friction"] for h in sic_history]
    coherences = [h["coherence"] for h in sic_history]
    urgencies = [h["urgency"] for h in sic_history]
    lc_weights = [h["lc_synapse"] for h in sic_history]

    # Color events by type
    event_colors = {
        "LOGIN": "#e74c3c",
        "CPU_LOAD": "#e67e22",
        "PING": "#3498db",
        "IDLE": "#95a5a6",
    }

    # Panel 4: Event timeline + friction
    ax4 = fig.add_subplot(gs[1, 0])
    for i, h in enumerate(sic_history):
        color = event_colors.get(h["event_type"], "gray")
        ax4.bar(h["time"], h["friction"], color=color, alpha=0.7, width=0.8)
    ax4.axhline(y=ACTION_THRESHOLD, color="red", linestyle="--",
                linewidth=1, alpha=0.7, label=f"Action threshold ({ACTION_THRESHOLD})")

    # Legend for event types
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=c, label=k) for k, c in event_colors.items()]
    legend_elements.append(plt.Line2D([0], [0], color="red", linestyle="--",
                                       label="Action threshold"))
    ax4.legend(handles=legend_elements, fontsize=7, loc="upper right")
    ax4.set_xlabel("Time (tick)")
    ax4.set_ylabel("Friction")
    ax4.set_title("SIC v3: Reactive Layer\nFriction by Event Type",
                  fontsize=11, fontweight="bold")
    ax4.grid(True, alpha=0.3)

    # Panel 5: Causal Discovery (LOGIN->CPU_LOAD synapse)
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.plot(times, lc_weights, color="purple", linewidth=2.5,
             label="LOGIN->CPU_LOAD synapse")
    ax5.fill_between(times, lc_weights, alpha=0.15, color="purple")
    ax5.axhline(y=0.4, color="gray", linestyle=":", alpha=0.5,
                label="Initial weight (0.4)")

    # Mark actions
    for h in sic_history:
        if "PREVENT" in h["action"]:
            ax5.axvline(x=h["time"], color="green", alpha=0.3, linewidth=1)
        elif "REACT" in h["action"]:
            ax5.axvline(x=h["time"], color="red", alpha=0.3, linewidth=1)

    ax5.set_xlabel("Time (tick)")
    ax5.set_ylabel("Synapse Weight (Coherence)")
    ax5.set_ylim(0, 1)
    ax5.set_title("SIC v3: Adaptive Layer\nCausal Discovery (Hebbian)",
                  fontsize=11, fontweight="bold")
    ax5.legend(fontsize=8)
    ax5.grid(True, alpha=0.3)

    # Panel 6: Urgency = Friction + Coherence (emergent decision)
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.plot(times, frictions, color="red", alpha=0.6, linewidth=1,
             label="Friction (present pain)")
    ax6.plot(times, coherences, color="blue", alpha=0.6, linewidth=1,
             label="Coherence (future prediction)")
    ax6.plot(times, urgencies, color="darkgreen", linewidth=2,
             label="Urgency = F + Coh*0.8")
    ax6.axhline(y=ACTION_THRESHOLD, color="orange", linestyle="--",
                linewidth=1, alpha=0.7, label="Action threshold")

    # Mark actions
    for h in sic_history:
        if "PREVENT" in h["action"]:
            ax6.plot(h["time"], h["urgency"], "g^", markersize=8, alpha=0.7)
        elif "REACT" in h["action"]:
            ax6.plot(h["time"], h["urgency"], "rv", markersize=8, alpha=0.7)

    ax6.set_xlabel("Time (tick)")
    ax6.set_ylabel("Magnitude")
    ax6.set_title("SIC v3: Emergent Decisions\nComposition Friction + Coherence",
                  fontsize=11, fontweight="bold")
    ax6.legend(fontsize=7, loc="upper right")
    ax6.grid(True, alpha=0.3)

    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"[saved to {save_path}]")


# =====================================================================
# TEXT REPORT
# =====================================================================

def print_report(thermostat, sic_history):
    """Print textual summary of both simulations."""
    print("=" * 70)
    print("  SIC -- Dynamic Consciousness & Cognitive Friction Report")
    print("=" * 70)

    # Thermostat stats
    f = thermostat["friction"]
    print("\n  PART 1: Consciousness Thermostat")
    print(f"    Initial friction:     {f[0]:.4f}")
    print(f"    Min friction (crisis): {f.min():.4f} at t={np.argmin(f)}")
    print(f"    Max friction (calm):   {f.max():.4f} at t={np.argmax(f)}")
    print(f"    Final friction:        {f[-1]:.4f}")
    print(f"    Crisis period:         t={thermostat['chaos_start']}-{thermostat['chaos_end']}")

    # Phases
    pre_crisis = f[:thermostat["chaos_start"]].mean()
    during_crisis = f[thermostat["chaos_start"]:thermostat["chaos_end"]].mean()
    post_crisis = f[thermostat["chaos_end"]:].mean()
    print(f"    Avg friction pre-crisis:  {pre_crisis:.4f} (Dogma/Efficiency)")
    print(f"    Avg friction in crisis:   {during_crisis:.4f} (Plasticity/Learning)")
    print(f"    Avg friction post-crisis: {post_crisis:.4f} (Wisdom/Recovery)")

    # SIC v3 stats
    print("\n  PART 2: SIC v3 Three-Layer System")

    actions = [h["action"] for h in sic_history]
    n_prevent = sum(1 for a in actions if "PREVENT" in a)
    n_react = sum(1 for a in actions if "REACT" in a)
    n_monitor = sum(1 for a in actions if "MONITOR" in a)

    print(f"    Total ticks:     {len(sic_history)}")
    print(f"    MONITOR actions: {n_monitor}")
    print(f"    PREVENT actions: {n_prevent}")
    print(f"    REACT actions:   {n_react}")

    # Causal discovery
    final_lc = sic_history[-1]["lc_synapse"]
    print(f"    LOGIN->CPU_LOAD synapse: {final_lc:.4f}")
    if final_lc > 0.6:
        print(f"    Causal discovery:        STRONG (system learned the hidden rule)")
    elif final_lc > 0.3:
        print(f"    Causal discovery:        MODERATE (learning in progress)")
    else:
        print(f"    Causal discovery:        WEAK (insufficient exposure)")

    # Print SIC v3 event log
    print(f"\n  {'PHASE':<6} | {'EVENT':<10} | {'FRIC':<5} | {'COH':<5} | {'ACTION':<22} | SYNAPSE")
    print("  " + "-" * 72)
    for h in sic_history:
        phase_short = h["phase"][:3]
        syn = f"L->C: {h['lc_synapse']:.2f}" if h["lc_synapse"] > 0 else ""
        print(f"  {phase_short:<6} | {h['event_type']:<10} | {h['friction']:.2f}  | "
              f"{h['coherence']:.2f}  | {h['action']:<22} | {syn}")

    print("\n" + "=" * 70)


# =====================================================================
# MAIN
# =====================================================================

def main():
    parser = argparse.ArgumentParser(
        description="SIC Dynamic Consciousness & Cognitive Friction Simulation"
    )
    parser.add_argument("-o", "--output", type=str, default="conciencia.png",
                        help="Output image path (default: conciencia.png)")
    parser.add_argument("--no-plot", action="store_true",
                        help="Skip visualization (text report only)")
    parser.add_argument("-s", "--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    parser.add_argument("-t", "--ticks", type=int, default=60,
                        help="Number of SIC v3 ticks (default: 60)")
    args = parser.parse_args()

    # Part 1: Consciousness Thermostat
    thermostat = simulate_consciousness_thermostat(steps=200, seed=args.seed)

    # Part 2: SIC v3
    sic_history = simulate_sic_v3(n_ticks=args.ticks, seed=args.seed)

    # Report
    print_report(thermostat, sic_history)

    # Visualize
    if not args.no_plot:
        visualize(thermostat, sic_history, args.output)


if __name__ == "__main__":
    main()
