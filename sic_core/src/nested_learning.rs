//! Nested Learning System — Section 16.1
//!
//! Three nested contexts at different timescales:
//!
//!   Reactive    {C:immediate, S:ms, P:hardware}
//!       ↕
//!   Adaptive    {C:patterns, S:seconds, P:statistical}
//!       ↕
//!   Environmental {C:environment, S:minutes, P:strategic}
//!
//! Event-driven: no polling. Contexts "resonate" with events based on
//! activation conditions. Memory decays exponentially with real time.

use crate::events::{Event, EventKind, EventQueue};
use std::time::Instant;

/// Trait for any context processor in the nested learning system.
///
/// This is the Rust formalization of the context interface from
/// Aplicaciones §16.2. Traits = formalized interfaces between contexts.
pub trait ContextProcessor {
    /// Resonance condition: should this context activate for this event?
    fn should_activate(&self, event: &Event) -> bool;

    /// Process the event and optionally generate a new event.
    fn process(&mut self, event: &Event) -> Option<Event>;

    /// Apply temporal decay based on elapsed time.
    /// decay(Δt) = value × exp(-Δt/τ)
    fn decay(&mut self, delta_t_secs: f64);
}

/// Reactive Context — direct sensor→actuator responses.
pub struct ReactiveContext {
    pub gain: f64,
    pub dead_zone: f64,
    pub position: f64,
}

impl ReactiveContext {
    pub fn new() -> Self {
        Self {
            gain: 0.5,
            dead_zone: 30.0,
            position: 90.0, // center
        }
    }
}

impl ContextProcessor for ReactiveContext {
    fn should_activate(&self, event: &Event) -> bool {
        event.kind == EventKind::SensorChange
    }

    fn process(&mut self, event: &Event) -> Option<Event> {
        let error = event.magnitude;
        if error.abs() <= self.dead_zone {
            return None;
        }

        // Proportional movement
        let delta = self.gain * (error / 512.0) * 10.0;
        self.position = (self.position + delta).clamp(0.0, 180.0);

        Some(Event::with_extra(
            EventKind::Movement,
            delta.abs(),
            error.abs() as i32,
        ))
    }

    fn decay(&mut self, _delta_t_secs: f64) {
        // Reactive context has no memory to decay
    }
}

/// Adaptive Context — detects patterns and adjusts reactive parameters.
pub struct AdaptiveContext {
    pub accumulated_energy: f64,
    pub error_avg: f64,
    pub movement_avg: f64,
    pub energy_threshold: f64,
    pub tau: f64, // time constant in seconds
    last_update: Instant,
}

impl AdaptiveContext {
    pub fn new() -> Self {
        Self {
            accumulated_energy: 0.0,
            error_avg: 0.0,
            movement_avg: 0.0,
            energy_threshold: 500.0,
            tau: 0.2, // 200ms
            last_update: Instant::now(),
        }
    }
}

impl ContextProcessor for AdaptiveContext {
    fn should_activate(&self, event: &Event) -> bool {
        matches!(
            event.kind,
            EventKind::SensorChange | EventKind::Movement
        )
    }

    fn process(&mut self, event: &Event) -> Option<Event> {
        self.accumulated_energy += event.magnitude.abs();

        // Time-aware exponential moving average
        let dt = self.last_update.elapsed().as_secs_f64();
        let alpha = (1.0 - (-dt / self.tau).exp()).clamp(0.02, 0.5);
        self.last_update = Instant::now();

        match event.kind {
            EventKind::Movement => {
                let normalized = (event.magnitude.abs() / 5.0).min(1.0);
                self.movement_avg = self.movement_avg * (1.0 - alpha) + normalized * alpha;
            }
            EventKind::SensorChange => {
                let normalized = (event.magnitude.abs() / 512.0).min(1.0);
                self.error_avg = self.error_avg * (1.0 - alpha) + normalized * alpha;
            }
            _ => {}
        }

        if self.accumulated_energy < self.energy_threshold {
            return None;
        }

        // Adaptation rules (Section 16.3)
        let mut gain_change: f64 = 0.0;

        // RULE 1: High movement + high error → reduce gain (nervous system)
        if self.movement_avg > 0.6 && self.error_avg > 0.1 {
            gain_change = -0.15;
        }
        // RULE 2: Low movement + high error → increase gain (slow system)
        if self.movement_avg < 0.2 && self.error_avg > 0.2 {
            gain_change = 0.15;
        }
        // RULE 3: High movement + low error → reduce unnecessary gain
        if self.movement_avg > 0.8 && self.error_avg < 0.06 {
            gain_change = -0.10;
        }

        self.accumulated_energy = 0.0;

        if gain_change.abs() > 0.01 {
            let direction = if gain_change > 0.0 { 1 } else { -1 };
            Some(Event::with_extra(
                EventKind::ParameterAdjust,
                gain_change,
                direction,
            ))
        } else {
            None
        }
    }

