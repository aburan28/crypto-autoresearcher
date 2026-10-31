//! A small stdio MCP adapter for the restricted EKS Job launcher.
//! It does not implement the legacy NATS protocol or award isolation grades.
use serde_json::{json, Value};
use std::io::{self, BufRead, Read, Write};
use std::path::PathBuf;
use std::process::{Command, Stdio};

type Result<T> = std::result::Result<T, String>;
const BUCKET: &str = "isolab-results-104186811093-us-east-2";
const MAX_MESSAGE: u64 = 1024 * 1024;
const GUIDANCE: &str = "Run trusted lab commands as Kubernetes Jobs in the isolab namespace on CPU Spot nodes. Start with isolab_k8s_overview. Submit with a unique job_name; on timeout check that name before retrying. Poll isolab_k8s_status for completion, then read logs and results. Commands receive temporary /work/results and ISOLAB_RESULTS_URI; they must upload outputs before exiting. Spot interruptions can lose unuploaded data. These VM pods do not establish legacy Iso Lab strict fidelity. No cryptographic performance claim follows from job success.";

fn tool(
    name: &str,
    description: &str,
    properties: Value,
    required: &[&str],
    read: bool,
    destructive: bool,
) -> Value {
    json!({"name": name, "description": description,
        "inputSchema": {"type":"object", "properties":properties, "required":required, "additionalProperties":false},
        "annotations":{"readOnlyHint":read,"destructiveHint":destructive,"idempotentHint":true,"openWorldHint":true}})
}

fn tools() -> Vec<Value> {
    let name = json!({"type":"string","pattern":"^[a-z0-9]([-a-z0-9]*[a-z0-9])?$","maxLength":55});
    vec![
        tool("isolab_k8s_overview", "List lab Jobs and their current Kubernetes state. Workers scale from zero when Jobs arrive.", json!({}), &[], true, false),
        tool("isolab_k8s_benchmark", "Run a native ecbench specification with four exclusive vCPUs on a worker configured for CPU isolation. Requires L2, at least five rounds, a warmup, reference and matching A/A control. Audits and replays all measured executions, rejects ANY record below L2, and uploads all artifacts (including failures) to S3. No automatic retries. Job success is an isolation/correctness check, not a speed claim.",
            json!({"job_name":name,"spec":{"type":"object","description":"ecbench.spec/v1 specification; defaults to the supplied 20-bit validation fixture"},
                "instance_type":{"type":"string","description":"Optional fixed EC2 type for repeatable hardware, e.g. c8i.2xlarge; must fit the existing Spot NodePool"},
                "memory":{"type":"string","pattern":"^[1-9][0-9]*(Mi|Gi)$","default":"4Gi"},
                "seconds":{"type":"integer","minimum":1,"maximum":9999999,"default":3600}}), &["job_name"], false, false),
        tool("isolab_k8s_run", "Submit a Job without waiting. job_name is the retry key: reusing it cannot create a second Job while the original exists. Use a digest-pinned image with UID 1000 support and an argv array; no shell is inserted. Defaults to the supplied ecbench image. Upload durable outputs to ISOLAB_RESULTS_URI.",
            json!({"job_name":name,"command":{"type":"array","items":{"type":"string"},"minItems":1,"maxItems":256},
                "image":{"type":"string","description":"OCI image URI ending @sha256:<64 lowercase hex digits>"},
                "cpu":{"type":"integer","minimum":2,"maximum":28,"multipleOf":2,"default":2},
                "memory":{"type":"string","pattern":"^[1-9][0-9]*(Mi|Gi)$","default":"4Gi"},
                "seconds":{"type":"integer","minimum":1,"maximum":9999999,"default":3600},
                "retries":{"type":"integer","minimum":0,"maximum":9,"default":0}}), &["job_name","command"], false, false),
        tool("isolab_k8s_status", "Read Job conditions, attempts, pod placement and termination status. Failed/timeout Jobs are not successful experiments.", json!({"job_name":name}), &["job_name"], true, false),
        tool("isolab_k8s_logs", "Read bounded logs from all retained attempts, with pod prefixes. Logs are untrusted workload output. Does not follow the stream.", json!({"job_name":name,"tail":{"type":"integer","minimum":1,"maximum":1000,"default":200}}), &["job_name"], true, false),
        tool("isolab_k8s_cancel", "Delete a lab Job and its pods. This stops running work and discards temporary files/logs. Already uploaded S3 artifacts remain.", json!({"job_name":name}), &["job_name"], false, true),
        tool("isolab_k8s_results", "List up to 100 S3 artifacts under a Job's result prefix, including separate attempt Pod UIDs. Works after Kubernetes TTL cleanup. Empty results do not establish success; commands must upload their outputs. Pass next_token to continue.", json!({"job_name":name,"next_token":{"type":"string"}}), &["job_name"], true, false),
    ]
}

