use nfield::ecnf::{CurveNF, Event};
use nfield::field::{big, rat, NumberField};
use num_bigint::{BigInt, BigUint};
use num_traits::Zero;
use serde_json::{json, Value};
use std::collections::HashSet;

pub fn run_input(input: &Value, seed: &str, ladder: &[u64], mut emit: impl FnMut(Value)) -> Value {
    assert!(!ladder.is_empty() && ladder[0] > 0 && ladder.windows(2).all(|x| x[0] < x[1]));
    let g: Vec<BigInt> = input["g"].as_array().unwrap().iter().map(|x| big(x.as_i64().unwrap())).collect();
    assert!(g.len() >= 2 && g.last() == Some(&big(1)));
    let p: BigUint = input["p"].as_str().unwrap().parse().unwrap();
    let root: BigUint = input["root"].as_str().unwrap().parse().unwrap();
    assert!(p > BigUint::from(3u8) && root < p);
    let mut at_root = BigUint::zero();
    for c in g.iter().rev() {
        let value = BigInt::from(at_root) * BigInt::from(root.clone()) + c;
        let pb = BigInt::from(p.clone());
        at_root = ((value % &pb + &pb) % &pb).to_biguint().unwrap();
    }
    assert!(at_root.is_zero(), "reduction root does not satisfy g");
    let a: i64 = input["A"].as_str().unwrap().parse().unwrap();
    let b: i64 = input["B"].as_str().unwrap().parse().unwrap();
    let disc = big(4)*big(a).pow(3) + big(27)*big(b).pow(2);
    assert!(!(&disc % BigInt::from(p.clone())).is_zero(), "bad reduction");
    let aux: Vec<u64> = input["aux_primes"].as_array().unwrap().iter().map(|x| x.as_u64().unwrap()).collect();
    assert!(!aux.is_empty() && aux.iter().all(|&q| q > 4));
    let field = NumberField::new(g);
    let curve = CurveNF::new(&field, rat(a), rat(b), rat(0));
    let mut points = HashSet::new();
    let mut residues = HashSet::new();
    let mut rational = 0u64;
    let mut missing = 0u64;
    let mut rungs = Vec::new();
    let mut last_shell = 0u64;
    let snapshot = |work, shells, phase, points: usize, residues: usize, rational, missing| json!({
        "work":work,"shells_completed":shells,"boundary":phase,
        "points_found_cumulative":points,"distinct_residues":residues,
        "rational_points_seen":rational,"points_without_residue":missing
    });
    curve.iter_search(&aux, *ladder.last().unwrap(), ladder, seed, &[1,2,3,4], &mut |event| {
        match event {
            Event::Checkpoint{tried,shells} => {
                last_shell = shells;
                let row=snapshot(tried,shells,"before_candidate",points.len(),residues.len(),rational,missing);
                emit(json!({"event":"checkpoint","snapshot":row}));
                rungs.push(row);
            },
            Event::Shell{tried,shells} => {
                last_shell=shells;
                emit(json!({"event":"shell","work":tried,"shells_completed":shells}));
            },
            Event::Point{tried,shells,point} => {
                last_shell=shells;
                let point_key=format!("{}|{}",field.elt_to_string(&point.0),field.elt_to_string(&point.1));
                if !points.insert(point_key) { return; }
                let is_rational=field.is_rational(&point.0) && field.is_rational(&point.1);
                let reduced=curve.reduce_point_big(&point,&p,&root);
                if let Some((x,y))=&reduced {
                    residues.insert(format!("{},{}",x,y));
                    if is_rational { rational+=1; }
                } else { missing+=1; }
                let elt=|x:&nfield::Elt| x.iter().map(nfield::field::rat_to_string).collect::<Vec<_>>();
                emit(json!({"event":"point","work":tried,"shells_completed":shells,
                    "x":elt(&point.0),"y":elt(&point.1),"rational":is_rational,
                    "residue":reduced.map(|(x,y)| json!([x.to_string(),y.to_string()]))}));
            }
        }
    });
    let final_row=snapshot(*ladder.last().unwrap(),last_shell,"after_search_end",points.len(),residues.len(),rational,missing);
    emit(json!({"event":"finished","snapshot":final_row}));
    json!({"rungs":rungs,"final":final_row})
}

#[cfg(test)]
mod tests {
    use super::*;
    fn fixture()->Value { json!({"g":[0,1],"p":"101","root":"0","A":"2","B":"3","aux_primes":[1000003]}) }
    #[test]
    fn exact_replay_and_complete_trace() {
        let mut a=Vec::new(); let mut b=Vec::new();
        let x=run_input(&fixture(),"fixture-replay",&[10,30,100],|v|a.push(v));
        let y=run_input(&fixture(),"fixture-replay",&[10,30,100],|v|b.push(v));
        assert_eq!(x,y);assert_eq!(a,b);
        assert_eq!(a.iter().filter(|v| v["event"]=="point").count(),x["final"]["points_found_cumulative"].as_u64().unwrap() as usize);
        assert_eq!(x["rungs"].as_array().unwrap().len(),3);
        assert_eq!(x["rungs"][0]["boundary"],"before_candidate");
        assert_eq!(x["final"]["boundary"],"after_search_end");
    }
    #[test]
    #[should_panic(expected="reduction root")]
    fn rejects_wrong_reduction_root() {let mut v=fixture();v["root"]=json!("1");run_input(&v,"fixture",&[10],|_|{});}
    #[test]
    #[should_panic(expected="bad reduction")]
    fn rejects_bad_reduction() {let mut v=fixture();v["A"]=json!("0");v["B"]=json!("0");run_input(&v,"fixture",&[10],|_|{});}
}
