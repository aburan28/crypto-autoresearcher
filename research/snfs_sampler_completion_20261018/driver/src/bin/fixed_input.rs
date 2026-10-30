use serde_json::{json,Value};
use std::fs::{self,OpenOptions};
use std::io::{BufWriter,Write};
use std::path::PathBuf;

fn main() {
    let args:Vec<String>=std::env::args().collect();
    assert!(args.len()==5 && args[1]=="--panel" && args[3]=="--out");
    let panel:Value=serde_json::from_slice(&fs::read(&args[2]).unwrap()).unwrap();
    let out=PathBuf::from(&args[4]);fs::create_dir(&out).expect("fresh output directory required");
    let ladder:Vec<u64>=panel["ladder"].as_array().unwrap().iter().map(|v|v.as_u64().unwrap()).collect();
    let mut rows=Vec::new();
    for job in panel["jobs"].as_array().unwrap() {
        let job_id=job["id"].as_str().unwrap();
        assert!(job_id.chars().all(|c|c.is_ascii_alphanumeric()||c=='-'));
        let input=panel["inputs"].as_array().unwrap().iter().find(|v|v["id"]==job["input_id"]).unwrap();
        let path=out.join(format!("{}.jsonl",job_id));
        let mut writer=BufWriter::new(OpenOptions::new().write(true).create_new(true).open(path).unwrap());
        let result=snfs_sampler_observer::run_input(input,job["search_seed"].as_str().unwrap(),&ladder,|event|{
            serde_json::to_writer(&mut writer,&event).unwrap();writer.write_all(b"\n").unwrap();
        });
        writer.flush().unwrap();
        eprintln!("{} {} D={}",job_id,job["input_id"],result["final"]["distinct_residues"]);
        rows.push(json!({"job":job,"input_id":input["id"],"observations":result}));
    }
    let bytes=serde_json::to_vec_pretty(&json!({"schema":"snfs.fixed_input_observations.v1","rows":rows})).unwrap();
    let mut file=OpenOptions::new().create_new(true).write(true).open(out.join("panel-result.json")).unwrap();
    file.write_all(&bytes).unwrap();file.write_all(b"\n").unwrap();
}
