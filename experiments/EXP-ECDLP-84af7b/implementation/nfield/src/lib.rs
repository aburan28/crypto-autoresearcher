//! Number-field toolkit for the SNFS-G lift experiments (EXP-ECDLP-84af7b, EXP-ECDLP-4c6a09).
//! Pure Rust with exact big-integer and rational arithmetic; the only native dependency is the
//! optional `pari` feature, which links libpari through a tiny C shim for cross-checks (ellrank
//! over Q, nfdisc). Nothing in the measured path depends on PARI.

pub mod ecnf;
pub mod field;
pub mod gp;
pub mod modpoly;
pub mod rng;

pub use field::{Elt, NumberField};
pub use rng::Rng;
