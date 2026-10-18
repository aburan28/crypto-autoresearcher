// Blind-spot item 18: classify the frozen ECDLP contracts with zero run
// directories, and emit the task cards for the trials this host can run.
//
// Std only; built with rustc (see PROTOCOL.md "Instrument"). The gates G1..G9
// and every reason string are defined in PROTOCOL.md; this file implements
// them and nothing else. It runs no contract and changes no repository file
// outside --out / --work.
//
// Modes:
//   selftest    --work DIR [--out FILE]
//   scan        --repo DIR --out DIR
//   emit-cards  --repo DIR --out DIR
//   table       --repo DIR --scan DIR --receipts DIR --out FILE

use std::collections::{BTreeMap, BTreeSet, HashMap, HashSet};
use std::fmt::Write as FmtWrite;
use std::fs;
use std::io::{BufRead, BufReader, Read, Write};
use std::os::unix::fs::PermissionsExt;
use std::path::{Path, PathBuf};
use std::process::{Child, ChildStdin, ChildStdout, Command, Stdio};

// ---------------------------------------------------------------- constants

const ECDLP_CLASS: &[&str] = &[
    "ECDLP", "ECDLP2M", "OAKLEY", "CERTBIN", "NISTBIN", "CRYPTO", "PATH", "ENDO", "ECTD", "PFDR",
    "ISOU", "SATIC", "DREG", "SDEG", "SIG", "MONO", "RELN", "ICEX", "ICLIFT", "XEDN", "SEMBIN",
    "ICPERF", "GRUMPY", "LHW", "FROB", "QSP", "GFPN", "BINSTD", "AUXIN",
];
const NAMED: &[&str] = &[
    "EXP-IC-002",
    "EXP-TLD-0a6b4d",
    "EXP-AOM-e057f7",
    "EXP-PMA-001",
    "EXP-JMV-001",
];
const GENERATED: &[&str] = &[
    "launch.json",
    "execution-receipt.json",
    "command.txt",
    "environment.json",
    "stdout.log",
    "stderr.log",
    "check.stdout.log",
    "check.stderr.log",
];
const MEM_CAP_MB: f64 = 4096.0;
const TIME_CAP_S: f64 = 2700.0;
const CARD_CMD_CAP_S: u64 = 220;
const OUT_DIR_REL: &str = "research/blindspots_20261018/18-frozen-contracts";
const RULE9: &[&str] = &[
    "evidence",
    "budget",
    "test_boundary",
    "remaining_uncertainty",
    "successor_or_revisit",
];

// ------------------------------------------------------------------- sha256

fn sha256(data: &[u8]) -> String {
    const K: [u32; 64] = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4,
        0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe,
        0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f,
        0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
        0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc,
        0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
        0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116,
        0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7,
        0xc67178f2,
    ];
    let mut h: [u32; 8] = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab,
        0x5be0cd19,
    ];
    let mut msg = data.to_vec();
    let bitlen = (data.len() as u64).wrapping_mul(8);
    msg.push(0x80);
    while msg.len() % 64 != 56 {
        msg.push(0);
    }
    msg.extend_from_slice(&bitlen.to_be_bytes());
    for chunk in msg.chunks(64) {
        let mut w = [0u32; 64];
        for i in 0..16 {
            w[i] = u32::from_be_bytes([
                chunk[4 * i],
                chunk[4 * i + 1],
                chunk[4 * i + 2],
                chunk[4 * i + 3],
            ]);
        }
        for i in 16..64 {
            let s0 = w[i - 15].rotate_right(7) ^ w[i - 15].rotate_right(18) ^ (w[i - 15] >> 3);
            let s1 = w[i - 2].rotate_right(17) ^ w[i - 2].rotate_right(19) ^ (w[i - 2] >> 10);
            w[i] = w[i - 16]
                .wrapping_add(s0)
                .wrapping_add(w[i - 7])
                .wrapping_add(s1);
        }
        let mut v = h;
        for i in 0..64 {
            let s1 = v[4].rotate_right(6) ^ v[4].rotate_right(11) ^ v[4].rotate_right(25);
            let ch = (v[4] & v[5]) ^ ((!v[4]) & v[6]);
            let t1 = v[7]
                .wrapping_add(s1)
                .wrapping_add(ch)
                .wrapping_add(K[i])
                .wrapping_add(w[i]);
            let s0 = v[0].rotate_right(2) ^ v[0].rotate_right(13) ^ v[0].rotate_right(22);
            let maj = (v[0] & v[1]) ^ (v[0] & v[2]) ^ (v[1] & v[2]);
            let t2 = s0.wrapping_add(maj);
            v[7] = v[6];
            v[6] = v[5];
            v[5] = v[4];
            v[4] = v[3].wrapping_add(t1);
            v[3] = v[2];
            v[2] = v[1];
            v[1] = v[0];
            v[0] = t1.wrapping_add(t2);
        }
        for i in 0..8 {
            h[i] = h[i].wrapping_add(v[i]);
        }
    }
    let mut s = String::new();
    for x in h {
        let _ = write!(s, "{:08x}", x);
    }
    s
}

// --------------------------------------------------------------------- json

#[derive(Clone, Debug, PartialEq)]
enum J {
    Null,
    Bool(bool),
    Num(f64),
    Str(String),
    Arr(Vec<J>),
    Obj(Vec<(String, J)>),
}

impl J {
    fn get(&self, k: &str) -> Option<&J> {
        match self {
            J::Obj(v) => v.iter().find(|(a, _)| a == k).map(|(_, b)| b),
            _ => None,
        }
    }
    fn as_str(&self) -> Option<&str> {
        match self {
            J::Str(s) => Some(s),
            _ => None,
        }
    }
    fn as_f64(&self) -> Option<f64> {
        match self {
            J::Num(n) => Some(*n),
            _ => None,
        }
    }
    fn as_arr(&self) -> Option<&Vec<J>> {
        match self {
            J::Arr(a) => Some(a),
            _ => None,
        }
    }
    fn str_list(&self) -> Option<Vec<String>> {
        let a = self.as_arr()?;
        let mut out = Vec::new();
        for x in a {
            out.push(x.as_str()?.to_string());
        }
        Some(out)
    }
    fn emit(&self, out: &mut String) {
        match self {
            J::Null => out.push_str("null"),
            J::Bool(b) => out.push_str(if *b { "true" } else { "false" }),
            J::Num(n) => {
                if n.fract() == 0.0 && n.abs() < 1e15 {
                    let _ = write!(out, "{}", *n as i64);
                } else {
                    let _ = write!(out, "{}", n);
                }
            }
            J::Str(s) => {
                out.push('"');
                for c in s.chars() {
                    match c {
                        '"' => out.push_str("\\\""),
                        '\\' => out.push_str("\\\\"),
                        '\n' => out.push_str("\\n"),
                        '\r' => out.push_str("\\r"),
                        '\t' => out.push_str("\\t"),
                        c if (c as u32) < 0x20 => {
                            let _ = write!(out, "\\u{:04x}", c as u32);
                        }
                        c => out.push(c),
                    }
                }
                out.push('"');
            }
            J::Arr(a) => {
                out.push('[');
                for (i, x) in a.iter().enumerate() {
                    if i > 0 {
                        out.push(',');
                    }
                    x.emit(out);
                }
                out.push(']');
            }
            J::Obj(o) => {
                out.push('{');
                for (i, (k, v)) in o.iter().enumerate() {
                    if i > 0 {
                        out.push(',');
                    }
                    J::Str(k.clone()).emit(out);
                    out.push(':');
                    v.emit(out);
                }
                out.push('}');
            }
        }
    }
    fn to_string(&self) -> String {
        let mut s = String::new();
        self.emit(&mut s);
        s
    }
}

fn js(x: &str) -> J {
    J::Str(x.to_string())
}
fn jn(x: usize) -> J {
    J::Num(x as f64)
}
fn jobj(v: Vec<(&str, J)>) -> J {
    J::Obj(v.into_iter().map(|(k, x)| (k.to_string(), x)).collect())
}
fn jstrs(v: &[String]) -> J {
    J::Arr(v.iter().map(|s| js(s)).collect())
}

struct JP<'a> {
    b: &'a [u8],
    i: usize,
}

fn json_parse(text: &str) -> Result<J, String> {
    let mut p = JP {
        b: text.as_bytes(),
        i: 0,
    };
    let v = p.value()?;
    p.ws();
    if p.i != p.b.len() {
        return Err(format!("trailing characters at {}", p.i));
    }
    Ok(v)
}

impl<'a> JP<'a> {
    fn ws(&mut self) {
        while self.i < self.b.len() && matches!(self.b[self.i], b' ' | b'\t' | b'\n' | b'\r') {
            self.i += 1;
        }
    }
    fn value(&mut self) -> Result<J, String> {
        self.ws();
        if self.i >= self.b.len() {
            return Err("unexpected end".into());
        }
        match self.b[self.i] {
            b'{' => {
                self.i += 1;
                let mut out = Vec::new();
                self.ws();
                if self.i < self.b.len() && self.b[self.i] == b'}' {
                    self.i += 1;
                    return Ok(J::Obj(out));
                }
                loop {
                    self.ws();
                    let k = match self.string()? {
                        J::Str(s) => s,
                        _ => unreachable!(),
                    };
                    self.ws();
                    if self.i >= self.b.len() || self.b[self.i] != b':' {
                        return Err(format!("expected ':' at {}", self.i));
                    }
                    self.i += 1;
                    let v = self.value()?;
                    out.push((k, v));
                    self.ws();
                    if self.i >= self.b.len() {
                        return Err("unterminated object".into());
                    }
                    match self.b[self.i] {
                        b',' => self.i += 1,
                        b'}' => {
                            self.i += 1;
                            return Ok(J::Obj(out));
                        }
                        _ => return Err(format!("expected ',' or '}}' at {}", self.i)),
                    }
                }
            }
            b'[' => {
                self.i += 1;
                let mut out = Vec::new();
                self.ws();
                if self.i < self.b.len() && self.b[self.i] == b']' {
                    self.i += 1;
                    return Ok(J::Arr(out));
                }
                loop {
                    out.push(self.value()?);
                    self.ws();
                    if self.i >= self.b.len() {
                        return Err("unterminated array".into());
                    }
                    match self.b[self.i] {
                        b',' => self.i += 1,
                        b']' => {
                            self.i += 1;
                            return Ok(J::Arr(out));
                        }
                        _ => return Err(format!("expected ',' or ']' at {}", self.i)),
                    }
                }
            }
            b'"' => self.string(),
            b't' if self.b[self.i..].starts_with(b"true") => {
                self.i += 4;
                Ok(J::Bool(true))
            }
            b'f' if self.b[self.i..].starts_with(b"false") => {
                self.i += 5;
                Ok(J::Bool(false))
            }
            b'n' if self.b[self.i..].starts_with(b"null") => {
                self.i += 4;
                Ok(J::Null)
            }
            _ => {
                let st = self.i;
                while self.i < self.b.len()
                    && matches!(
                        self.b[self.i],
                        b'-' | b'+' | b'.' | b'e' | b'E' | b'0'..=b'9'
                    )
                {
                    self.i += 1;
                }
                let t = std::str::from_utf8(&self.b[st..self.i]).map_err(|e| e.to_string())?;
                t.parse::<f64>()
                    .map(J::Num)
                    .map_err(|_| format!("bad token at {}", st))
            }
        }
    }
    fn string(&mut self) -> Result<J, String> {
        if self.i >= self.b.len() || self.b[self.i] != b'"' {
            return Err(format!("expected string at {}", self.i));
        }
        self.i += 1;
        let mut out: Vec<u8> = Vec::new();
        while self.i < self.b.len() {
            let c = self.b[self.i];
            self.i += 1;
            match c {
                b'"' => return Ok(J::Str(String::from_utf8_lossy(&out).into_owned())),
                b'\\' => {
                    if self.i >= self.b.len() {
                        break;
                    }
                    let e = self.b[self.i];
                    self.i += 1;
                    match e {
                        b'n' => out.push(b'\n'),
                        b't' => out.push(b'\t'),
                        b'r' => out.push(b'\r'),
                        b'b' => out.push(8),
                        b'f' => out.push(12),
                        b'u' => {
                            if self.i + 4 > self.b.len() {
                                return Err("bad \\u escape".into());
                            }
                            let hex = std::str::from_utf8(&self.b[self.i..self.i + 4])
                                .map_err(|e| e.to_string())?;
                            let cp = u32::from_str_radix(hex, 16).map_err(|e| e.to_string())?;
                            self.i += 4;
                            let ch = char::from_u32(cp).unwrap_or('\u{fffd}');
                            let mut buf = [0u8; 4];
                            out.extend_from_slice(ch.encode_utf8(&mut buf).as_bytes());
                        }
                        other => out.push(other),
                    }
                }
                _ => out.push(c),
            }
        }
        Err("unterminated string".into())
    }
}

// ---------------------------------------------------------------- yaml-lite
// A reader for the YAML the repository's records use: block maps and
// sequences, inline maps in sequence items, one-line and multi-line flow
// collections, quoted / plain (multi-line) / block scalars, comments. Scalars
// stay text; no anchors, tags or merge keys. A line it cannot place is an
// error, reported by the caller, never skipped.

#[derive(Clone, Debug)]
enum Y {
    Null,
    Str(String),
    Seq(Vec<Y>),
    Map(Vec<(String, Y)>),
}

impl Y {
    fn get(&self, k: &str) -> Option<&Y> {
        match self {
            Y::Map(v) => v.iter().find(|(a, _)| a == k).map(|(_, b)| b),
            _ => None,
        }
    }
    fn str(&self) -> Option<&str> {
        match self {
            Y::Str(s) => Some(s),
            _ => None,
        }
    }
    fn seq(&self) -> Option<&Vec<Y>> {
        match self {
            Y::Seq(v) => Some(v),
            _ => None,
        }
    }
    fn flat_text(&self) -> String {
        match self {
            Y::Null => String::new(),
            Y::Str(s) => s.clone(),
            Y::Seq(v) => v
                .iter()
                .map(|x| x.flat_text())
                .collect::<Vec<_>>()
                .join(" "),
            Y::Map(v) => v
                .iter()
                .map(|(_, x)| x.flat_text())
                .collect::<Vec<_>>()
                .join(" "),
        }
    }
    fn truthy(&self) -> bool {
        match self {
            Y::Null => false,
            Y::Str(s) => !s.trim().is_empty(),
            Y::Seq(v) => !v.is_empty(),
            Y::Map(v) => !v.is_empty(),
        }
    }
}

struct YP {
    lines: Vec<String>,
    i: usize,
}

fn indent_of(l: &str) -> usize {
    l.len() - l.trim_start_matches(' ').len()
}
fn blank_or_comment(l: &str) -> bool {
    let t = l.trim();
    t.is_empty() || t.starts_with('#')
}
fn is_seq_line(t: &str) -> bool {
    t == "-" || t.starts_with("- ")
}

fn strip_plain_comment(s: &str) -> &str {
    match s.find(" #") {
        Some(p) => s[..p].trim_end(),
        None => s.trim_end(),
    }
}