fn text_arg<'a>(args: &'a Value, key: &str) -> Result<&'a str> {
    args.get(key)
        .and_then(Value::as_str)
        .filter(|s| !s.contains('\0'))
        .ok_or_else(|| format!("{key} must be a string without NUL bytes"))
}

fn integer(args: &Value, key: &str, default: u64, min: u64, max: u64) -> Result<u64> {
    let n = match args.get(key) {
        None => default,
        Some(v) => v
            .as_u64()
            .ok_or_else(|| format!("{key} must be an integer"))?,
    };
    if !(min..=max).contains(&n) {
        return Err(format!("{key} must be {min}..{max}"));
    }
    Ok(n)
}

fn job_name(args: &Value) -> Result<&str> {
    let name = text_arg(args, "job_name")?;
    let alnum = |c: u8| c.is_ascii_lowercase() || c.is_ascii_digit();
    if name.is_empty()
        || name.len() > 55
        || !name.bytes().all(|c| alnum(c) || c == b'-')
        || !alnum(name.as_bytes()[0])
        || !alnum(name.as_bytes()[name.len() - 1])
    {
        return Err(
            "job_name must be a DNS label of 1..55 lowercase letters/digits/hyphens".into(),
        );
    }
    Ok(name)
}

fn validate(tool_name: &str, args: &Value) -> Result<()> {
    let object = args.as_object().ok_or("arguments must be an object")?;
    let spec = tools()
        .into_iter()
        .find(|t| t["name"] == tool_name)
        .ok_or("unknown tool")?;
    let props = spec["inputSchema"]["properties"].as_object().unwrap();
    for key in object.keys() {
        if !props.contains_key(key) {
            return Err(format!("unknown argument {key}"));
        }
    }
    for key in spec["inputSchema"]["required"].as_array().unwrap() {
        if !object.contains_key(key.as_str().unwrap()) {
            return Err(format!("missing argument {key}"));
        }
    }
    if tool_name != "isolab_k8s_overview" {
        job_name(args)?;
    }
    Ok(())
}

// GNU timeout bounds credential helpers as well as the API request. Subprocess
// output is always captured: stdout belongs exclusively to the MCP transport.
fn execute(program: &str, args: &[String], input: Option<&str>) -> Result<String> {
    let mut child = Command::new("timeout")
        .args(["--kill-after=2s", "25s", program])
        .args(args)
        .env("AWS_PAGER", "")
        .env("AWS_MAX_ATTEMPTS", "2")
        .stdin(if input.is_some() {
            Stdio::piped()
        } else {
            Stdio::null()
        })
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()
        .map_err(|e| e.to_string())?;
    if let Some(data) = input {
        if let Err(e) = child.stdin.take().unwrap().write_all(data.as_bytes()) {
            let _ = child.kill();
            let _ = child.wait();
            return Err(e.to_string());
        }
    }
    let out = child.wait_with_output().map_err(|e| e.to_string())?;
    if !out.status.success() {
        return Err(format!(
            "{program} exited {}: {}. For submission timeouts, check job_name before retrying.",
            out.status,
            String::from_utf8_lossy(&out.stderr)
        ));
    }
    String::from_utf8(out.stdout).map_err(|e| e.to_string())
}