    fn decay(&mut self, delta_t_secs: f64) {
        let factor = (-delta_t_secs / self.tau).exp();
        self.accumulated_energy *= factor;

        let slow_factor = (-delta_t_secs / (self.tau * 10.0)).exp();
        self.movement_avg *= slow_factor;
        self.error_avg *= slow_factor;
    }
}

/// Environmental Context — assesses global performance and adjusts adaptive limits.
pub struct EnvironmentalContext {
    pub samples: usize,
    pub sample_threshold: usize,
    pub adjustments: usize,
    pub oscillations: usize,
    last_direction: i32,
}

impl EnvironmentalContext {
    pub fn new() -> Self {
        Self {
            samples: 0,
            sample_threshold: 50,
            adjustments: 0,
            oscillations: 0,
            last_direction: 0,
        }
    }
}

impl ContextProcessor for EnvironmentalContext {
    fn should_activate(&self, event: &Event) -> bool {
        event.kind == EventKind::ParameterAdjust
    }

    fn process(&mut self, event: &Event) -> Option<Event> {
        self.adjustments += 1;
        self.samples += 1;

        // Detect oscillations
        let dir = event.extra;
        if dir != 0 && dir != self.last_direction && self.last_direction != 0 {
            self.oscillations += 1;
        }
        self.last_direction = dir;

        if self.samples < self.sample_threshold {
            return None;
        }

        let osc_ratio = self.oscillations as f64 / self.adjustments.max(1) as f64;

        let result = if osc_ratio > 0.5 {
            // Oscillating → widen allowed ranges
            Some(Event::with_extra(
                EventKind::EnvironmentChange,
                osc_ratio,
                1, // widen
            ))
        } else if osc_ratio < 0.2 && self.adjustments > 5 {
            // Converging → narrow ranges for precision
            Some(Event::with_extra(
                EventKind::EnvironmentChange,
                osc_ratio,
                -1, // narrow
            ))
        } else {
            None
        };

        // Reset counters
        self.samples = 0;
        self.adjustments = 0;
        self.oscillations = 0;

        result
    }

    fn decay(&mut self, _delta_t_secs: f64) {
        // Environmental context has long-term memory, minimal decay
    }
}

/// The complete Nested Learning System.
///
/// Orchestrates three contexts with event-driven propagation.
pub struct NestedLearningSystem {
    pub reactive: ReactiveContext,
    pub adaptive: AdaptiveContext,
    pub environmental: EnvironmentalContext,
    pub event_queue: EventQueue,
    last_decay: Instant,
}

impl NestedLearningSystem {
    pub fn new() -> Self {
        Self {
            reactive: ReactiveContext::new(),
            adaptive: AdaptiveContext::new(),
            environmental: EnvironmentalContext::new(),
            event_queue: EventQueue::new(32),
            last_decay: Instant::now(),
        }
    }

    /// Inject a sensor event and propagate through all contexts.
    pub fn process_sensor(&mut self, sensor_value: f64) {
        self.event_queue.enqueue(Event::new(
            EventKind::SensorChange,
            sensor_value,
        ));

        // Propagate all events
        let mut iterations = 0;
        while !self.event_queue.is_empty() && iterations < 100 {
            if let Some(event) = self.event_queue.dequeue() {
                // Each context resonates if the event matches
                if self.reactive.should_activate(&event) {
                    if let Some(new_event) = self.reactive.process(&event) {
                        self.event_queue.enqueue(new_event);
                    }
                }
                if self.adaptive.should_activate(&event) {
                    if let Some(new_event) = self.adaptive.process(&event) {
                        self.event_queue.enqueue(new_event);
                    }
                }
                if self.environmental.should_activate(&event) {
                    if let Some(new_event) = self.environmental.process(&event) {
                        self.event_queue.enqueue(new_event);
                    }
                }
            }
            iterations += 1;
        }

        // Apply temporal decay
        let dt = self.last_decay.elapsed().as_secs_f64();
        if dt > 0.001 {
            self.adaptive.decay(dt);
            self.environmental.decay(dt);
            self.last_decay = Instant::now();
        }
    }
}