// Split "key: rest" at the first key colon; None when the text is not a key line.
fn find_key(t: &str) -> Option<(String, String)> {
    let b = t.as_bytes();
    if b.is_empty() {
        return None;
    }
    if b[0] == b'"' || b[0] == b'\'' {
        let q = b[0];
        let mut i = 1;
        while i < b.len() {
            if b[i] == q {
                if q == b'\'' && i + 1 < b.len() && b[i + 1] == b'\'' {
                    i += 2;
                    continue;
                }
                break;
            }
            if q == b'"' && b[i] == b'\\' {
                i += 1;
            }
            i += 1;
        }
        if i >= b.len() {
            return None;
        }
        let key = t[1..i].to_string();
        let rest = &t[i + 1..];
        let rt = rest.trim_start();
        if rt.starts_with(':') && (rt.len() == 1 || rt[1..].starts_with(' ')) {
            return Some((key, rt[1..].trim().to_string()));
        }
        return None;
    }
    if matches!(
        b[0],
        b'[' | b'{' | b'|' | b'>' | b'#' | b'&' | b'*' | b'!' | b'%' | b'@' | b'`'
    ) {
        return None;
    }
    let mut i = 0;
    while i < b.len() {
        if b[i] == b':' && (i + 1 == b.len() || b[i + 1] == b' ') {
            return Some((t[..i].trim_end().to_string(), t[i + 1..].trim().to_string()));
        }
        i += 1;
    }
    None
}

fn unquote_double(s: &str) -> String {
    let mut out = String::new();
    let mut it = s.chars();
    while let Some(c) = it.next() {
        if c == '\\' {
            match it.next() {
                Some('n') => out.push('\n'),
                Some('t') => out.push('\t'),
                Some('"') => out.push('"'),
                Some('\\') => out.push('\\'),
                Some('/') => out.push('/'),
                Some(o) => {
                    out.push('\\');
                    out.push(o);
                }
                None => out.push('\\'),
            }
        } else {
            out.push(c);
        }
    }
    out
}

// Parse a quoted scalar starting at text[0]; returns (value, bytes consumed) or None if unterminated.
fn read_quoted(t: &str) -> Option<(String, usize)> {
    let b = t.as_bytes();
    let q = b[0];
    let mut i = 1;
    while i < b.len() {
        if q == b'\'' && b[i] == b'\'' {
            if i + 1 < b.len() && b[i + 1] == b'\'' {
                i += 2;
                continue;
            }
            return Some((t[1..i].replace("''", "'"), i + 1));
        }
        if q == b'"' {
            if b[i] == b'\\' {
                i += 2;
                continue;
            }
            if b[i] == b'"' {
                return Some((unquote_double(&t[1..i]), i + 1));
            }
        }
        i += 1;
    }
    None
}

// Incremental bracket/quote state of a flow collection spread over lines.
struct FlowBal {
    depth: i32,
    q: Option<char>,
    prev: char,
}

impl FlowBal {
    fn new() -> FlowBal {
        FlowBal {
            depth: 0,
            q: None,
            prev: ' ',
        }
    }
    fn feed(&mut self, s: &str) {
        let mut it = s.chars();
        while let Some(c) = it.next() {
            match self.q {
                Some(qc) => {
                    if qc == '"' && c == '\\' {
                        it.next();
                    } else if c == qc {
                        self.q = None;
                        self.prev = c;
                    }
                }
                None => {
                    match c {
                        // a quote opens a quoted scalar only at the start of a flow token
                        '"' | '\'' if matches!(self.prev, ' ' | '[' | '{' | ',' | ':') => {
                            self.q = Some(c)
                        }
                        '[' | '{' => self.depth += 1,
                        ']' | '}' => self.depth -= 1,
                        _ => {}
                    }
                    if !c.is_whitespace() && self.q.is_none() {
                        self.prev = c;
                    } else if c.is_whitespace() && !matches!(self.prev, '[' | '{' | ',' | ':') {
                        self.prev = ' ';
                    }
                }
            }
        }
    }
    fn balanced(&self) -> bool {
        self.depth <= 0 && self.q.is_none()
    }
}

struct FlowP {
    c: Vec<char>,
    i: usize,
}

impl FlowP {
    fn ws(&mut self) {
        while self.i < self.c.len() && self.c[self.i].is_whitespace() {
            self.i += 1;
        }
    }
    fn node(&mut self) -> Result<Y, String> {
        self.ws();
        if self.i >= self.c.len() {
            return Ok(Y::Null);
        }
        match self.c[self.i] {
            '[' => {
                self.i += 1;
                let mut out = Vec::new();
                loop {
                    self.ws();
                    if self.i >= self.c.len() {
                        return Err("unterminated flow sequence".into());
                    }
                    if self.c[self.i] == ']' {
                        self.i += 1;
                        return Ok(Y::Seq(out));
                    }
                    let before = self.i;
                    out.push(self.node()?);
                    self.ws();
                    if self.i < self.c.len() && self.c[self.i] == ',' {
                        self.i += 1;
                    } else if self.i == before {
                        return Err("flow sequence: unexpected character".into());
                    }
                }
            }
            '{' => {
                self.i += 1;
                let mut out = Vec::new();
                loop {
                    self.ws();
                    if self.i >= self.c.len() {
                        return Err("unterminated flow mapping".into());
                    }
                    if self.c[self.i] == '}' {
                        self.i += 1;
                        return Ok(Y::Map(out));
                    }
                    let before = self.i;
                    let k = match self.scalar(true)? {
                        Y::Str(s) => s,
                        _ => String::new(),
                    };
                    self.ws();
                    let v = if self.i < self.c.len() && self.c[self.i] == ':' {
                        self.i += 1;
                        self.node()?
                    } else {
                        Y::Null
                    };
                    out.push((k, v));
                    self.ws();
                    if self.i < self.c.len() && self.c[self.i] == ',' {
                        self.i += 1;
                    } else if self.i == before {
                        return Err("flow mapping: unexpected character".into());
                    }
                }
            }
            _ => self.scalar(false),
        }
    }
    fn scalar(&mut self, key: bool) -> Result<Y, String> {
        self.ws();
        if self.i < self.c.len() && (self.c[self.i] == '"' || self.c[self.i] == '\'') {
            let rest: String = self.c[self.i..].iter().collect();
            let (v, used) = read_quoted(&rest).ok_or("unterminated quoted scalar in flow")?;
            self.i += rest[..used].chars().count();
            return Ok(Y::Str(v));
        }
        let st = self.i;
        while self.i < self.c.len() {
            let ch = self.c[self.i];
            if ch == ',' || ch == ']' || ch == '}' {
                break;
            }
            if ch == ':' && key && (self.i + 1 >= self.c.len() || self.c[self.i + 1] == ' ') {
                break;
            }
            self.i += 1;
        }
        let s: String = self.c[st..self.i].iter().collect();
        let s = s.trim();
        if matches!(s, "null" | "Null" | "NULL" | "~") {
            return Ok(Y::Null);
        }
        Ok(Y::Str(s.to_string()))
    }
}

fn parse_flow(s: &str) -> Result<Y, String> {
    let mut p = FlowP {
        c: s.chars().collect(),
        i: 0,
    };
    p.node()
}

impl YP {
    fn skip(&mut self) {
        while self.i < self.lines.len() && blank_or_comment(&self.lines[self.i]) {
            self.i += 1;
        }
    }
    fn next_sig(&self, from: usize) -> Option<usize> {
        let mut k = from;
        while k < self.lines.len() {
            if !blank_or_comment(&self.lines[k]) {
                return Some(k);
            }
            k += 1;
        }
        None
    }
    fn err<T>(&self, m: &str) -> Result<T, String> {
        Err(format!("line {}: {}", self.i + 1, m))
    }

    fn value_at(&mut self, min_indent: usize) -> Result<Y, String> {
        self.skip();
        if self.i >= self.lines.len() {
            return Ok(Y::Null);
        }
        let ind = indent_of(&self.lines[self.i]);
        if ind < min_indent {
            return Ok(Y::Null);
        }
        let t = self.lines[self.i].trim_start().to_string();
        if is_seq_line(&t) {
            self.seq(ind)
        } else if find_key(&t).is_some() {
            self.map(ind)
        } else {
            self.i += 1;
            self.scalar(&t, ind as i64 - 1)
        }
    }

    fn seq(&mut self, ind: usize) -> Result<Y, String> {
        let mut out = Vec::new();
        loop {
            self.skip();
            if self.i >= self.lines.len() {
                break;
            }
            let li = indent_of(&self.lines[self.i]);
            if li < ind {
                break;
            }
            if li > ind {
                return self.err("unexpected indent in sequence");
            }
            let t = self.lines[self.i].trim_start().to_string();
            if !is_seq_line(&t) {
                break;
            }
            let after = if t == "-" { "" } else { &t[2..] };
            let after_trim = after.trim_start();
            let offset = 1 + (after.len() - after_trim.len()) + if t == "-" { 0 } else { 1 };
            if after_trim.is_empty() || after_trim.starts_with('#') {
                self.i += 1;
                self.skip();
                if self.i < self.lines.len() && indent_of(&self.lines[self.i]) > ind {
                    out.push(self.value_at(ind + 1)?);
                } else {
                    out.push(Y::Null);
                }
            } else if is_seq_line(after_trim) || find_key(after_trim).is_some() {
                let new_ind = ind + offset;
                self.lines[self.i] = format!("{}{}", " ".repeat(new_ind), after_trim);
                out.push(self.value_at(new_ind)?);
            } else {
                let a = after_trim.to_string();
                self.i += 1;
                out.push(self.scalar(&a, ind as i64)?);
            }
        }
        Ok(Y::Seq(out))
    }

    fn map(&mut self, ind: usize) -> Result<Y, String> {
        let mut out: Vec<(String, Y)> = Vec::new();
        loop {
            self.skip();
            if self.i >= self.lines.len() {
                break;
            }
            let li = indent_of(&self.lines[self.i]);
            if li < ind {
                break;
            }
            if li > ind {
                return self.err("unexpected indent in mapping");
            }
            let t = self.lines[self.i].trim_start().to_string();
            if is_seq_line(&t) {
                break;
            }
            let (key, rest) = match find_key(&t) {
                Some(kr) => kr,
                None => return self.err("expected 'key: value'"),
            };
            self.i += 1;
            let mut rest = rest.trim().to_string();
            if rest.starts_with('&') {
                // an anchor: drop the name, keep what follows it
                rest = match rest.split_once(' ') {
                    Some((_, tail)) => tail.trim().to_string(),
                    None => String::new(),
                };
            }
            let val = if rest.is_empty() || rest.starts_with('#') {
                self.skip();
                if self.i < self.lines.len() {
                    let ni = indent_of(&self.lines[self.i]);
                    let nt = self.lines[self.i].trim_start();
                    if ni > ind {
                        self.value_at(ind + 1)?
                    } else if ni == ind && is_seq_line(nt) {
                        self.seq(ind)?
                    } else {
                        Y::Null
                    }
                } else {
                    Y::Null
                }
            } else if rest.starts_with('|') || rest.starts_with('>') {
                self.block_scalar(ind)
            } else {
                self.scalar(&rest, ind as i64)?
            };
            out.push((key, val));
        }
        Ok(Y::Map(out))
    }

    fn block_scalar(&mut self, ind: usize) -> Y {
        let mut parts: Vec<String> = Vec::new();
        while self.i < self.lines.len() {
            let l = &self.lines[self.i];
            if l.trim().is_empty() || indent_of(l) > ind {
                parts.push(l.trim().to_string());
                self.i += 1;
            } else {
                break;
            }
        }
        Y::Str(parts.join("\n").trim().to_string())
    }

    // first: the text of the value on its own line (self.i already past that line)
    fn scalar(&mut self, first: &str, parent: i64) -> Result<Y, String> {
        let f = first.trim();
        if f.starts_with('"') || f.starts_with('\'') {
            let mut text = f.to_string();
            let start_line = self.i;
            loop {
                if let Some((v, _)) = read_quoted(&text) {
                    return Ok(Y::Str(v));
                }
                if self.i >= self.lines.len() {
                    return Err(format!("line {}: unterminated quoted scalar", start_line));
                }
                text.push(' ');
                text.push_str(self.lines[self.i].trim());
                self.i += 1;
            }
        }
        if f.starts_with('[') || f.starts_with('{') {
            let mut text = f.to_string();
            let start_line = self.i;
            let mut bal = FlowBal::new();
            bal.feed(&text);
            while !bal.balanced() {
                if self.i >= self.lines.len() {
                    return Err(format!("line {}: unterminated flow collection", start_line));
                }
                let l = self.lines[self.i].trim();
                if !l.starts_with('#') {
                    text.push(' ');
                    text.push_str(l);
                    bal.feed(" ");
                    bal.feed(l);
                }
                self.i += 1;
            }
            return parse_flow(&text);
        }
        let mut text = strip_plain_comment(f).to_string();
        loop {
            match self.next_sig(self.i) {
                Some(k) if (indent_of(&self.lines[k]) as i64) > parent => {
                    let t = strip_plain_comment(self.lines[k].trim());
                    text.push(' ');
                    text.push_str(t);
                    self.i = k + 1;
                }
                _ => break,
            }
        }
        if matches!(text.as_str(), "null" | "Null" | "NULL" | "~") {
            return Ok(Y::Null);
        }
        Ok(Y::Str(text))
    }
}

fn yaml_parse(text: &str) -> Result<Y, String> {
    let mut lines = Vec::new();
    for l in text.lines() {
        let l = l.trim_end_matches('\r');
        if l == "---" || l == "..." || l.starts_with("%YAML") {
            continue;
        }
        if l.starts_with('\t') {
            return Err("tab indentation".into());
        }
        lines.push(l.to_string());
    }
    let mut p = YP { lines, i: 0 };
    let v = p.value_at(0)?;
    p.skip();
    if p.i < p.lines.len() {
        return Err(format!("line {}: content after the document", p.i + 1));
    }
    Ok(v)
}

// ---------------------------------------------------------------------- git

fn run_cmd(
    prog: &str,
    args: &[&str],
    cwd: Option<&Path>,
) -> Result<(i32, Vec<u8>, Vec<u8>), String> {
    let mut c = Command::new(prog);
    c.args(args);
    if let Some(d) = cwd {
        c.current_dir(d);
    }
    let o = c.output().map_err(|e| format!("{}: {}", prog, e))?;
    Ok((o.status.code().unwrap_or(-1), o.stdout, o.stderr))
}

fn git(repo: &Path, args: &[&str]) -> Result<Vec<u8>, String> {
    let mut a: Vec<&str> = vec!["-C", repo.to_str().unwrap_or(".")];
    a.extend_from_slice(args);
    let (code, out, err) = run_cmd("git", &a, None)?;
    if code != 0 {
        return Err(format!(
            "git {:?} exited {}: {}",
            args,
            code,
            String::from_utf8_lossy(&err).trim()
        ));
    }
    Ok(out)
}

struct Blobs {
    child: Child,
    stdin: ChildStdin,
    out: BufReader<ChildStdout>,
}