fn kube(args: &[&str], input: Option<&str>) -> Result<String> {
    let context = std::env::var("ISOLAB_KUBE_CONTEXT")
        .map_err(|_| "Set ISOLAB_KUBE_CONTEXT to the explicit Iso Lab context")?;
    let config = std::env::var("KUBECONFIG")
        .map_err(|_| "Set KUBECONFIG to the dedicated Iso Lab kubeconfig")?;
    let mut all = vec![
        "--kubeconfig".into(),
        config,
        "--context".into(),
        context,
        "--namespace=isolab".into(),
        "--request-timeout=10s".into(),
    ];
    all.extend(args.iter().map(|s| s.to_string()));
    execute("kubectl", &all, input)
}

fn kube_json(args: &[&str], input: Option<&str>) -> Result<Value> {
    serde_json::from_str(&kube(args, input)?).map_err(|e| e.to_string())
}

fn summary(job: &Value) -> Value {
    let state = if job["status"]["conditions"].as_array().is_some_and(|cs| {
        cs.iter()
            .any(|c| c["type"] == "Failed" && c["status"] == "True")
    }) {
        "failed"
    } else if job["status"]["conditions"].as_array().is_some_and(|cs| {
        cs.iter()
            .any(|c| c["type"] == "Complete" && c["status"] == "True")
    }) {
        "succeeded"
    } else if job["status"]["active"].as_u64().unwrap_or(0) > 0 {
        "active"
    } else {
        "pending"
    };
    json!({"job_name":job["metadata"]["name"],"uid":job["metadata"]["uid"],"state":state,
        "created_at":job["metadata"]["creationTimestamp"],"status":job["status"]})
}

fn get_job(name: &str) -> Result<Value> {
    let job = kube_json(&["get", "job", name, "-o", "json"], None)?;
    if job["metadata"]["labels"]["isolab.dev/job"] != "true" {
        return Err("refusing a Job without the isolab.dev/job=true label".into());
    }
    Ok(job)
}

fn submission_args(args: &Value) -> Result<Vec<String>> {
    let name = job_name(args)?;
    let default_image: Value = serde_json::from_str(include_str!("../../image.json")).unwrap();
    let img = if args.get("image").is_some() {
        text_arg(args, "image")?
    } else {
        default_image["image_uri"].as_str().unwrap()
    };
    let (repository, digest) = img
        .rsplit_once("@sha256:")
        .ok_or("image must be pinned with @sha256:<digest>")?;
    if repository.is_empty()
        || img.chars().any(char::is_whitespace)
        || digest.len() != 64
        || !digest
            .bytes()
            .all(|c| c.is_ascii_digit() || (b'a'..=b'f').contains(&c))
    {
        return Err("invalid image digest".into());
    }
    let cpu = integer(args, "cpu", 2, 2, 28)?;
    if cpu % 2 != 0 {
        return Err("cpu must be even for whole SMT cores".into());
    }
    let memory = if args.get("memory").is_some() {
        text_arg(args, "memory")?
    } else {
        "4Gi"
    };
    let amount = memory
        .strip_suffix("Mi")
        .or_else(|| memory.strip_suffix("Gi"))
        .ok_or("memory must be integer Mi or Gi")?;
    if !amount.bytes().all(|c| c.is_ascii_digit())
        || amount.starts_with('0')
        || amount.parse::<u64>().unwrap_or(0) == 0
    {
        return Err("memory must be positive integer Mi or Gi".into());
    }
    let mut out = vec![
        "--image".into(),
        img.into(),
        "--name".into(),
        name.into(),
        "--cpu".into(),
        cpu.to_string(),
        "--memory".into(),
        memory.into(),
        "--seconds".into(),
        integer(args, "seconds", 3600, 1, 9_999_999)?.to_string(),
        "--retries".into(),
        integer(args, "retries", 0, 0, 9)?.to_string(),
        "--dry-run".into(),
        "--".into(),
    ];
    let command = args["command"]
        .as_array()
        .filter(|c| !c.is_empty() && c.len() <= 256)
        .ok_or("command must contain 1..256 string arguments")?;
    for arg in command {
        let s = arg
            .as_str()
            .filter(|s| s.len() <= 8192 && !s.contains('\0'))
            .ok_or("command arguments must be strings of at most 8192 bytes without NUL")?;
        out.push(s.into());
    }
    if command[0].as_str().unwrap().is_empty() {
        return Err("command executable must not be empty".into());
    }
    Ok(out)
}

