use nfield::field::{big,is_irreducible_over_q,is_prime_big,NumberField};
use num_bigint::BigInt;
use num_traits::{Signed,Zero};
use serde_json::{json,Value};
use std::fs::{self,OpenOptions};
use std::io::{BufWriter,Write};

fn main() {
    let args:Vec<String>=std::env::args().collect();
    assert!(args.len()==5 && args[1]=="--coefficients" && args[3]=="--out");
    let coefficients:Value=serde_json::from_slice(&fs::read(&args[2]).unwrap()).unwrap();
    let mut out=BufWriter::new(OpenOptions::new().write(true).create_new(true).open(&args[4]).unwrap());
    for (i,row) in coefficients.as_array().unwrap().iter().enumerate() {
        let g:Vec<BigInt>=row["g"].as_array().unwrap().iter().map(|v|big(v.as_i64().unwrap())).collect();
        let disc=NumberField::new(g.clone()).discriminant();
        let screen=if disc.is_zero() {None} else {is_irreducible_over_q(&g)};
        let mut values=Vec::new();
        for k in 4..=12 {
            let t=big(2).pow(k);
            let p=g.iter().rev().fold(BigInt::zero(),|v,c|v*&t+c);
            let eligible=p.is_positive() && p>=big(4096);
            let prime=eligible && is_prime_big(&p.to_biguint().unwrap());
            values.push(json!({"k":k,"p":p.to_string(),"source_prime_screen":prime,"meets_minimum":eligible}));
        }
        serde_json::to_writer(&mut out,&json!({"index":i,"shape":row["shape"],"g":row["g"],"discriminant":disc.to_string(),"source_irreducibility_witness":screen,"values":values})).unwrap();
        out.write_all(b"\n").unwrap();out.flush().unwrap();
        if i%100==0 {eprintln!("source screen {}",i);}
    }
}