impl Blobs {
    fn new(repo: &Path) -> Result<Blobs, String> {
        let mut child = Command::new("git")
            .arg("-C")
            .arg(repo)
            .args(["cat-file", "--batch"])
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .spawn()
            .map_err(|e| format!("git cat-file: {}", e))?;
        let stdin = child.stdin.take().ok_or("no stdin")?;
        let out = BufReader::new(child.stdout.take().ok_or("no stdout")?);
        Ok(Blobs { child, stdin, out })
    }
    // The blob at HEAD:path, or None when HEAD does not have it.
    fn get(&mut self, path: &str) -> Option<Vec<u8>> {
        if writeln!(self.stdin, "HEAD:{}", path).is_err() || self.stdin.flush().is_err() {
            return None;
        }
        let mut header = String::new();
        if self.out.read_line(&mut header).ok()? == 0 {
            return None;
        }
        let header = header.trim_end();
        if header.ends_with("missing") || header.ends_with("ambiguous") {
            return None;
        }
        let size: usize = header.rsplit(' ').next()?.parse().ok()?;
        if !header.contains(" blob ") {
            // a tree or something else: drain it
            let mut buf = vec![0u8; size + 1];
            self.out.read_exact(&mut buf).ok()?;
            return None;
        }
        let mut buf = vec![0u8; size + 1];
        self.out.read_exact(&mut buf).ok()?;
        buf.pop();
        Some(buf)
    }
}

impl Drop for Blobs {
    fn drop(&mut self) {
        let _ = self.child.kill();
        let _ = self.child.wait();
    }
}

fn which(prog: &str) -> bool {
    if prog.contains('/') {
        return Path::new(prog).is_file();
    }
    match std::env::var("PATH") {
        Ok(p) => p.split(':').any(|d| {
            let f = Path::new(d).join(prog);
            f.is_file()
                && fs::metadata(&f)
                    .map(|m| m.permissions().mode() & 0o111 != 0)
                    .unwrap_or(false)
        }),
        Err(_) => false,
    }
}

fn read_text(p: &Path) -> Option<String> {
    fs::read(p)
        .ok()
        .map(|b| String::from_utf8_lossy(&b).into_owned())
}

fn write_file(p: &Path, s: &str) -> Result<(), String> {
    if let Some(d) = p.parent() {
        fs::create_dir_all(d).map_err(|e| format!("{}: {}", d.display(), e))?;
    }
    fs::write(p, s).map_err(|e| format!("{}: {}", p.display(), e))
}

// ------------------------------------------------------------ model: world

#[derive(Clone, Debug)]
struct Spec {
    id: String,
    status: String,
    approved_by: String,
    exec_auth_false: bool,
    frozen_true: bool,
    supersedes: Vec<String>,
    wall: Option<f64>,
}

#[derive(Clone, Debug)]
struct TrialRes {
    id: String,
    run_id: String,
    memory_mb: f64,
    watchdog: Option<f64>,
    runnable: bool,
    reasons: Vec<String>,
    argv: Vec<String>,
    check_argv: Vec<String>,
    artifacts: Vec<String>,
    depends_on: Vec<String>,
}

#[derive(Clone, Debug)]
struct Row {
    id: String,
    area: String,
    scope: &'static str,
    status: String,
    gate: String,
    reason: String,
    outcome: &'static str,
    has_plan: bool,
    run_state: &'static str,
    approvals: Vec<String>,
    off_main: Vec<String>,
    trials: Vec<TrialRes>,
    spec_error: String,
}

struct Decision {
    id: String,
    decided_at: String,
    record: Y,
}

struct World {
    repo: PathBuf,
    head: String,
    blobs: Blobs,
    exp_files: BTreeMap<String, Vec<String>>,
    dec_files: Vec<String>,
    ecc_areas: Vec<String>,
    approvals: HashMap<String, Vec<String>>,
    withheld: HashMap<String, String>,
    off_main: HashMap<String, Vec<String>>,
    off_main_probe: String,
    decision_parse_failures: Vec<String>,
    decisions_parsed: usize,
    stdlib: HashSet<String>,
    stdlib_probe: String,
    module_cache: HashMap<String, bool>,
}

fn area_of(id: &str) -> Option<String> {
    let rest = id.strip_prefix("EXP-")?;
    let a: String = rest
        .chars()
        .take_while(|c| c.is_ascii_uppercase() || c.is_ascii_digit())
        .collect();
    if a.is_empty() || !rest[a.len()..].starts_with('-') {
        None
    } else {
        Some(a)
    }
}

// The EXP ids named in a text (the regex EXP-[A-Za-z0-9]+-(?:[0-9a-fA-F]{6}|\d{3})).
fn exp_ids_in(text: &str) -> Vec<String> {
    let b = text.as_bytes();
    let mut out = Vec::new();
    let mut i = 0;
    while i + 4 <= b.len() {
        if &b[i..i + 4] == b"EXP-" {
            let mut j = i + 4;
            while j < b.len() && b[j].is_ascii_alphanumeric() {
                j += 1;
            }
            if j > i + 4 && j < b.len() && b[j] == b'-' {
                let mut k = j + 1;
                while k < b.len() && b[k].is_ascii_alphanumeric() {
                    k += 1;
                }
                let tail = &b[j + 1..k];
                let take = if tail.len() >= 6 && tail[..6].iter().all(|c| c.is_ascii_hexdigit()) {
                    6
                } else if tail.len() >= 3 && tail[..3].iter().all(|c| c.is_ascii_digit()) {
                    3
                } else {
                    0
                };
                if take > 0 {
                    out.push(text[i..j + 1 + take].to_string());
                    i = j + 1 + take;
                    continue;
                }
            }
        }
        i += 1;
    }
    out
}

fn parse_spec(text: &str, dir_id: &str) -> Result<Spec, String> {
    let doc = yaml_parse(text)?;
    let exp = match doc.get("experiment") {
        Some(e @ Y::Map(_)) => e.clone(),
        _ => doc.clone(),
    };
    if !matches!(exp, Y::Map(_)) {
        return Err("specification is not a mapping".into());
    }
    let s = |k: &str| {
        exp.get(k)
            .map(|y| y.flat_text().trim().to_string())
            .unwrap_or_default()
    };
    let wall = exp
        .get("budget")
        .and_then(|b| b.get("wall_clock_seconds_per_run"))
        .and_then(|y| y.str())
        .and_then(|t| t.trim().parse::<f64>().ok());
    let id = s("id");
    Ok(Spec {
        id: if id.is_empty() {
            dir_id.to_string()
        } else {
            id
        },
        status: s("status"),
        approved_by: s("approved_by"),
        exec_auth_false: s("execution_authorized").eq_ignore_ascii_case("false"),
        frozen_true: s("frozen").eq_ignore_ascii_case("true"),
        supersedes: exp
            .get("supersedes")
            .map(|y| exp_ids_in(&y.flat_text()))
            .unwrap_or_default(),
        wall,
    })
}

fn ecc_areas_from(text: &str) -> Vec<String> {
    let mut out = Vec::new();
    let mut inside = false;
    for l in text.lines() {
        if l.starts_with("ecc_areas:") {
            inside = true;
            continue;
        }
        if inside {
            let t = l.trim_start();
            if t.starts_with("- ") {
                let v = t[2..].split('#').next().unwrap_or("").trim();
                if !v.is_empty() {
                    out.push(v.to_string());
                }
            } else if !l.is_empty() && !t.starts_with('#') && !l.starts_with(' ') {
                break;
            }
        }
    }
    out
}

impl World {
    fn load(repo: &Path) -> Result<World, String> {
        let repo = repo.to_path_buf();
        let head = String::from_utf8_lossy(&git(&repo, &["rev-parse", "HEAD"])?)
            .trim()
            .to_string();
        let mut blobs = Blobs::new(&repo)?;
        // HEAD file lists
        let tree = git(
            &repo,
            &[
                "ls-tree",
                "-r",
                "-z",
                "--name-only",
                "HEAD",
                "--",
                "experiments",
                "ledger/decisions",
            ],
        )?;
        let mut exp_files: BTreeMap<String, Vec<String>> = BTreeMap::new();
        let mut dec_files = Vec::new();
        for name in tree.split(|b| *b == 0) {
            if name.is_empty() {
                continue;
            }
            let name = String::from_utf8_lossy(name).into_owned();
            if let Some(rest) = name.strip_prefix("experiments/") {
                if let Some((id, f)) = rest.split_once('/') {
                    if id.starts_with("EXP-") {
                        exp_files
                            .entry(id.to_string())
                            .or_default()
                            .push(f.to_string());
                    }
                }
            } else if name.starts_with("ledger/decisions/")
                && (name.ends_with(".yaml") || name.ends_with(".yml"))
            {
                dec_files.push(name);
            }
        }
        // ECC areas
        let ecc_areas = blobs
            .get("orchestration/research-priority.yaml")
            .map(|b| ecc_areas_from(&String::from_utf8_lossy(&b)))
            .unwrap_or_default();
        // decisions
        let mut decisions: Vec<Decision> = Vec::new();
        let mut approvals: HashMap<String, Vec<String>> = HashMap::new();
        let mut failures = Vec::new();
        let mut parsed = 0usize;
        for f in &dec_files {
            let text = match blobs.get(f) {
                Some(b) => String::from_utf8_lossy(&b).into_owned(),
                None => continue,
            };
            let relevant = text.contains("approve")
                || text.contains("withheld_contracts")
                || text.contains("released_contracts");
            if !relevant {
                continue;
            }
            let doc = match yaml_parse(&text) {
                Ok(d) => d,
                Err(e) => {
                    failures.push(format!("{}: {}", f, e));
                    continue;
                }
            };
            parsed += 1;
            let cd = match doc.get("coordinator_decision") {
                Some(c @ Y::Map(_)) => c.clone(),
                _ => continue,
            };
            let stem = Path::new(f)
                .file_stem()
                .and_then(|s| s.to_str())
                .unwrap_or("")
                .to_string();
            let did = cd
                .get("id")
                .and_then(|y| y.str())
                .map(|s| s.to_string())
                .unwrap_or(stem);
            if cd.get("decision").and_then(|y| y.str()).map(|s| s.trim()) == Some("approve") {
                if let Some(Y::Seq(t)) = cd.get("target_ids") {
                    for x in t {
                        if let Some(s) = x.str() {
                            approvals
                                .entry(s.trim().to_string())
                                .or_default()
                                .push(did.clone());
                        }
                    }
                }
            }
            if cd.get("withheld_contracts").is_some() || cd.get("released_contracts").is_some() {
                let decided = cd
                    .get("decided_at")
                    .and_then(|y| y.str())
                    .unwrap_or("")
                    .replace(' ', "T");
                decisions.push(Decision {
                    id: did,
                    decided_at: decided,
                    record: cd,
                });
            }
        }
        // withheld state, ascending (decided_at, id)
        decisions.sort_by(|a, b| {
            (a.decided_at.as_str(), a.id.as_str()).cmp(&(b.decided_at.as_str(), b.id.as_str()))
        });
        let mut withheld: HashMap<String, String> = HashMap::new();
        for d in &decisions {
            for key in ["withheld_contracts", "released_contracts"] {
                let blocks: Vec<&Y> = match d.record.get(key) {
                    Some(Y::Seq(v)) => v.iter().collect(),
                    Some(m @ Y::Map(_)) => vec![m],
                    _ => vec![],
                };
                for b in blocks {
                    let ids: Vec<String> = match b.get("ids") {
                        Some(Y::Seq(v)) => v
                            .iter()
                            .filter_map(|x| match x {
                                Y::Str(s) => Some(s.trim().to_string()),
                                Y::Map(_) => x
                                    .get("id")
                                    .and_then(|i| i.str())
                                    .map(|s| s.trim().to_string()),
                                _ => None,
                            })
                            .filter(|s| !s.is_empty())
                            .collect(),
                        _ => continue,
                    };
                    if key == "released_contracts" {
                        for i in ids {
                            withheld.remove(&i);
                        }
                        continue;
                    }
                    let guard_ok = match b.get("rule_9_fields") {
                        Some(f @ Y::Map(_)) => RULE9
                            .iter()
                            .all(|k| f.get(k).map(|y| y.truthy()).unwrap_or(false)),
                        _ => false,
                    };
                    if !guard_ok {
                        continue;
                    }
                    for i in ids {
                        withheld.insert(i, d.id.clone());
                    }
                }
            }
        }
        // runs on other remote branches
        let mut off_main: HashMap<String, Vec<String>> = HashMap::new();
        let probe;
        match git(
            &repo,
            &[
                "log",
                "--remotes=origin",
                "--not",
                "origin/main",
                "--name-only",
                "--format=@@%D",
                "--",
                "experiments/*/runs/*",
            ],
        ) {
            Ok(out) => {
                let mut refs: Vec<String> = Vec::new();
                for line in String::from_utf8_lossy(&out).lines() {
                    if let Some(r) = line.strip_prefix("@@") {
                        refs = r
                            .split(',')
                            .map(|x| x.trim().to_string())
                            .filter(|x| !x.is_empty())
                            .collect();
                        continue;
                    }
                    let parts: Vec<&str> = line.split('/').collect();
                    if parts.len() >= 3 && parts[0] == "experiments" && parts[2] == "runs" {
                        let e = off_main.entry(parts[1].to_string()).or_default();
                        if refs.is_empty() {
                            if !e.contains(&"(unnamed commit)".to_string()) {
                                e.push("(unnamed commit)".into());
                            }
                        }
                        for r in &refs {
                            if !e.contains(r) {
                                e.push(r.clone());
                            }
                        }
                    }
                }
                probe = "ok".to_string();
            }
            Err(e) => probe = format!("failed: {}", e),
        }
        // python stdlib names
        let (stdlib, stdlib_probe) = match run_cmd(
            "python3",
            &[
                "-c",
                "import sys;print(' '.join(sorted(sys.stdlib_module_names)))",
            ],
            None,
        ) {
            Ok((0, o, _)) => (
                String::from_utf8_lossy(&o)
                    .split_whitespace()
                    .map(|s| s.to_string())
                    .collect::<HashSet<_>>(),
                "ok".to_string(),
            ),
            Ok((c, _, e)) => (
                HashSet::new(),
                format!("failed: exit {} {}", c, String::from_utf8_lossy(&e).trim()),
            ),
            Err(e) => (HashSet::new(), format!("failed: {}", e)),
        };
        Ok(World {
            repo,
            head,
            blobs,
            exp_files,
            dec_files,
            ecc_areas,
            approvals,
            withheld,
            off_main,
            off_main_probe: probe,
            decision_parse_failures: failures,
            decisions_parsed: parsed,
            stdlib,
            stdlib_probe,
            module_cache: HashMap::new(),
        })
    }

    fn module_available(&mut self, m: &str) -> bool {
        if let Some(v) = self.module_cache.get(m) {
            return *v;
        }
        let code = "import importlib.util as u,sys\nsys.exit(0 if u.find_spec(sys.argv[1]) is not None else 1)";
        let ok = matches!(
            run_cmd("python3", &["-c", code, m], Some(&self.repo)),
            Ok((0, _, _))
        );
        self.module_cache.insert(m.to_string(), ok);
        ok
    }
}