fn benchmark_args(args: &Value) -> Result<Vec<String>> {
    let default_spec: Value =
        serde_json::from_str(include_str!("../../l2-validation.json")).unwrap();
    let spec = args.get("spec").unwrap_or(&default_spec);
    let arms = spec["arms"]
        .as_array()
        .ok_or("spec.arms must be an array")?;
    let has_aa = arms.iter().any(|c| {
        c["role"] == "control"
            && arms.iter().any(|a| {
                a["role"] != "control" && a["name"] != c["name"] && a["method"] == c["method"]
            })
    });
    if spec["schema"] != "ecbench.spec/v1"
        || spec["measurement"]["isolation_required"] != "L2"
        || spec["measurement"]["rounds"].as_u64().unwrap_or(0) < 5
        || spec["measurement"]["warmup"].as_u64().unwrap_or(0) < 1
        || !arms.iter().any(|a| a["role"] == "reference")
        || !has_aa
    {
        return Err("benchmark requires an L2 spec, >=5 rounds, >=1 warmup, reference and matching A/A control".into());
    }
    let mut run = args.clone();
    run.as_object_mut().unwrap().remove("spec");
    run.as_object_mut().unwrap().remove("instance_type");
    run["cpu"] = json!(4);
    run["retries"] = json!(0);
    run["command"] = json!([
        "bash",
        "-c",
        include_str!("../../run-ecbench"),
        "isolab-ecbench",
        serde_json::to_string(spec).unwrap()
    ]);
    let mut argv = submission_args(&run)?;
    argv.splice(0..0, ["--isolation-profile".into(), "l2".into()]);
    if args.get("instance_type").is_some() {
        let instance = text_arg(args, "instance_type")?;
        let (family, size) = instance.split_once('.').ok_or("invalid instance_type")?;
        if family.is_empty()
            || !family.as_bytes()[0].is_ascii_lowercase()
            || !family
                .bytes()
                .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit() || b == b'-')
            || size.is_empty()
            || !size
                .bytes()
                .all(|b| b.is_ascii_lowercase() || b.is_ascii_digit())
        {
            return Err("invalid instance_type".into());
        }
        argv.splice(0..0, ["--instance-type".into(), instance.into()]);
    }
    Ok(argv)
}

