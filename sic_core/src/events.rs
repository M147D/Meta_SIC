//! Event system — Section 16.2
//!
//! Event-driven paradigm: no fixed-frequency loops. Events propagate
//! through contexts that "resonate" based on activation conditions.

use std::time::Instant;

/// Types of events that propagate through the context system.
#[derive(Debug, Clone, PartialEq)]
pub enum EventKind {
    /// A sensor reading changed significantly
    SensorChange,
    /// A movement or action was performed
    Movement,
    /// An internal parameter was adjusted
    ParameterAdjust,
    /// A pattern was detected by an adaptive context
    PatternDetected,
    /// The environment assessment changed
    EnvironmentChange,
    /// Custom event type
    Custom(String),
}

/// An event that propagates through the context system.
///
/// Events are value types (Clone + Send) so they can be freely
/// passed between contexts without ownership issues.
#[derive(Debug, Clone)]
pub struct Event {
    pub kind: EventKind,
    pub magnitude: f64,
    pub timestamp: Instant,
    pub extra: i32,
}

impl Event {
    pub fn new(kind: EventKind, magnitude: f64) -> Self {
        Self {
            kind,
            magnitude,
            timestamp: Instant::now(),
            extra: 0,
        }
    }

    pub fn with_extra(kind: EventKind, magnitude: f64, extra: i32) -> Self {
        Self {
            kind,
            magnitude,
            timestamp: Instant::now(),
            extra,
        }
    }

    /// Time elapsed since the event was created (for decay calculations).
    pub fn age_secs(&self) -> f64 {
        self.timestamp.elapsed().as_secs_f64()
    }
}

/// A circular event queue with fixed capacity (no allocations after init).
///
/// Models the event queue from the Arduino implementation but generalized.
pub struct EventQueue {
    buffer: Vec<Option<Event>>,
    head: usize,
    tail: usize,
    count: usize,
    capacity: usize,
}

impl EventQueue {
    pub fn new(capacity: usize) -> Self {
        Self {
            buffer: (0..capacity).map(|_| None).collect(),
            head: 0,
            tail: 0,
            count: 0,
            capacity,
        }
    }

    pub fn is_empty(&self) -> bool {
        self.count == 0
    }

    pub fn len(&self) -> usize {
        self.count
    }

    /// Enqueue an event. Returns false if the queue is full.
    pub fn enqueue(&mut self, event: Event) -> bool {
        if self.count >= self.capacity {
            return false;
        }
        self.buffer[self.tail] = Some(event);
        self.tail = (self.tail + 1) % self.capacity;
        self.count += 1;
        true
    }

    /// Dequeue the next event, if any.
    pub fn dequeue(&mut self) -> Option<Event> {
        if self.count == 0 {
            return None;
        }
        let event = self.buffer[self.head].take();
        self.head = (self.head + 1) % self.capacity;
        self.count -= 1;
        event
    }
}