// Imported top-level module names in a Python source.
fn py_imports(src: &str) -> BTreeSet<String> {
    let ident = |s: &str| !s.is_empty() && s.chars().all(|c| c.is_ascii_alphanumeric() || c == '_');
    let mut out = BTreeSet::new();
    for l in src.lines() {
        let t = l.trim();
        if let Some(rest) = t.strip_prefix("import ") {
            let rest = rest.split('#').next().unwrap_or("");
            let parts: Vec<&str> = rest.split(',').collect();
            let mut ok = true;
            let mut names = Vec::new();
            for p in &parts {
                let w: Vec<&str> = p.split_whitespace().collect();
                let good =
                    (w.len() == 1 || (w.len() == 3 && w[1] == "as")) && w[0].split('.').all(ident);
                if !good {
                    ok = false;
                    break;
                }
                names.push(w[0].split('.').next().unwrap().to_string());
            }
            if ok {
                out.extend(names);
            }
        } else if let Some(rest) = t.strip_prefix("from ") {
            if let Some((m, _)) = rest.split_once(" import ") {
                let m = m.trim();
                if !m.starts_with('.') && m.split('.').all(ident) {
                    out.insert(m.split('.').next().unwrap().to_string());
                }
            }
        }
    }
    out
}

fn local_module(repo: &Path, script_dir: &Path, name: &str) -> bool {
    fn walk(d: &Path, name: &str, depth: usize) -> bool {
        if depth > 3 {
            return false;
        }
        if d.join(format!("{}.py", name)).is_file() || d.join(name).is_dir() {
            return true;
        }
        if let Ok(rd) = fs::read_dir(d) {
            for e in rd.flatten() {
                let p = e.path();
                if p.is_dir()
                    && !p
                        .file_name()
                        .map(|n| n.to_string_lossy().starts_with('.'))
                        .unwrap_or(false)
                    && walk(&p, name, depth + 1)
                {
                    return true;
                }
            }
        }
        false
    }
    repo.join(format!("{}.py", name)).is_file()
        || repo.join(name).join("__init__.py").is_file()
        || repo.join("tools").join(format!("{}.py", name)).is_file()
        || walk(script_dir, name, 0)
}

// --------------------------------------------------------- classification

fn scope_of(id: &str, area: &Option<String>, ecc: &[String]) -> &'static str {
    if NAMED.contains(&id) {
        return "named";
    }
    match area {
        Some(a) if ECDLP_CLASS.contains(&a.as_str()) => "ecdlp",
        Some(a) if ecc.iter().any(|x| x == a) => "other_ecc",
        _ => "non_ecc",
    }
}

fn first_num(v: Option<&J>) -> Option<f64> {
    v.and_then(|x| x.as_f64())
}

// Gate G6: the plan is valid. Returns the parsed plan and its trials.
fn read_plan(w: &mut World, id: &str, spec_blob: &[u8]) -> Result<(J, Vec<TrialRes>), String> {
    let path = format!("experiments/{}/trial-plan.json", id);
    let bytes = w.blobs.get(&path).ok_or("unreadable_json")?;
    let plan =
        json_parse(&String::from_utf8_lossy(&bytes)).map_err(|_| "unreadable_json".to_string())?;
    if plan.get("schema").and_then(|x| x.as_str()) != Some("crypto.autoresearch.trial_plan.v1") {
        return Err("schema".into());
    }
    if plan.get("frozen") != Some(&J::Bool(true)) {
        return Err("plan_not_frozen".into());
    }
    for f in [
        "experiment_id",
        "task_id",
        "approved_by",
        "specification",
        "queue",
    ] {
        if plan
            .get(f)
            .and_then(|x| x.as_str())
            .map(|s| s.trim().is_empty())
            .unwrap_or(true)
        {
            return Err(format!("missing_field:{}", f));
        }
    }
    if plan.get("experiment_id").and_then(|x| x.as_str()) != Some(id) {
        return Err("experiment_id_mismatch".into());
    }
    let spec_rel = format!("experiments/{}/specification.yaml", id);
    if plan.get("specification").and_then(|x| x.as_str()) != Some(spec_rel.as_str()) {
        return Err("specification_path".into());
    }
    if plan.get("specification_sha256").and_then(|x| x.as_str()) != Some(sha256(spec_blob).as_str())
    {
        return Err("spec_sha256_mismatch".into());
    }
    let sources = match plan.get("source_sha256") {
        Some(J::Obj(o)) if !o.is_empty() => o.clone(),
        _ => return Err("no_sources".into()),
    };
    for (p, d) in &sources {
        let want = d.as_str().unwrap_or("");
        let blob = w
            .blobs
            .get(p)
            .ok_or_else(|| format!("source_missing:{}", p))?;
        if sha256(&blob) != want {
            return Err(format!("source_hash:{}", p));
        }
        match fs::read(w.repo.join(p)) {
            Ok(b) if sha256(&b) == want => {}
            Ok(_) => return Err(format!("source_modified:{}", p)),
            Err(_) => return Err(format!("source_missing:{}", p)),
        }
    }
    let trials = match plan.get("trials") {
        Some(J::Arr(a)) if !a.is_empty() => a.clone(),
        _ => return Err("no_trials".into()),
    };
    let mut seen_t: HashSet<String> = HashSet::new();
    let mut seen_r: HashSet<String> = HashSet::new();
    let mut out = Vec::new();
    for t in &trials {
        let tid = t
            .get("id")
            .and_then(|x| x.as_str())
            .unwrap_or("")
            .to_string();
        if tid.trim().is_empty() || !seen_t.insert(tid.clone()) {
            return Err("trial_id".into());
        }
        let rid = t
            .get("run_id")
            .and_then(|x| x.as_str())
            .unwrap_or("")
            .to_string();
        let ok_rid = rid.starts_with("RUN-") && {
            let parts: Vec<&str> = rid[4..].rsplitn(2, '-').collect();
            parts.len() == 2
                && !parts[1].is_empty()
                && parts[1].chars().all(|c| c.is_ascii_alphanumeric())
                && parts[0].len() == 6
                && parts[0]
                    .chars()
                    .all(|c| c.is_ascii_hexdigit() && !c.is_ascii_uppercase())
        };
        if !ok_rid || !seen_r.insert(rid.clone()) {
            return Err(format!("run_id:{}", tid));
        }
        let mut argvs = Vec::new();
        for f in ["argv", "check_argv"] {
            let a = t.get(f).and_then(|x| x.str_list());
            match a {
                Some(v)
                    if !v.is_empty() && v.iter().all(|s| !s.is_empty() && !s.contains('\0')) =>
                {
                    if !sources.iter().any(|(p, _)| v.iter().any(|x| x == p)) {
                        return Err(format!("{}_unbound:{}", f, tid));
                    }
                    argvs.push(v);
                }
                _ => return Err(format!("{}:{}", f, tid)),
            }
        }
        let artifacts = t
            .get("artifacts")
            .and_then(|x| x.str_list())
            .unwrap_or_default();
        let uniq: HashSet<&String> = artifacts.iter().collect();
        if artifacts.is_empty()
            || uniq.len() != artifacts.len()
            || !artifacts.iter().any(|a| a == "manifest.yaml")
            || !artifacts.iter().any(|a| a == "raw-result.json")
            || artifacts.iter().any(|a| GENERATED.contains(&a.as_str()))
        {
            return Err(format!("artifacts:{}", tid));
        }
        let mem = first_num(t.get("memory_mb")).unwrap_or(0.0);
        if mem <= 0.0 {
            return Err(format!("memory:{}", tid));
        }
        let wd = first_num(t.get("watchdog_seconds"));
        if let Some(x) = wd {
            if x <= 0.0 {
                return Err(format!("watchdog:{}", tid));
            }
        }
        let deps = t
            .get("depends_on")
            .map(|x| x.str_list().unwrap_or_default())
            .unwrap_or_default();
        let earlier: HashSet<String> = out.iter().map(|r: &TrialRes| r.id.clone()).collect();
        if !deps.iter().all(|d| earlier.contains(d)) {
            return Err(format!("depends_on:{}", tid));
        }
        out.push(TrialRes {
            id: tid,
            run_id: rid,
            memory_mb: mem,
            watchdog: wd,
            runnable: false,
            reasons: vec![],
            argv: argvs[0].clone(),
            check_argv: argvs[1].clone(),
            artifacts,
            depends_on: deps,
        });
    }
    Ok((plan, out))
}

fn num_text(x: f64) -> String {
    if x.fract() == 0.0 {
        format!("{}", x as i64)
    } else {
        format!("{}", x)
    }
}