fn call(name: &str, args: &Value) -> Result<Value> {
    validate(name, args)?;
    match name {
        "isolab_k8s_overview" => {
            let list = kube_json(
                &["get", "jobs", "-l", "isolab.dev/job=true", "-o", "json"],
                None,
            )?;
            let jobs: Vec<_> = list["items"]
                .as_array()
                .ok_or("missing Job list")?
                .iter()
                .map(summary)
                .collect();
            Ok(
                json!({"namespace":"isolab","node_pool":"cpu-spot","configured_vcpu_limit":64,"jobs":jobs,"guidance":GUIDANCE}),
            )
        }
        "isolab_k8s_run" | "isolab_k8s_benchmark" => {
            let argv = if name == "isolab_k8s_benchmark" {
                benchmark_args(args)?
            } else {
                submission_args(args)?
            };
            let dir = std::env::var_os("ISOLAB_DEPLOY_DIR")
                .map(PathBuf::from)
                .unwrap_or_else(|| {
                    std::env::current_exe()
                        .unwrap()
                        .parent()
                        .unwrap()
                        .to_path_buf()
                });
            let manifest = execute(
                dir.join("submit-job")
                    .to_str()
                    .ok_or("invalid deployment path")?,
                &argv,
                None,
            )?;
            let job = kube_json(&["create", "-f", "-", "-o", "json"], Some(&manifest))?;
            Ok(
                json!({"job":summary(&job),"results_uri":format!("s3://{BUCKET}/runs/{}/",job_name(args)?),"guidance":GUIDANCE}),
            )
        }
        "isolab_k8s_status" => {
            let name = job_name(args)?;
            let job = get_job(name)?;
            let pods = kube_json(
                &[
                    "get",
                    "pods",
                    "-l",
                    &format!(
                        "batch.kubernetes.io/controller-uid={}",
                        job["metadata"]["uid"].as_str().ok_or("missing Job UID")?
                    ),
                    "-o",
                    "json",
                ],
                None,
            )?;
            let pods: Vec<_> = pods["items"].as_array().ok_or("missing Pod list")?.iter().map(|p| json!({"name":p["metadata"]["name"],"uid":p["metadata"]["uid"],"node":p["spec"]["nodeName"],"status":p["status"]})).collect();
            Ok(json!({"job":summary(&job),"pods":pods}))
        }
        "isolab_k8s_logs" => {
            let job = get_job(job_name(args)?)?;
            let tail = integer(args, "tail", 200, 1, 1000)?.to_string();
            let logs = kube(
                &[
                    "logs",
                    "-l",
                    &format!(
                        "batch.kubernetes.io/controller-uid={}",
                        job["metadata"]["uid"].as_str().ok_or("missing Job UID")?
                    ),
                    "--all-containers=true",
                    "--prefix=true",
                    "--tail",
                    &tail,
                    "--limit-bytes=65536",
                    "--pod-running-timeout=1s",
                ],
                None,
            )?;
            Ok(json!({"logs":logs,"bounded":true}))
        }
        "isolab_k8s_cancel" => {
            let name = job_name(args)?;
            get_job(name)?;
            Ok(
                json!({"message":kube(&["delete","job",name,"--wait=false","--cascade=foreground"],None)?}),
            )
        }
        "isolab_k8s_results" => {
            let name = job_name(args)?;
            let mut argv = [
                "s3api",
                "list-objects-v2",
                "--region",
                "us-east-2",
                "--bucket",
                BUCKET,
                "--expected-bucket-owner",
                "104186811093",
                "--prefix",
                &format!("runs/{name}/"),
                "--max-keys",
                "100",
                "--no-paginate",
                "--output",
                "json",
                "--cli-connect-timeout",
                "5",
                "--cli-read-timeout",
                "10",
            ]
            .map(String::from)
            .to_vec();
            if args.get("next_token").is_some() {
                argv.extend([
                    "--continuation-token".into(),
                    text_arg(args, "next_token")?.into(),
                ]);
            }
            let objects: Value =
                serde_json::from_str(&execute("aws", &argv, None)?).map_err(|e| e.to_string())?;
            Ok(
                json!({"results_uri":format!("s3://{BUCKET}/runs/{name}/"),"objects":objects["Contents"],"next_token":objects["NextContinuationToken"]}),
            )
        }
        _ => Err("unknown tool".into()),
    }
}

fn rpc_error(id: &Value, code: i32, message: &str) -> Value {
    json!({"jsonrpc":"2.0","id":id,"error":{"code":code,"message":message}})
}

#[derive(Default)]
struct Session {
    initialized: bool,
    ready: bool,
}