fn classify_all(w: &mut World) -> Result<Vec<Row>, String> {
    let ids: Vec<String> = w.exp_files.keys().cloned().collect();
    // specs
    let mut specs: BTreeMap<String, Result<Spec, String>> = BTreeMap::new();
    let mut spec_bytes: HashMap<String, Vec<u8>> = HashMap::new();
    for id in &ids {
        if !w.exp_files[id].iter().any(|f| f == "specification.yaml") {
            continue;
        }
        if let Some(b) = w
            .blobs
            .get(&format!("experiments/{}/specification.yaml", id))
        {
            let r = parse_spec(&String::from_utf8_lossy(&b), id);
            specs.insert(id.clone(), r);
            spec_bytes.insert(id.clone(), b);
        }
    }
    let mut superseded: BTreeMap<String, String> = BTreeMap::new();
    for (id, s) in &specs {
        if let Ok(s) = s {
            for t in &s.supersedes {
                superseded.entry(t.clone()).or_insert_with(|| id.clone());
            }
        }
    }
    let mut rows = Vec::new();
    for id in &ids {
        let area = area_of(id);
        let scope = scope_of(id, &area, &w.ecc_areas);
        let mut row = Row {
            id: id.clone(),
            area: area.clone().unwrap_or_default(),
            scope,
            status: String::new(),
            gate: String::new(),
            reason: String::new(),
            outcome: "not_runnable",
            has_plan: w.exp_files[id].iter().any(|f| f == "trial-plan.json"),
            run_state: "none",
            approvals: vec![],
            off_main: w.off_main.get(id).cloned().unwrap_or_default(),
            trials: vec![],
            spec_error: String::new(),
        };
        let spec = match specs.get(id) {
            Some(Ok(s)) => {
                row.status = s.status.clone();
                Some(s.clone())
            }
            Some(Err(e)) => {
                row.spec_error = e.clone();
                row.status = "(unreadable)".into();
                None
            }
            None => {
                row.status = "(no specification)".into();
                None
            }
        };
        let tracked_runs = w.exp_files[id].iter().any(|f| f.starts_with("runs/RUN-"));
        let disk_runs = fs::read_dir(w.repo.join("experiments").join(id).join("runs"))
            .map(|rd| {
                rd.flatten()
                    .any(|e| e.file_name().to_string_lossy().starts_with("RUN-"))
            })
            .unwrap_or(false);
        row.run_state = if tracked_runs || disk_runs {
            "has_runs"
        } else if w.off_main.contains_key(id) {
            "run_elsewhere"
        } else {
            "none"
        };
        if scope == "non_ecc" {
            rows.push(row);
            continue;
        }
        let fail = |row: &mut Row, gate: &str, reason: String| {
            row.gate = gate.to_string();
            row.reason = reason;
        };
        // G1
        let g1 = match (&spec, specs.get(id)) {
            (Some(s), _) => {
                if s.status != "approved" && s.status != "frozen_awaiting_execution" {
                    Some(format!(
                        "not_frozen:status:{}",
                        if s.status.is_empty() {
                            "(none)"
                        } else {
                            &s.status
                        }
                    ))
                } else if s.approved_by.trim().is_empty() {
                    Some("not_frozen:no_approved_by".to_string())
                } else if s.exec_auth_false {
                    Some("not_frozen:execution_not_authorized".to_string())
                } else if let Some(by) = superseded.get(id) {
                    Some(format!("not_frozen:superseded_by:{}", by))
                } else {
                    None
                }
            }
            (None, Some(Err(e))) => Some(format!("not_frozen:unreadable_specification:{}", e)),
            (None, _) => Some("not_frozen:no_specification".to_string()),
        };
        if let Some(r) = g1 {
            fail(&mut row, "G1", r);
            rows.push(row);
            continue;
        }
        let spec = spec.unwrap();
        // G2
        if row.run_state == "has_runs" {
            fail(&mut row, "G2", "has_runs".into());
            rows.push(row);
            continue;
        }
        if let Some(refs) = w.off_main.get(id) {
            fail(
                &mut row,
                "G2",
                format!(
                    "run_elsewhere:{}",
                    refs.first().cloned().unwrap_or_default()
                ),
            );
            rows.push(row);
            continue;
        }
        // G3
        let appr = w.approvals.get(id).cloned().unwrap_or_default();
        row.approvals = appr.clone();
        let approved = if spec.approved_by.starts_with("DEC-") {
            let tok: String = spec
                .approved_by
                .chars()
                .take_while(|c| c.is_ascii_alphanumeric() || *c == '-')
                .collect();
            appr.iter().any(|d| *d == tok)
        } else {
            !appr.is_empty()
        };
        if !approved {
            fail(&mut row, "G3", "no_committed_approval".into());
            rows.push(row);
            continue;
        }
        // G4
        if let Some(d) = w.withheld.get(id) {
            fail(&mut row, "G4", format!("withheld:{}", d));
            rows.push(row);
            continue;
        }
        // G5
        if !row.has_plan {
            fail(&mut row, "G5", "no_launcher".into());
            rows.push(row);
            continue;
        }
        // G6
        let sb = spec_bytes.get(id).cloned().unwrap_or_default();
        let (plan, mut trials) = match read_plan(w, id, &sb) {
            Ok(x) => x,
            Err(why) => {
                fail(&mut row, "G6", format!("plan_invalid:{}", why));
                rows.push(row);
                continue;
            }
        };
        if spec.id != *id {
            fail(&mut row, "G6", "plan_invalid:spec_id_mismatch".into());
            row.trials = trials;
            rows.push(row);
            continue;
        }
        if !spec.frozen_true {
            fail(&mut row, "G6", "plan_invalid:spec_not_frozen_flag".into());
            row.trials = trials;
            rows.push(row);
            continue;
        }
        // G7
        let plan_rel = format!("experiments/{}/trial-plan.json", id);
        let plan_digest = sha256(&w.blobs.get(&plan_rel).unwrap_or_default());
        let task_id = plan
            .get("task_id")
            .and_then(|x| x.as_str())
            .unwrap_or("")
            .to_string();
        let queue_rel = plan
            .get("queue")
            .and_then(|x| x.as_str())
            .unwrap_or("")
            .to_string();
        let queue = w
            .blobs
            .get(&queue_rel)
            .and_then(|b| json_parse(&String::from_utf8_lossy(&b)).ok());
        let queue = match queue {
            Some(q) => q,
            None => {
                fail(&mut row, "G7", "needs_dispatch_queue:queue_absent".into());
                row.trials = trials;
                rows.push(row);
                continue;
            }
        };
        if queue.get("schema").and_then(|x| x.as_str())
            != Some("crypto.autoresearch.dispatch_queue.v1")
            || queue.get("tasks").and_then(|x| x.as_arr()).is_none()
        {
            fail(&mut row, "G7", "needs_dispatch_queue:queue_schema".into());
            row.trials = trials;
            rows.push(row);
            continue;
        }
        let task = queue
            .get("tasks")
            .and_then(|x| x.as_arr())
            .and_then(|a| {
                a.iter()
                    .find(|t| t.get("id").and_then(|x| x.as_str()) == Some(task_id.as_str()))
            })
            .cloned();
        let task = match task {
            Some(t) => t,
            None => {
                fail(&mut row, "G7", "needs_dispatch_queue:task_missing".into());
                row.trials = trials;
                rows.push(row);
                continue;
            }
        };
        let binding_ok = match task.get("handoff").and_then(|h| h.get("execution")) {
            Some(b) => {
                b.get("mode").and_then(|x| x.as_str()) == Some("experiments")
                    && b.get("kind").and_then(|x| x.as_str()) == Some("run")
                    && b.get("experiment_id").and_then(|x| x.as_str()) == Some(id.as_str())
                    && b.get("trial_plan").and_then(|x| x.as_str()) == Some(plan_rel.as_str())
                    && b.get("trial_plan_sha256").and_then(|x| x.as_str())
                        == Some(plan_digest.as_str())
                    && b.get("approved_by").and_then(|x| x.as_str())
                        == plan.get("approved_by").and_then(|x| x.as_str())
            }
            None => false,
        };
        if !binding_ok {
            fail(
                &mut row,
                "G7",
                "needs_dispatch_queue:binding_mismatch".into(),
            );
            row.trials = trials;
            rows.push(row);
            continue;
        }
        // G8
        let budget = task.get("handoff").and_then(|h| h.get("budget"));
        for key in ["maximum_runs", "experiment_maximum_runs"] {
            if first_num(budget.and_then(|b| b.get(key))) == Some(0.0) {
                fail(&mut row, "G8", format!("handoff_budget:{}_zero", key));
                break;
            }
        }
        if row.gate.is_empty() {
            let paths: HashSet<String> = task
                .get("artifact_paths")
                .and_then(|x| x.str_list())
                .unwrap_or_default()
                .into_iter()
                .collect();
            let spec_dir = format!("experiments/{}", id);
            let mut missing = 0usize;
            for t in &trials {
                for name in GENERATED
                    .iter()
                    .map(|s| s.to_string())
                    .chain(t.artifacts.iter().cloned())
                {
                    if !paths.contains(&format!("{}/runs/{}/{}", spec_dir, t.run_id, name)) {
                        missing += 1;
                    }
                }
            }
            if missing > 0 {
                fail(
                    &mut row,
                    "G8",
                    format!("handoff_archive_coverage:{}_files_missing", missing),
                );
            }
        }
        if row.gate.is_empty() {
            if let Some(gb) = first_num(budget.and_then(|b| b.get("memory_gb"))) {
                if let Some(t) = trials.iter().find(|t| t.memory_mb > gb * 1024.0) {
                    fail(
                        &mut row,
                        "G8",
                        format!(
                            "handoff_budget:memory_{}GB<{}MB:{}",
                            num_text(gb),
                            num_text(t.memory_mb),
                            t.id
                        ),
                    );
                }
            }
        }
        if !row.gate.is_empty() {
            row.trials = trials;
            rows.push(row);
            continue;
        }
        // G9, per trial
        let mut programs: Vec<String> = Vec::new();
        if let Some(b) = w.blobs.get(&format!("experiments/{}/runbook.yaml", id)) {
            if let Ok(doc) = yaml_parse(&String::from_utf8_lossy(&b)) {
                if let Some(Y::Seq(p)) = doc.get("environment").and_then(|e| e.get("programs")) {
                    programs = p
                        .iter()
                        .filter_map(|x| x.str())
                        .map(|s| s.to_string())
                        .collect();
                }
            }
        }
        let sources: Vec<String> = match plan.get("source_sha256") {
            Some(J::Obj(o)) => o.iter().map(|(k, _)| k.clone()).collect(),
            _ => vec![],
        };
        let mut missing_modules: Vec<String> = Vec::new();
        for s in sources.iter().filter(|s| s.ends_with(".py")) {
            let src = read_text(&w.repo.join(s)).unwrap_or_default();
            let sdir = w.repo.join(Path::new(s).parent().unwrap_or(Path::new("")));
            for m in py_imports(&src) {
                if m == "__future__" || w.stdlib.contains(&m) || local_module(&w.repo, &sdir, &m) {
                    continue;
                }
                if !w.module_available(&m) && !missing_modules.contains(&m) {
                    missing_modules.push(m);
                }
            }
        }
        let mut done: HashMap<String, bool> = HashMap::new();
        for t in trials.iter_mut() {
            let mut r: Vec<String> = Vec::new();
            if t.memory_mb > MEM_CAP_MB {
                r.push(format!("memory:{}MB>4096MB", num_text(t.memory_mb)));
            }
            match t.watchdog.or(spec.wall) {
                Some(s) if s > TIME_CAP_S => r.push(format!("watchdog:{}s>2700s", num_text(s))),
                Some(_) => {}
                None => r.push("time_unbounded".into()),
            }
            let mut tools: Vec<String> = vec![t.argv[0].clone()];
            tools.extend(programs.iter().cloned());
            tools.sort();
            tools.dedup();
            for p in tools {
                if !which(&p) {
                    r.push(format!("tool_missing:{}", p));
                }
            }
            for m in &missing_modules {
                r.push(format!("module_missing:{}", m));
            }
            for d in &t.depends_on {
                if !done.get(d).copied().unwrap_or(false) {
                    r.push(format!("dependency:{}", d));
                }
            }
            t.runnable = r.is_empty();
            t.reasons = r;
            done.insert(t.id.clone(), t.runnable);
        }
        let n_ok = trials.iter().filter(|t| t.runnable).count();
        row.gate = "G9".into();
        if n_ok == trials.len() {
            row.outcome = "runnable";
            row.gate = String::new();
        } else if n_ok > 0 {
            row.outcome = "partial";
            row.gate = String::new();
            if let Some(t) = trials.iter().find(|t| !t.runnable) {
                row.reason = format!("{}:{}", t.id, t.reasons[0]);
            }
        } else {
            row.reason = trials[0].reasons[0].clone();
        }
        row.trials = trials;
        rows.push(row);
    }
    Ok(rows)
}

// ------------------------------------------------------------------- output

fn row_json(r: &Row) -> J {
    jobj(vec![
        ("id", js(&r.id)),
        ("area", js(&r.area)),
        ("scope", js(r.scope)),
        ("status", js(&r.status)),
        ("outcome", js(r.outcome)),
        ("gate", js(&r.gate)),
        ("reason", js(&r.reason)),
        ("has_plan", J::Bool(r.has_plan)),
        ("run_state", js(r.run_state)),
        ("trials", jn(r.trials.len())),
        (
            "trials_runnable",
            jn(r.trials.iter().filter(|t| t.runnable).count()),
        ),
        ("approvals", jstrs(&r.approvals)),
        ("off_main", jstrs(&r.off_main)),
        ("spec_error", js(&r.spec_error)),
    ])
}

fn trial_json(r: &Row, t: &TrialRes) -> J {
    let mut reasons = Vec::new();
    if !r.reason.is_empty() && r.gate != "G9" && r.outcome != "runnable" && r.outcome != "partial" {
        reasons.push(r.reason.clone());
    }
    reasons.extend(t.reasons.iter().cloned());
    jobj(vec![
        ("experiment_id", js(&r.id)),
        ("scope", js(r.scope)),
        ("trial_id", js(&t.id)),
        ("run_id", js(&t.run_id)),
        ("memory_mb", J::Num(t.memory_mb)),
        (
            "watchdog_seconds",
            t.watchdog.map(J::Num).unwrap_or(J::Null),
        ),
        ("runnable", J::Bool(t.runnable)),
        ("reasons", jstrs(&reasons)),
        ("argv", jstrs(&t.argv)),
        ("depends_on", jstrs(&t.depends_on)),
    ])
}

fn reason_class(reason: &str) -> String {
    // the reason with its variable tail removed, for counting
    let head = reason.split(':').next().unwrap_or(reason);
    match head {
        "not_frozen" => reason.splitn(3, ':').take(2).collect::<Vec<_>>().join(":"),
        "withheld" | "run_elsewhere" | "plan_invalid" | "needs_dispatch_queue" => head.to_string(),
        "handoff_archive_coverage" => head.to_string(),
        _ => head.to_string(),
    }
}

fn counts_json(m: &BTreeMap<String, usize>) -> J {
    J::Obj(m.iter().map(|(k, v)| (k.clone(), jn(*v))).collect())
}

struct Anchor {
    id: &'static str,
    want: &'static str, // outcome:reason-prefix
}

fn anchors(rows: &[Row]) -> (J, bool) {
    let list = [
        Anchor {
            id: "EXP-XEDN-0c0182",
            want: "runnable",
        },
        Anchor {
            id: "EXP-ECDLP-f34097",
            want: "handoff_archive_coverage",
        },
        Anchor {
            id: "EXP-SEMBIN-d9767f",
            want: "memory:6144MB>4096MB",
        },
        Anchor {
            id: "EXP-IC-002",
            want: "no_launcher",
        },
        Anchor {
            id: "EXP-ECDLP-daee4d",
            want: "needs_dispatch_queue",
        },
        Anchor {
            id: "EXP-PMA-001",
            want: "has_runs",
        },
    ];
    let mut all = true;
    let mut out = Vec::new();
    for a in &list {
        let r = rows.iter().find(|r| r.id == a.id);
        let (got, ok) = match r {
            None => ("(absent)".to_string(), false),
            Some(r) => {
                let got = if r.outcome == "runnable" {
                    "runnable".to_string()
                } else {
                    r.reason.clone()
                };
                let mut ok = got.starts_with(a.want);
                if a.id == "EXP-XEDN-0c0182" {
                    ok = ok && r.trials.len() == 2 && r.trials.iter().all(|t| t.runnable);
                }
                if a.id == "EXP-SEMBIN-d9767f" {
                    ok = r.outcome == "not_runnable"
                        && !r.trials.is_empty()
                        && r.trials.iter().all(|t| {
                            t.reasons.iter().any(|x| x == "memory:6144MB>4096MB")
                                && t.reasons.iter().any(|x| x.starts_with("watchdog:"))
                        });
                }
                (got, ok)
            }
        };
        all &= ok;
        out.push(jobj(vec![
            ("id", js(a.id)),
            ("want", js(a.want)),
            ("got", js(&got)),
            ("ok", J::Bool(ok)),
        ]));
    }
    (J::Arr(out), all)
}

fn scan(repo: &Path, out: &Path) -> Result<(), String> {
    let t0 = std::time::Instant::now();
    let mut w = World::load(repo)?;
    let t_load = t0.elapsed().as_millis();
    let rows = classify_all(&mut w)?;
    let t_classify = t0.elapsed().as_millis() - t_load;
    eprintln!("scan: load {} ms, classify {} ms", t_load, t_classify);
    // contracts.jsonl and trials.jsonl
    let mut cj = String::new();
    let mut tj = String::new();
    for r in rows.iter().filter(|r| r.scope != "non_ecc") {
        cj.push_str(&row_json(r).to_string());
        cj.push('\n');
        for t in &r.trials {
            tj.push_str(&trial_json(r, t).to_string());
            tj.push('\n');
        }
    }
    write_file(&out.join("contracts.jsonl"), &cj)?;
    write_file(&out.join("trials.jsonl"), &tj)?;
    // summary
    let mut by_scope: BTreeMap<String, usize> = BTreeMap::new();
    let mut by_status: BTreeMap<String, usize> = BTreeMap::new();
    let mut by_area_nonecc: BTreeMap<String, usize> = BTreeMap::new();
    let mut by_area_other: BTreeMap<String, usize> = BTreeMap::new();
    let mut reasons_ecdlp: BTreeMap<String, usize> = BTreeMap::new();
    let mut outcomes_ecdlp: BTreeMap<String, usize> = BTreeMap::new();
    let mut zero_run = 0usize;
    let mut approved_zero_run_ecc = 0usize;
    let mut with_plan_ecdlp = 0usize;
    let mut ready_ecdlp = 0usize;
    let mut spec_errors = Vec::new();
    for r in &rows {
        *by_scope.entry(r.scope.to_string()).or_default() += 1;
        *by_status.entry(r.status.clone()).or_default() += 1;
        if !r.spec_error.is_empty() {
            spec_errors.push(format!("{}: {}", r.id, r.spec_error));
        }
        let has_runs = r.run_state != "none";
        match r.scope {
            "non_ecc" => *by_area_nonecc.entry(r.area.clone()).or_default() += 1,
            "other_ecc" => *by_area_other.entry(r.area.clone()).or_default() += 1,
            _ => {}
        }
        if !has_runs {
            zero_run += 1;
        }
        if !has_runs && r.status == "approved" && matches!(r.scope, "ecdlp" | "other_ecc") {
            approved_zero_run_ecc += 1;
        }
        if matches!(r.scope, "ecdlp" | "named") && !has_runs {
            if r.has_plan {
                with_plan_ecdlp += 1;
            }
            if r.gate.is_empty() || r.gate == "G8" || r.gate == "G9" {
                ready_ecdlp += 1;
            }
        }
        if matches!(r.scope, "ecdlp" | "named") {
            *outcomes_ecdlp.entry(r.outcome.to_string()).or_default() += 1;
            let k = if r.outcome == "runnable" {
                "runnable".to_string()
            } else if r.outcome == "partial" {
                "partial".to_string()
            } else {
                reason_class(&r.reason)
            };
            *reasons_ecdlp.entry(k).or_default() += 1;
        }
    }
    let (anch, anch_ok) = anchors(&rows);
    let class_missing: Vec<String> = ECDLP_CLASS
        .iter()
        .filter(|a| !w.ecc_areas.iter().any(|x| x == *a))
        .map(|s| s.to_string())
        .collect();
    let runnable: Vec<J> = rows
        .iter()
        .filter(|r| {
            matches!(r.scope, "ecdlp" | "named")
                && (r.outcome == "runnable" || r.outcome == "partial")
        })
        .map(|r| {
            jobj(vec![
                ("id", js(&r.id)),
                ("outcome", js(r.outcome)),
                (
                    "trials",
                    J::Arr(
                        r.trials
                            .iter()
                            .filter(|t| t.runnable)
                            .map(|t| js(&t.id))
                            .collect(),
                    ),
                ),
            ])
        })
        .collect();
    let summary = jobj(vec![
        ("schema", js("blindspots18.scan.v1")),
        ("head", js(&w.head)),
        ("contract_dirs_at_head", jn(rows.len())),
        ("contracts_without_run", jn(zero_run)),
        ("approved_zero_run_in_ecc_areas", jn(approved_zero_run_ecc)),
        ("ecdlp_or_named_without_run_with_plan", jn(with_plan_ecdlp)),
        ("ecdlp_or_named_past_g7", jn(ready_ecdlp)),
        ("by_scope", counts_json(&by_scope)),
        ("by_spec_status", counts_json(&by_status)),
        ("non_ecc_by_area", counts_json(&by_area_nonecc)),
        ("other_ecc_by_area", counts_json(&by_area_other)),
        ("ecdlp_and_named_by_outcome", counts_json(&outcomes_ecdlp)),
        ("ecdlp_and_named_by_reason", counts_json(&reasons_ecdlp)),
        ("runnable_contracts", J::Arr(runnable)),
        ("anchors", anch),
        ("anchors_ok", J::Bool(anch_ok)),
        ("class_not_in_ecc_areas", jstrs(&class_missing)),
        ("ecc_areas_read", jn(w.ecc_areas.len())),
        ("decision_files", jn(w.dec_files.len())),
        ("decisions_parsed", jn(w.decisions_parsed)),
        ("decision_parse_failures", jstrs(&w.decision_parse_failures)),
        ("spec_parse_failures", jstrs(&spec_errors)),
        ("withheld_ids", jn(w.withheld.len())),
        ("probe_off_main", js(&w.off_main_probe)),
        ("probe_python_stdlib", js(&w.stdlib_probe)),
    ]);
    write_file(&out.join("summary.json"), &(summary.to_string() + "\n"))?;
    // table.md (pre-execution form)
    let mut t = String::new();
    t.push_str(
        "| contract | scope | runnable | run id | exit | reason |\n|---|---|---|---|---|---|\n",
    );
    for r in rows.iter().filter(|r| matches!(r.scope, "ecdlp" | "named")) {
        if r.trials.is_empty() {
            let _ = writeln!(t, "| {} | {} | no | - | - | {} |", r.id, r.scope, r.reason);
        } else {
            for tr in &r.trials {
                let why = if tr.runnable {
                    String::new()
                } else if r.gate == "G9" || r.outcome == "partial" || r.outcome == "runnable" {
                    tr.reasons.join("; ")
                } else {
                    r.reason.clone()
                };
                let _ = writeln!(
                    t,
                    "| {} | {} | {} | {} | - | {} |",
                    r.id,
                    r.scope,
                    if tr.runnable { "yes" } else { "no" },
                    tr.run_id,
                    why
                );
            }
        }
    }
    write_file(&out.join("table.md"), &t)?;
    println!(
        "scan: head {} contracts {} ecdlp/named {} runnable_contracts {} anchors_ok {}",
        &w.head[..12.min(w.head.len())],
        rows.len(),
        rows.iter()
            .filter(|r| matches!(r.scope, "ecdlp" | "named"))
            .count(),
        rows.iter()
            .filter(|r| matches!(r.scope, "ecdlp" | "named")
                && (r.outcome == "runnable" || r.outcome == "partial"))
            .count(),
        anch_ok
    );
    Ok(())
}