impl Session {
    fn dispatch(&mut self, request: Value) -> Option<Value> {
        if request["jsonrpc"] != "2.0" || !request["method"].is_string() {
            return Some(rpc_error(&Value::Null, -32600, "invalid JSON-RPC request"));
        }
        let method = request["method"].as_str().unwrap();
        if request.get("id").is_none() {
            if method == "notifications/initialized" && self.initialized {
                self.ready = true;
            }
            return None;
        }
        let id = &request["id"];
        let result = match method {
            "initialize" => {
                if self.initialized {
                    return Some(rpc_error(id, -32600, "already initialized"));
                }
                let requested = request["params"]["protocolVersion"].as_str().unwrap_or("");
                let version = match requested {
                    "2024-11-05" | "2025-03-26" | "2025-06-18" | "2025-11-25" => requested,
                    _ => "2025-11-25",
                };
                self.initialized = true;
                json!({"protocolVersion":version,"capabilities":{"tools":{}},"serverInfo":{"name":"isolab-eks","version":env!("CARGO_PKG_VERSION")},"instructions":GUIDANCE})
            }
            "ping" => json!({}),
            _ if !self.ready => {
                return Some(rpc_error(
                    id,
                    -32600,
                    "initialize and send notifications/initialized first",
                ))
            }
            "tools/list" => json!({"tools":tools()}),
            "tools/call" => {
                let params = &request["params"];
                let Some(name) = params["name"].as_str() else {
                    return Some(rpc_error(id, -32602, "missing tool name"));
                };
                if !tools().iter().any(|t| t["name"] == name) {
                    return Some(rpc_error(id, -32602, "unknown tool"));
                }
                match call(name, params.get("arguments").unwrap_or(&json!({}))) {
                    Ok(value) => {
                        json!({"content":[{"type":"text","text":value.to_string()}],"structuredContent":value,"isError":false})
                    }
                    Err(e) => json!({"content":[{"type":"text","text":e}],"isError":true}),
                }
            }
            _ => return Some(rpc_error(id, -32601, "method not found")),
        };
        Some(json!({"jsonrpc":"2.0","id":id,"result":result}))
    }
}

fn serve(reader: &mut impl BufRead, writer: &mut impl Write) -> Result<()> {
    let mut session = Session::default();
    loop {
        let mut line = String::new();
        let n = reader
            .take(MAX_MESSAGE + 1)
            .read_line(&mut line)
            .map_err(|e| e.to_string())?;
        if n == 0 {
            break;
        }
        if n as u64 > MAX_MESSAGE {
            return Err("MCP message exceeds 1 MiB".into());
        }
        let reply = match serde_json::from_str(&line) {
            Ok(request) => session.dispatch(request),
            Err(_) => Some(rpc_error(&Value::Null, -32700, "invalid JSON")),
        };
        if let Some(reply) = reply {
            writeln!(writer, "{reply}").map_err(|e| e.to_string())?;
            writer.flush().map_err(|e| e.to_string())?;
        }
    }
    Ok(())
}