// -------------------------------------------------------------------- cards

fn yq(s: &str) -> String {
    let lower = s.to_ascii_lowercase();
    let reserved = [
        "true", "false", "null", "yes", "no", "on", "off", "y", "n", "~",
    ];
    if s.parse::<f64>().is_ok()
        || s.chars()
            .next()
            .map(|c| c.is_ascii_digit() || c == '.')
            .unwrap_or(false)
        || reserved.contains(&lower.as_str())
    {
        return format!("\"{}\"", s);
    }
    // YAML flow-safe scalar: quote when it has characters that could confuse a flow sequence
    if s.chars()
        .all(|c| c.is_ascii_alphanumeric() || "/._-=+@%".contains(c))
        && !s.is_empty()
        && !s.starts_with('-')
    {
        s.to_string()
    } else if s.starts_with("--")
        && s.chars()
            .all(|c| c.is_ascii_alphanumeric() || "/._-=+@%".contains(c))
    {
        s.to_string()
    } else {
        format!("\"{}\"", s.replace('\\', "\\\\").replace('"', "\\\""))
    }
}

fn argv_yaml(v: &[String]) -> String {
    format!(
        "[{}]",
        v.iter().map(|s| yq(s)).collect::<Vec<_>>().join(", ")
    )
}

struct Card {
    name: String,
    text: String,
    worst_seconds: u64,
    experiment: String,
    trial: String,
}

fn make_card(
    repo: &Path,
    number: usize,
    r: &Row,
    t: &TrialRes,
    spec_wall: Option<f64>,
) -> Result<Card, String> {
    let nn = format!("{:02}", number);
    let rundir = format!("{}/raw/runs/{}", OUT_DIR_REL, t.run_id);
    let sub = |v: &[String]| -> Vec<String> {
        v.iter().map(|a| a.replace("{run_dir}", &rundir)).collect()
    };
    let run_argv = sub(&t.argv);
    let check_argv = sub(&t.check_argv);
    // replica fidelity: undoing the substitution must give the plan's argv back
    let back: Vec<String> = run_argv
        .iter()
        .map(|a| {
            if *a == rundir {
                "{run_dir}".to_string()
            } else {
                a.clone()
            }
        })
        .collect();
    if back != t.argv {
        return Err(format!(
            "{}: substitution changed the argv beyond {{run_dir}}",
            t.id
        ));
    }
    let bytes = (t.memory_mb * 1024.0 * 1024.0) as u64;
    let bound = t.watchdog.or(spec_wall).unwrap_or(CARD_CMD_CAP_S as f64);
    let cap = if bound > CARD_CMD_CAP_S as f64 {
        CARD_CMD_CAP_S
    } else {
        bound as u64
    };
    let mut binds: Vec<(String, String)> = Vec::new();
    for a in run_argv.iter().chain(check_argv.iter()) {
        let p = repo.join(a);
        if p.is_file() && !binds.iter().any(|(q, _)| q == a) {
            let b = fs::read(&p).map_err(|e| format!("{}: {}", a, e))?;
            binds.push((a.clone(), sha256(&b)));
        }
    }
    let envline = "{PYTHONHASHSEED: \"0\", PYTHONDONTWRITEBYTECODE: \"1\", OMP_NUM_THREADS: \"1\", RAYON_NUM_THREADS: \"1\", OPENBLAS_NUM_THREADS: \"1\", MKL_NUM_THREADS: \"1\"}";
    let mut s = String::new();
    let _ = writeln!(s, "schema: crypto.autoresearch.mechanical-task-card.v1");
    let _ = writeln!(s, "card_id: CARD-BLINDSPOT-18-{}", nn);
    let _ = writeln!(s, "experiment_id: BLINDSPOT-18");
    let _ = writeln!(s, "author_role: experiment-director");
    let _ = writeln!(s, "executor_role: executor-mechanical");
    let _ = writeln!(s, "kind: frozen_command");
    let _ = writeln!(s);
    let _ = writeln!(s, "receipt: {}/raw/receipt-card-{}.json", OUT_DIR_REL, nn);
    let _ = writeln!(s, "binds:");
    for (p, d) in &binds {
        let _ = writeln!(s, "  - {{path: {}, sha256: {}}}", p, d);
    }
    let _ = writeln!(s, "commands:");
    let _ = writeln!(s, "  - id: make-run-dir");
    let _ = writeln!(s, "    argv: [mkdir, -p, {}]", rundir);
    let _ = writeln!(s, "    timeout_seconds: 5");
    let _ = writeln!(s, "    success_exit_codes: [0]");
    let _ = writeln!(s, "  - id: run-{}", t.id);
    let mut full = vec!["prlimit".to_string(), format!("--as={}", bytes)];
    full.extend(run_argv.iter().cloned());
    let _ = writeln!(s, "    argv: {}", argv_yaml(&full));
    let _ = writeln!(s, "    timeout_seconds: {}", cap);
    let _ = writeln!(s, "    success_exit_codes: [0]");
    let _ = writeln!(s, "    env: {}", envline);
    let _ = writeln!(s, "    stdout: {}/stdout.log", rundir);
    let _ = writeln!(s, "    stderr: {}/stderr.log", rundir);
    let outs: Vec<String> = t
        .artifacts
        .iter()
        .map(|a| format!("{}/{}", rundir, a))
        .collect();
    let _ = writeln!(s, "    outputs: [{}]", outs.join(", "));
    let _ = writeln!(s, "  - id: check-{}", t.id);
    let mut fullc = vec!["prlimit".to_string(), format!("--as={}", bytes)];
    fullc.extend(check_argv.iter().cloned());
    let _ = writeln!(s, "    argv: {}", argv_yaml(&fullc));
    let _ = writeln!(s, "    timeout_seconds: {}", cap);
    let _ = writeln!(s, "    success_exit_codes: [0, 1]");
    let _ = writeln!(s, "    env: {}", envline);
    let _ = writeln!(s, "    stdout: {}/check.stdout.log", rundir);
    let _ = writeln!(s, "    stderr: {}/check.stderr.log", rundir);
    let _ = writeln!(s);
    let _ = writeln!(s, "bus_address: executor-mechanical-blindspot-18");
    let _ = writeln!(s, "background: false");
    let _ = writeln!(s, "write_scope:");
    let _ = writeln!(s, "  - {}/raw/", OUT_DIR_REL);
    let _ = writeln!(s, "stop_when:");
    let _ = writeln!(s, "  - The tool exits with status 2.");
    let _ = writeln!(
        s,
        "  - The status line in the printed summary does not read status completed."
    );
    let _ = writeln!(
        s,
        "  - Any command line in the printed summary ends with FAILED."
    );
    let _ = writeln!(
        s,
        "  - Any output line in the printed summary ends with MISSING."
    );
    let _ = writeln!(s, "notes: \"The repository root is /home/user/crypto-autoresearcher. Run the command through the Bash tool with timeout 600000.\"");
    Ok(Card {
        name: format!("card-{}.yaml", nn),
        text: s,
        worst_seconds: 5 + 2 * cap,
        experiment: r.id.clone(),
        trial: t.id.clone(),
    })
}

fn emit_cards(repo: &Path, out: &Path) -> Result<Vec<Card>, String> {
    let mut w = World::load(repo)?;
    let rows = classify_all(&mut w)?;
    let mut cards = Vec::new();
    let mut n = 2;
    // spec wall clock for time bounds
    for r in rows.iter().filter(|r| {
        matches!(r.scope, "ecdlp" | "named") && (r.outcome == "runnable" || r.outcome == "partial")
    }) {
        let wall = w
            .blobs
            .get(&format!("experiments/{}/specification.yaml", r.id))
            .and_then(|b| parse_spec(&String::from_utf8_lossy(&b), &r.id).ok())
            .and_then(|s| s.wall);
        for t in r.trials.iter().filter(|t| t.runnable) {
            cards.push(make_card(repo, n, r, t, wall)?);
            n += 1;
        }
    }
    for c in &cards {
        write_file(&out.join(&c.name), &c.text)?;
        println!(
            "emit-cards: {} {} {} worst-case {} s",
            c.name, c.experiment, c.trial, c.worst_seconds
        );
    }
    println!("emit-cards: {} card(s)", cards.len());
    Ok(cards)
}

// -------------------------------------------------------------------- table

fn table(scan_dir: &Path, receipts: &Path, out: &Path) -> Result<(), String> {
    // trial id -> (run exit, check exit, status)
    let mut results: HashMap<String, (String, String)> = HashMap::new();
    let mut files: Vec<PathBuf> = fs::read_dir(receipts)
        .map_err(|e| format!("{}: {}", receipts.display(), e))?
        .flatten()
        .map(|e| e.path())
        .filter(|p| {
            p.file_name()
                .map(|n| n.to_string_lossy().starts_with("receipt-card-"))
                .unwrap_or(false)
        })
        .collect();
    files.sort();
    for f in files {
        let j = json_parse(&read_text(&f).unwrap_or_default())
            .map_err(|e| format!("{}: {}", f.display(), e))?;
        if let Some(J::Arr(cmds)) = j.get("commands") {
            for c in cmds {
                let id = c.get("id").and_then(|x| x.as_str()).unwrap_or("");
                let exit = if c.get("timed_out") == Some(&J::Bool(true)) {
                    "timed out".to_string()
                } else {
                    c.get("exit_code")
                        .and_then(|x| x.as_f64())
                        .map(|x| format!("{}", x as i64))
                        .unwrap_or_else(|| "none".into())
                };
                if let Some(t) = id.strip_prefix("run-") {
                    results.entry(t.to_string()).or_default().0 = exit;
                } else if let Some(t) = id.strip_prefix("check-") {
                    results.entry(t.to_string()).or_default().1 = exit;
                }
            }
        }
    }
    let mut t = String::new();
    t.push_str("| contract | scope | runnable | run id | exit (run / check) | reason |\n|---|---|---|---|---|---|\n");
    let contracts = read_text(&scan_dir.join("contracts.jsonl")).ok_or("contracts.jsonl")?;
    let trials = read_text(&scan_dir.join("trials.jsonl")).ok_or("trials.jsonl")?;
    let mut by_c: HashMap<String, Vec<J>> = HashMap::new();
    for l in trials.lines() {
        let j = json_parse(l)?;
        if let Some(e) = j.get("experiment_id").and_then(|x| x.as_str()) {
            by_c.entry(e.to_string()).or_default().push(j.clone());
        }
    }
    for l in contracts.lines() {
        let c = json_parse(l)?;
        let scope = c.get("scope").and_then(|x| x.as_str()).unwrap_or("");
        if scope != "ecdlp" && scope != "named" {
            continue;
        }
        let id = c.get("id").and_then(|x| x.as_str()).unwrap_or("");
        let reason = c.get("reason").and_then(|x| x.as_str()).unwrap_or("");
        match by_c.get(id) {
            None => {
                let _ = writeln!(t, "| {} | {} | no | - | - | {} |", id, scope, reason);
            }
            Some(ts) => {
                for tr in ts {
                    let tid = tr.get("trial_id").and_then(|x| x.as_str()).unwrap_or("");
                    let run = tr.get("run_id").and_then(|x| x.as_str()).unwrap_or("");
                    let ok = tr.get("runnable") == Some(&J::Bool(true));
                    let (re, ce) = results
                        .get(tid)
                        .cloned()
                        .unwrap_or(("not run".into(), "not run".into()));
                    let why = tr
                        .get("reasons")
                        .and_then(|x| x.str_list())
                        .map(|v| v.join("; "))
                        .unwrap_or_default();
                    let _ = writeln!(
                        t,
                        "| {} | {} | {} | {} | {} / {} | {} |",
                        id,
                        scope,
                        if ok { "yes" } else { "no" },
                        run,
                        if ok { re } else { "-".into() },
                        if ok { ce } else { "-".into() },
                        why
                    );
                }
            }
        }
    }
    write_file(out, &t)?;
    println!("table: written {}", out.display());
    Ok(())
}

// ----------------------------------------------------------------- selftest

struct Ctl {
    lines: Vec<String>,
    failed: usize,
    total: usize,
}