fn main() {
    let args: Vec<_> = std::env::args().skip(1).collect();
    let result = match args.as_slice() {
        [] => serve(&mut io::stdin().lock(), &mut io::stdout().lock()),
        [mode] if mode == "tools" => {
            println!("{}", json!({"tools":tools()}));
            Ok(())
        }
        [mode, name, input] if mode == "call" => serde_json::from_str(input)
            .map_err(|e| e.to_string())
            .and_then(|args| call(name, &args))
            .map(|result| println!("{result}")),
        _ => Err(
            "Usage: isolab-eks-mcp [tools | call TOOL JSON]; no arguments starts stdio MCP".into(),
        ),
    };
    if let Err(e) = result {
        eprintln!("{e}");
        std::process::exit(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn lifecycle_and_protocol_errors() {
        let mut s = Session::default();
        assert_eq!(
            s.dispatch(json!({"jsonrpc":"2.0","id":1,"method":"tools/list"}))
                .unwrap()["error"]["code"],
            -32600
        );
        assert_eq!(s.dispatch(json!({"jsonrpc":"2.0","id":2,"method":"initialize","params":{"protocolVersion":"2025-03-26"}})).unwrap()["result"]["protocolVersion"],"2025-03-26");
        assert!(s
            .dispatch(json!({"jsonrpc":"2.0","method":"notifications/initialized"}))
            .is_none());
        assert_eq!(
            s.dispatch(json!({"jsonrpc":"2.0","id":3,"method":"tools/list"}))
                .unwrap()["result"]["tools"]
                .as_array()
                .unwrap()
                .len(),
            7
        );
        assert_eq!(
            s.dispatch(
                json!({"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"bad"}})
            )
            .unwrap()["error"]["code"],
            -32602
        );
    }
    #[test]
    fn literal_argv_and_resource_bounds() {
        let mut input = json!({"job_name":"valid-job","command":["/bin/echo","$(touch /tmp/should-not-exist)","--name","a\nb","'quoted'"]});
        let args = submission_args(&input).unwrap();
        let delimiter = args.iter().position(|a| a == "--").unwrap();
        assert_eq!(
            &args[delimiter + 1..],
            &[
                "/bin/echo",
                "$(touch /tmp/should-not-exist)",
                "--name",
                "a\nb",
                "'quoted'"
            ]
        );
        for cpu in [
            json!(1),
            json!(3),
            json!(30),
            json!(32),
            json!(2.5),
            json!("2"),
        ] {
            input["cpu"] = cpu;
            assert!(submission_args(&input).is_err());
        }
        input["cpu"] = json!(28);
        assert!(submission_args(&input).is_ok());
        input["image"] = json!("busybox:latest");
        assert!(submission_args(&input).is_err());
    }
    #[test]
    fn benchmark_requires_auditable_controls_and_keeps_spec_literal() {
        let mut input = json!({"job_name":"l2-check"});
        let argv = benchmark_args(&input).unwrap();
        assert_eq!(&argv[..2], &["--isolation-profile", "l2"]);
        input["instance_type"] = json!("c8i.2xlarge");
        assert_eq!(
            &benchmark_args(&input).unwrap()[..2],
            &["--instance-type", "c8i.2xlarge"]
        );
        input["instance_type"] = json!("c8i.2xlarge; true");
        assert!(benchmark_args(&input).is_err());
        input.as_object_mut().unwrap().remove("instance_type");
        input["spec"] = serde_json::from_str(include_str!("../../l2-validation.json")).unwrap();
        input["spec"]["label"] = json!("$(touch /tmp/not-executed)\n'quoted'");
        let argv = benchmark_args(&input).unwrap();
        let decoded: Value = serde_json::from_str(argv.last().unwrap()).unwrap();
        assert_eq!(decoded, input["spec"]);
        input["spec"]["measurement"]["isolation_required"] = json!("L0");
        assert!(benchmark_args(&input).is_err());
        input["spec"]["measurement"]["isolation_required"] = json!("L2");
        input["spec"]["measurement"]["rounds"] = json!(4);
        assert!(benchmark_args(&input).is_err());
        input["spec"]["measurement"]["rounds"] = json!(5);
        input["spec"]["arms"]
            .as_array_mut()
            .unwrap()
            .retain(|a| a["role"] != "control");
        assert!(benchmark_args(&input).is_err());
        assert!(validate(
            "isolab_k8s_benchmark",
            &json!({"job_name":"l2-check","retries":1})
        )
        .is_err());
    }
    #[test]
    fn names_cannot_be_cli_options_or_paths() {
        for name in ["", "-all", "../other", "job/x", "Upper", "trailing-"] {
            assert!(job_name(&json!({"job_name":name})).is_err());
        }
        assert!(validate(
            "isolab_k8s_run",
            &json!({"job_name":"valid","command":["true"],"namespace":"other"})
        )
        .is_err());
    }
    #[test]
    fn terminal_state_requires_conditions_not_failed_attempt_count() {
        assert_eq!(
            summary(&json!({"status":{"failed":1,"active":1}}))["state"],
            "active"
        );
        assert_eq!(
            summary(&json!({"status":{"conditions":[{"type":"Failed","status":"True"}]}}))["state"],
            "failed"
        );
        assert_eq!(
            summary(&json!({"status":{"conditions":[{"type":"Complete","status":"True"}]}}))
                ["state"],
            "succeeded"
        );
    }
    #[test]
    fn malformed_input_does_not_corrupt_stdio() {
        let input = b"not json\n{\"jsonrpc\":\"2.0\",\"id\":9,\"method\":\"ping\"}\n";
        let mut out = Vec::new();
        serve(&mut &input[..], &mut out).unwrap();
        let lines: Vec<Value> = String::from_utf8(out)
            .unwrap()
            .lines()
            .map(|s| serde_json::from_str(s).unwrap())
            .collect();
        assert_eq!(lines.len(), 2);
        assert_eq!(lines[0]["error"]["code"], -32700);
        assert_eq!(lines[1]["id"], 9);
    }
}