impl Ctl {
    fn check(&mut self, name: &str, expected: &str, got: &str) {
        let pass = expected == got;
        self.total += 1;
        if !pass {
            self.failed += 1;
        }
        self.lines.push(
            jobj(vec![
                ("control", js(name)),
                ("expected", js(expected)),
                ("got", js(got)),
                ("pass", J::Bool(pass)),
            ])
            .to_string(),
        );
    }
}

#[derive(Clone)]
struct Opt {
    status: &'static str,
    flag: bool,
    approved_by: String,
    exec_auth_false: bool,
    supersedes: Option<String>,
    wall: Option<u32>,
    mem: u32,
    watchdog: Option<u32>,
    argv0: &'static str,
    imports: &'static str,
    plan: bool,
    queue: bool,
    binding_ok: bool,
    drop_paths: usize,
    zero_runs: bool,
    spec_hash_bad: bool,
    src_hash_bad: bool,
    approve: u8,                         // 0 none, 1 own decision, 2 a different decision
    second: Option<(u32, &'static str)>, // memory of trial 2, dependency
}

impl Opt {
    fn new(id: &str) -> Opt {
        let _ = id;
        Opt {
            status: "approved",
            flag: true,
            approved_by: String::new(),
            exec_auth_false: false,
            supersedes: None,
            wall: Some(600),
            mem: 256,
            watchdog: Some(60),
            argv0: "python3",
            imports: "import json\nimport argparse\n",
            plan: true,
            queue: true,
            binding_ok: true,
            drop_paths: 0,
            zero_runs: false,
            spec_hash_bad: false,
            src_hash_bad: false,
            approve: 1,
            second: None,
        }
    }
}

fn add_contract(files: &mut BTreeMap<String, String>, id: &str, o: &Opt) {
    let dec = format!("DEC-FX-{}", id.rsplit('-').next().unwrap());
    let approved_by = if !o.approved_by.is_empty() {
        o.approved_by.clone()
    } else if o.approve == 2 {
        format!("{}-wrong", dec)
    } else {
        dec.clone()
    };
    let mut spec = String::new();
    spec.push_str("experiment:\n");
    let _ = writeln!(spec, "  id: {}", id);
    let _ = writeln!(spec, "  status: {}", o.status);
    if o.flag {
        spec.push_str("  frozen: true\n");
    }
    if o.approved_by != "-" {
        let _ = writeln!(spec, "  approved_by: {}", approved_by);
    }
    if o.exec_auth_false {
        spec.push_str("  execution_authorized: false\n");
    }
    if let Some(s) = &o.supersedes {
        let _ = writeln!(spec, "  supersedes: {}", s);
    }
    spec.push_str("  title: 'fixture: a title with a colon'\n");
    if let Some(w) = o.wall {
        let _ = writeln!(spec, "  budget:\n    wall_clock_seconds_per_run: {}", w);
    }
    let base = format!("experiments/{}", id);
    files.insert(format!("{}/specification.yaml", base), spec.clone());
    if o.approve == 1 {
        files.insert(
            format!("ledger/decisions/{}.yaml", dec),
            format!("coordinator_decision:\n  id: {}\n  decided_at: '2026-10-01'\n  decision: approve\n  target_ids:\n    - {}\n", dec, id),
        );
    } else if o.approve == 2 {
        files.insert(
            format!("ledger/decisions/{}-other.yaml", dec),
            format!("coordinator_decision:\n  id: {}-other\n  decided_at: '2026-10-01'\n  decision: approve\n  target_ids:\n    - {}\n", dec, id),
        );
    }
    let run_py = format!("{}\n", o.imports);
    let check_py = "import json\n".to_string();
    let run_rel = format!("{}/implementation/run.py", base);
    let check_rel = format!("{}/implementation/check.py", base);
    files.insert(run_rel.clone(), run_py.clone());
    files.insert(check_rel.clone(), check_py.clone());
    if !o.plan {
        return;
    }
    let spec_sha = if o.spec_hash_bad {
        "0".repeat(64)
    } else {
        sha256(spec.as_bytes())
    };
    let run_sha = if o.src_hash_bad {
        "1".repeat(64)
    } else {
        sha256(run_py.as_bytes())
    };
    let tail = id.rsplit('-').next().unwrap();
    let mk_trial = |tid: &str, rid: String, mem: u32, deps: &[&str]| -> J {
        let mut v = vec![
            (
                "argv",
                J::Arr(vec![
                    js(o.argv0),
                    js(&run_rel),
                    js("--run-dir"),
                    js("{run_dir}"),
                ]),
            ),
            (
                "artifacts",
                J::Arr(vec![js("manifest.yaml"), js("raw-result.json")]),
            ),
            (
                "check_argv",
                J::Arr(vec![js("python3"), js(&check_rel), js("{run_dir}")]),
            ),
            ("depends_on", J::Arr(deps.iter().map(|d| js(d)).collect())),
            ("id", js(tid)),
            ("memory_mb", J::Num(mem as f64)),
            ("run_id", js(&rid)),
        ];
        if let Some(wd) = o.watchdog {
            v.push(("watchdog_seconds", J::Num(wd as f64)));
            v.push(("watchdog_reason", js("fixture machine protection")));
        }
        jobj(v)
    };
    let mut trials = vec![mk_trial(
        "t1",
        format!("RUN-FX-{}", &format!("{:0>6}", tail)[..6]),
        o.mem,
        &[],
    )];
    let mut run_ids = vec![format!("RUN-FX-{}", &format!("{:0>6}", tail)[..6])];
    if let Some((m2, dep)) = o.second {
        let rid = format!("RUN-FX-{}", &format!("{:0>6}", format!("f{}", tail))[..6]);
        run_ids.push(rid.clone());
        let deps: Vec<&str> = if dep.is_empty() { vec![] } else { vec![dep] };
        trials.push(mk_trial("t2", rid, m2, &deps));
    }
    let task = format!("TASK-FX-{}", tail);
    let queue_rel = format!("coordination/q-{}.json", id);
    let plan = jobj(vec![
        ("approved_by", js(&approved_by)),
        ("experiment_id", js(id)),
        ("frozen", J::Bool(true)),
        ("queue", js(&queue_rel)),
        ("schema", js("crypto.autoresearch.trial_plan.v1")),
        (
            "source_sha256",
            jobj(vec![
                (&check_rel, js(&sha256(check_py.as_bytes()))),
                (&run_rel, js(&run_sha)),
            ]),
        ),
        ("specification", js(&format!("{}/specification.yaml", base))),
        ("specification_sha256", js(&spec_sha)),
        ("task_id", js(&task)),
        ("trials", J::Arr(trials)),
    ]);
    let plan_text = plan.to_string() + "\n";
    let plan_rel = format!("{}/trial-plan.json", base);
    let plan_sha = sha256(plan_text.as_bytes());
    files.insert(plan_rel.clone(), plan_text);
    if !o.queue {
        return;
    }
    let mut paths: Vec<String> = Vec::new();
    for rid in &run_ids {
        for g in GENERATED {
            paths.push(format!("{}/runs/{}/{}", base, rid, g));
        }
        paths.push(format!("{}/runs/{}/manifest.yaml", base, rid));
        paths.push(format!("{}/runs/{}/raw-result.json", base, rid));
    }
    for _ in 0..o.drop_paths {
        paths.pop();
    }
    let bound_sha = if o.binding_ok {
        plan_sha
    } else {
        "2".repeat(64)
    };
    let mut budget = vec![("memory_gb", J::Num(8.0))];
    if o.zero_runs {
        budget.push(("maximum_runs", J::Num(0.0)));
    }
    let queue = jobj(vec![
        ("schema", js("crypto.autoresearch.dispatch_queue.v1")),
        (
            "tasks",
            J::Arr(vec![jobj(vec![
                ("id", js(&task)),
                ("artifact_paths", jstrs(&paths)),
                (
                    "handoff",
                    jobj(vec![
                        (
                            "execution",
                            jobj(vec![
                                ("mode", js("experiments")),
                                ("kind", js("run")),
                                ("experiment_id", js(id)),
                                ("trial_plan", js(&plan_rel)),
                                ("trial_plan_sha256", js(&bound_sha)),
                                ("approved_by", js(&approved_by)),
                            ]),
                        ),
                        ("budget", jobj(budget)),
                    ]),
                ),
            ])]),
        ),
    ]);
    files.insert(queue_rel, queue.to_string() + "\n");
}

fn git_ok(dir: &Path, args: &[&str]) -> Result<(), String> {
    let mut a = vec![
        "-c",
        "user.name=fx",
        "-c",
        "user.email=fx@example.invalid",
        "-c",
        "commit.gpgsign=false",
    ];
    a.extend_from_slice(args);
    let (c, _, e) = run_cmd("git", &a, Some(dir))?;
    if c != 0 {
        return Err(format!("git {:?}: {}", args, String::from_utf8_lossy(&e)));
    }
    Ok(())
}

fn selftest(work: &Path, out: Option<&Path>) -> Result<bool, String> {
    let mut ctl = Ctl {
        lines: vec![],
        failed: 0,
        total: 0,
    };
    // --- sha256 vectors (FIPS 180-2) and a file digest against sha256sum
    ctl.check(
        "sha256-empty",
        "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        &sha256(b""),
    );
    ctl.check(
        "sha256-abc",
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
        &sha256(b"abc"),
    );
    ctl.check(
        "sha256-56byte",
        "248d6a61d20638b8e5c026930c3e6039a33ce45964ff2167f6ecedd419db06c1",
        &sha256(b"abcdbcdecdefdefgefghfghighijhijkijkljklmklmnlmnomnopnopq"),
    );
    let million: Vec<u8> = vec![b'a'; 1_000_000];
    ctl.check(
        "sha256-million-a",
        "cdc76e5c9914fb9281a1c7e284d73e67f1809a48a497200e046d39ccc7112cd0",
        &sha256(&million),
    );
    let _ = fs::remove_dir_all(work);
    fs::create_dir_all(work).map_err(|e| e.to_string())?;
    let known = work.join("known.bin");
    let blob: Vec<u8> = (0..5000u32).map(|i| (i * 31 % 251) as u8).collect();
    fs::write(&known, &blob).map_err(|e| e.to_string())?;
    match run_cmd("sha256sum", &[known.to_str().unwrap()], None) {
        Ok((0, o, _)) => {
            let want = String::from_utf8_lossy(&o)
                .split_whitespace()
                .next()
                .unwrap_or("")
                .to_string();
            ctl.check("sha256-file-vs-sha256sum", &want, &sha256(&blob));
        }
        _ => ctl.check(
            "sha256-file-vs-sha256sum",
            "sha256sum available",
            "sha256sum not available",
        ),
    }
    // --- json reader
    let j = json_parse("{\"a\":[1,2.5,\"x\\n\\u0041\"],\"b\":{\"c\":true,\"d\":null}}")
        .map_err(|e| e.to_string())?;
    ctl.check(
        "json-fixture",
        "{\"a\":[1,2.5,\"x\\nA\"],\"b\":{\"c\":true,\"d\":null}}",
        &j.to_string(),
    );
    ctl.check(
        "json-rejects-trailing",
        "err",
        if json_parse("{} x").is_err() {
            "err"
        } else {
            "ok"
        },
    );
    // --- yaml reader
    let ytext = "a: 1\nb:\n  - x\n  - y: 2\n    z: [3, 4]\n  - \"q: r\"\nc: |\n  block\n  text\nd: plain\n  continued # comment\ne:\n- s1\n- s2\nf: {k: v, n: [1, 2]}\ng: 'it''s'\nh:\n  i:\n    j: deep\nl: [a,\n  b]\n# trailing comment\n";
    let y = yaml_parse(ytext)?;
    let pick = |p: Option<&Y>| p.map(|v| v.flat_text()).unwrap_or_else(|| "(none)".into());
    ctl.check("yaml-a", "1", &pick(y.get("a")));
    ctl.check(
        "yaml-seq-map-z1",
        "4",
        &pick(
            y.get("b")
                .and_then(|b| b.seq())
                .and_then(|s| s.get(1))
                .and_then(|m| m.get("z"))
                .and_then(|z| z.seq())
                .and_then(|z| z.get(1)),
        ),
    );
    ctl.check(
        "yaml-quoted-colon",
        "q: r",
        &pick(y.get("b").and_then(|b| b.seq()).and_then(|s| s.get(2))),
    );
    ctl.check("yaml-block-scalar", "block\ntext", &pick(y.get("c")));
    ctl.check("yaml-plain-multiline", "plain continued", &pick(y.get("d")));
    ctl.check("yaml-same-indent-seq", "s1 s2", &pick(y.get("e")));
    ctl.check(
        "yaml-flow-map",
        "1",
        &pick(
            y.get("f")
                .and_then(|f| f.get("n"))
                .and_then(|n| n.seq())
                .and_then(|n| n.get(0)),
        ),
    );
    ctl.check("yaml-single-quote", "it's", &pick(y.get("g")));
    ctl.check(
        "yaml-nested",
        "deep",
        &pick(y.get("h").and_then(|h| h.get("i")).and_then(|i| i.get("j"))),
    );
    ctl.check("yaml-multiline-flow", "a b", &pick(y.get("l")));
    ctl.check(
        "yaml-rejects-bad-indent",
        "err",
        if yaml_parse("a:\n  b: 1\n c: 2\n").is_err() {
            "err"
        } else {
            "ok"
        },
    );
    let y2 = yaml_parse("n: null\nm: ~\nq: 'null'\nk: &id001\n- a\n- b\nf: [it's, fine]\n")?;
    ctl.check(
        "yaml-plain-null-is-null",
        "(null)",
        if matches!(y2.get("n"), Some(Y::Null)) {
            "(null)"
        } else {
            "(not null)"
        },
    );
    ctl.check(
        "yaml-tilde-is-null",
        "(null)",
        if matches!(y2.get("m"), Some(Y::Null)) {
            "(null)"
        } else {
            "(not null)"
        },
    );
    ctl.check("yaml-quoted-null-is-text", "null", &pick(y2.get("q")));
    ctl.check("yaml-anchor-then-seq", "a b", &pick(y2.get("k")));
    ctl.check("yaml-apostrophe-in-flow", "it's fine", &pick(y2.get("f")));
    ctl.check(
        "exp-ids-regex",
        "EXP-ECDLP-0a1b2c EXP-IC-002",
        &exp_ids_in("see EXP-ECDLP-0a1b2c and EXP-IC-002, not EXP-X-12").join(" "),
    );
    ctl.check(
        "py-imports",
        "json os yaml",
        &py_imports(
            "import os, json as j\nfrom yaml import x\nfrom . import y\nimport the foo bar\n",
        )
        .into_iter()
        .collect::<Vec<_>>()
        .join(" "),
    );

    // --- fixture repository
    let repo = work.join("repo");
    fs::create_dir_all(&repo).map_err(|e| e.to_string())?;
    git_ok(&repo, &["init", "-q", "-b", "main"])?;
    let mut files: BTreeMap<String, String> = BTreeMap::new();
    files.insert(
        "orchestration/research-priority.yaml".into(),
        "ecc_areas:\n  - ECDLP   # prime-field\n  - SSI\n  - CSIDH\nexcluded_areas:\n  AEADC: not ecc\n".into(),
    );
    let mut expect: Vec<(String, String)> = Vec::new(); // id -> expected
    let mut case = |files: &mut BTreeMap<String, String>, tail: &str, o: Opt, want: &str| {
        let id = format!("EXP-ECDLP-{}", tail);
        add_contract(files, &id, &o);
        expect.push((id, want.to_string()));
    };
    case(&mut files, "a00001", Opt::new(""), "runnable");
    case(
        &mut files,
        "a00002",
        Opt {
            status: "draft",
            ..Opt::new("")
        },
        "not_frozen:status:draft",
    );
    case(
        &mut files,
        "a00003",
        Opt {
            approved_by: "-".into(),
            ..Opt::new("")
        },
        "not_frozen:no_approved_by",
    );
    case(
        &mut files,
        "a00028",
        Opt {
            approved_by: "null".into(),
            ..Opt::new("")
        },
        "not_frozen:no_approved_by",
    );
    case(
        &mut files,
        "a00004",
        Opt {
            exec_auth_false: true,
            ..Opt::new("")
        },
        "not_frozen:execution_not_authorized",
    );
    case(
        &mut files,
        "a00005",
        Opt::new(""),
        "not_frozen:superseded_by:EXP-ECDLP-a0000b",
    );
    case(
        &mut files,
        "a0000b",
        Opt {
            status: "draft",
            supersedes: Some("EXP-ECDLP-a00005".into()),
            approve: 0,
            plan: false,
            ..Opt::new("")
        },
        "not_frozen:status:draft",
    );
    case(&mut files, "a00006", Opt::new(""), "has_runs");
    files.insert(
        "experiments/EXP-ECDLP-a00006/runs/RUN-FX-aaaaaa/manifest.yaml".into(),
        "x: 1\n".into(),
    );
    case(&mut files, "a00007", Opt::new(""), "has_runs");
    case(
        &mut files,
        "a00008",
        Opt::new(""),
        "run_elsewhere:origin/side",
    );
    case(
        &mut files,
        "a00009",
        Opt {
            approve: 0,
            approved_by: "coordinator".into(),
            ..Opt::new("")
        },
        "no_committed_approval",
    );
    case(
        &mut files,
        "a0000a",
        Opt {
            approve: 2,
            ..Opt::new("")
        },
        "no_committed_approval",
    );
    case(&mut files, "a00010", Opt::new(""), "withheld:DEC-FX-hold");
    case(&mut files, "a00011", Opt::new(""), "runnable");
    case(&mut files, "a00012", Opt::new(""), "runnable");
    files.insert(
        "ledger/decisions/DEC-FX-hold.yaml".into(),
        "coordinator_decision:\n  id: DEC-FX-hold\n  decided_at: '2026-10-05'\n  withheld_contracts:\n    ids:\n      - EXP-ECDLP-a00010\n      - EXP-ECDLP-a00011\n    rule_9_fields:\n      evidence: e\n      budget: b\n      test_boundary: t\n      remaining_uncertainty: r\n      successor_or_revisit: s\n  decision: pause\n".into(),
    );
    files.insert(
        "ledger/decisions/DEC-FX-release.yaml".into(),
        "coordinator_decision:\n  id: DEC-FX-release\n  decided_at: '2026-10-06'\n  decision: pause\n  released_contracts:\n    ids:\n      - EXP-ECDLP-a00011\n".into(),
    );
    files.insert(
        "ledger/decisions/DEC-FX-unguarded.yaml".into(),
        "coordinator_decision:\n  id: DEC-FX-unguarded\n  decided_at: '2026-10-07'\n  decision: pause\n  withheld_contracts:\n    ids:\n      - EXP-ECDLP-a00012\n    rule_9_fields:\n      evidence: e\n".into(),
    );
    case(
        &mut files,
        "a00013",
        Opt {
            plan: false,
            ..Opt::new("")
        },
        "no_launcher",
    );
    case(
        &mut files,
        "a00014",
        Opt {
            spec_hash_bad: true,
            ..Opt::new("")
        },
        "plan_invalid:spec_sha256_mismatch",
    );
    case(
        &mut files,
        "a00015",
        Opt {
            src_hash_bad: true,
            ..Opt::new("")
        },
        "plan_invalid:source_hash:experiments/EXP-ECDLP-a00015/implementation/run.py",
    );
    case(
        &mut files,
        "a00016",
        Opt {
            flag: false,
            ..Opt::new("")
        },
        "plan_invalid:spec_not_frozen_flag",
    );
    case(
        &mut files,
        "a00017",
        Opt {
            queue: false,
            ..Opt::new("")
        },
        "needs_dispatch_queue:queue_absent",
    );
    case(
        &mut files,
        "a00018",
        Opt {
            binding_ok: false,
            ..Opt::new("")
        },
        "needs_dispatch_queue:binding_mismatch",
    );
    case(
        &mut files,
        "a00019",
        Opt {
            drop_paths: 3,
            ..Opt::new("")
        },
        "handoff_archive_coverage:3_files_missing",
    );
    case(
        &mut files,
        "a0001a",
        Opt {
            zero_runs: true,
            ..Opt::new("")
        },
        "handoff_budget:maximum_runs_zero",
    );
    case(
        &mut files,
        "a00020",
        Opt {
            mem: 4096 + 4096,
            ..Opt::new("")
        },
        "memory:8192MB>4096MB",
    );
    case(
        &mut files,
        "a00021",
        Opt {
            watchdog: Some(5000),
            ..Opt::new("")
        },
        "watchdog:5000s>2700s",
    );
    case(
        &mut files,
        "a00022",
        Opt {
            watchdog: None,
            wall: None,
            ..Opt::new("")
        },
        "time_unbounded",
    );
    case(
        &mut files,
        "a00023",
        Opt {
            argv0: "no-such-tool-xyz",
            ..Opt::new("")
        },
        "tool_missing:no-such-tool-xyz",
    );
    case(
        &mut files,
        "a00024",
        Opt {
            imports: "import json\nimport no_such_module_zzz\n",
            ..Opt::new("")
        },
        "module_missing:no_such_module_zzz",
    );
    case(
        &mut files,
        "a00025",
        Opt {
            imports: "import json\nimport helper_mod\n",
            ..Opt::new("")
        },
        "runnable",
    );
    files.insert(
        "experiments/EXP-ECDLP-a00025/implementation/vendor/helper_mod.py".into(),
        "X = 1\n".into(),
    );
    case(
        &mut files,
        "a00026",
        Opt {
            mem: 8192,
            second: Some((256, "t1")),
            ..Opt::new("")
        },
        "memory:8192MB>4096MB",
    );
    case(
        &mut files,
        "a00027",
        Opt {
            second: Some((8192, "t1")),
            ..Opt::new("")
        },
        "partial",
    );
    // scope controls
    add_contract(&mut files, "EXP-SSI-b00001", &Opt::new(""));
    add_contract(&mut files, "EXP-AEADC-c00001", &Opt::new(""));
    for (p, c) in &files {
        write_file(&repo.join(p), c)?;
    }
    git_ok(&repo, &["add", "-A"])?;
    git_ok(&repo, &["commit", "-q", "-m", "fixture main"])?;
    git_ok(&repo, &["update-ref", "refs/remotes/origin/main", "HEAD"])?;
    git_ok(&repo, &["checkout", "-q", "-b", "side"])?;
    write_file(
        &repo.join("experiments/EXP-ECDLP-a00008/runs/RUN-FX-bbbbbb/manifest.yaml"),
        "x: 1\n",
    )?;
    git_ok(&repo, &["add", "-A"])?;
    git_ok(&repo, &["commit", "-q", "-m", "fixture side"])?;
    git_ok(&repo, &["update-ref", "refs/remotes/origin/side", "HEAD"])?;
    git_ok(&repo, &["checkout", "-q", "main"])?;
    // a run directory on disk only
    write_file(
        &repo.join("experiments/EXP-ECDLP-a00007/runs/RUN-FX-cccccc/manifest.yaml"),
        "x: 1\n",
    )?;

    let mut w = World::load(&repo)?;
    let rows = classify_all(&mut w)?;
    for (id, want) in &expect {
        let got = match rows.iter().find(|r| &r.id == id) {
            None => "(no row)".to_string(),
            Some(r) => match r.outcome {
                "runnable" => "runnable".to_string(),
                "partial" => "partial".to_string(),
                _ => r.reason.clone(),
            },
        };
        ctl.check(&format!("gate-{}", id), want, &got);
    }
    let dep = rows
        .iter()
        .find(|r| r.id == "EXP-ECDLP-a00026")
        .and_then(|r| r.trials.get(1))
        .map(|t| t.reasons.join(";"))
        .unwrap_or_default();
    ctl.check("dependency-trial-reason", "dependency:t1", &dep);
    let sc = |id: &str| {
        rows.iter()
            .find(|r| r.id == id)
            .map(|r| format!("{}:{}", r.scope, r.outcome))
            .unwrap_or_else(|| "(no row)".into())
    };
    ctl.check("scope-ecdlp", "ecdlp:runnable", &sc("EXP-ECDLP-a00001"));
    ctl.check(
        "scope-other-ecc",
        "other_ecc:runnable",
        &sc("EXP-SSI-b00001"),
    );
    ctl.check(
        "scope-non-ecc",
        "non_ecc:not_runnable",
        &sc("EXP-AEADC-c00001"),
    );
    ctl.check(
        "decision-parse-failures",
        "0",
        &w.decision_parse_failures.len().to_string(),
    );
    // outputs of scan
    let scan_out = work.join("scan");
    scan(&repo, &scan_out)?;
    let contracts = read_text(&scan_out.join("contracts.jsonl")).unwrap_or_default();
    ctl.check(
        "scan-skips-non-ecc",
        "false",
        &contracts.contains("EXP-AEADC-c00001").to_string(),
    );
    ctl.check(
        "scan-has-other-ecc",
        "true",
        &contracts.contains("EXP-SSI-b00001").to_string(),
    );
    // emitted cards: only ecdlp-scope runnable trials; argv equals the plan's up to {run_dir}
    let cards_out = work.join("cards");
    let cards = emit_cards(&repo, &cards_out)?;
    let want_cards = rows
        .iter()
        .filter(|r| matches!(r.scope, "ecdlp" | "named"))
        .map(|r| r.trials.iter().filter(|t| t.runnable).count())
        .sum::<usize>();
    ctl.check(
        "emit-card-count",
        &want_cards.to_string(),
        &cards.len().to_string(),
    );
    let first = cards.first().map(|c| c.text.clone()).unwrap_or_default();
    let rid = rows
        .iter()
        .find(|r| r.id == "EXP-ECDLP-a00001")
        .and_then(|r| r.trials.first())
        .map(|t| t.run_id.clone())
        .unwrap_or_default();
    let expect_run = format!(
        "argv: [prlimit, --as=268435456, python3, experiments/EXP-ECDLP-a00001/implementation/run.py, --run-dir, {}/raw/runs/{}]",
        OUT_DIR_REL, rid
    );
    ctl.check(
        "emit-card-argv-fidelity",
        "true",
        &first.contains(&expect_run).to_string(),
    );
    ctl.check(
        "emit-card-no-placeholder",
        "false",
        &first.contains("{run_dir}").to_string(),
    );
    ctl.check(
        "emit-card-skips-other-ecc",
        "false",
        &cards
            .iter()
            .any(|c| c.experiment.contains("-SSI-"))
            .to_string(),
    );
    ctl.check(
        "emit-card-worst-case-under-450",
        "true",
        &cards.iter().all(|c| c.worst_seconds < 450).to_string(),
    );
    let _ = fs::remove_dir_all(work);
    let lines = ctl.lines.join("\n") + "\n";
    if let Some(o) = out {
        write_file(o, &lines)?;
    }
    for l in &ctl.lines {
        if l.contains("\"pass\":false") {
            println!("FAILED CONTROL {}", l);
        }
    }
    println!("selftest: {} controls, {} failed", ctl.total, ctl.failed);
    Ok(ctl.failed == 0)
}

fn arg(args: &[String], name: &str) -> Option<String> {
    args.iter()
        .position(|a| a == name)
        .and_then(|i| args.get(i + 1))
        .cloned()
}

fn main() {
    let args: Vec<String> = std::env::args().skip(1).collect();
    let mode = args.first().cloned().unwrap_or_default();
    let res: Result<i32, String> = (|| {
        match mode.as_str() {
        "selftest" => {
            let work = arg(&args, "--work").ok_or("--work DIR required")?;
            let out = arg(&args, "--out");
            Ok(if selftest(Path::new(&work), out.as_deref().map(Path::new))? { 0 } else { 1 })
        }
        "scan" => {
            let repo = arg(&args, "--repo").ok_or("--repo DIR required")?;
            let out = arg(&args, "--out").ok_or("--out DIR required")?;
            scan(Path::new(&repo), Path::new(&out))?;
            Ok(0)
        }
        "emit-cards" => {
            let repo = arg(&args, "--repo").ok_or("--repo DIR required")?;
            let out = arg(&args, "--out").ok_or("--out DIR required")?;
            emit_cards(Path::new(&repo), Path::new(&out))?;
            Ok(0)
        }
        "yaml-dump" => {
            let f = arg(&args, "--file").ok_or("--file FILE required")?;
            let text = read_text(Path::new(&f)).ok_or("unreadable file")?;
            fn to_j(y: &Y) -> J {
                match y {
                    Y::Null => J::Null,
                    Y::Str(s) => J::Str(s.clone()),
                    Y::Seq(v) => J::Arr(v.iter().map(to_j).collect()),
                    Y::Map(v) => J::Obj(v.iter().map(|(k, x)| (k.clone(), to_j(x))).collect()),
                }
            }
            match yaml_parse(&text) {
                Ok(y) => println!("{}", to_j(&y).to_string()),
                Err(e) => println!("{}", jobj(vec![("error", js(&e))]).to_string()),
            }
            Ok(0)
        }
        "yaml-check" => {
            let f = arg(&args, "--file").ok_or("--file FILE required")?;
            let text = read_text(Path::new(&f)).ok_or("unreadable file")?;
            match yaml_parse(&text) {
                Ok(_) => println!("yaml-check: ok"),
                Err(e) => println!("yaml-check: error {}", e),
            }
            Ok(0)
        }
        "table" => {
            let scan_dir = arg(&args, "--scan").ok_or("--scan DIR required")?;
            let rec = arg(&args, "--receipts").ok_or("--receipts DIR required")?;
            let out = arg(&args, "--out").ok_or("--out FILE required")?;
            table(Path::new(&scan_dir), Path::new(&rec), Path::new(&out))?;
            Ok(0)
        }
        _ => Err("usage: selftest --work DIR [--out FILE] | scan --repo DIR --out DIR | emit-cards --repo DIR --out DIR | table --scan DIR --receipts DIR --out FILE".into()),
    }
    })();
    match res {
        Ok(c) => std::process::exit(c),
        Err(e) => {
            eprintln!("error: {}", e);
            std::process::exit(2);
        }
    }
}
