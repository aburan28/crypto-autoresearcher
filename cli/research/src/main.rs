//! Native CLI frontend. The Python adapter remains the single source of truth.
use std::env;
use std::process::{Command, ExitCode};

fn usage() {
    eprintln!("Usage: research <batch|campaign|doctor|...> [args...]\n\n  research batch plan --delivery auto\n  research batch status --all\n  research batch collect <id>\n  research campaign autopilot --preset anthropic-batch\n\nEnvironment: AUTORESEARCH_PYTHON selects the interpreter.");
}

fn main() -> ExitCode {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.is_empty() || matches!(args[0].as_str(), "-h" | "--help") {
        usage();
        return ExitCode::SUCCESS;
    }
    let python = env::var("AUTORESEARCH_PYTHON").unwrap_or_else(|_| "python3".into());
    let mut cmd = Command::new(&python);
    // Batch subcommands use the existing adapter; all others use the unified CLI.
    if args[0] == "batch" {
        cmd.args(["-m", "orchestration.adapter"]);
    } else {
        cmd.args(["-m", "orchestration"]);
    }
    let status = cmd.args(&args).status();
    match status {
        Ok(s) => ExitCode::from(s.code().unwrap_or(1).clamp(0, 255) as u8),
        Err(e) => {
            eprintln!("research: failed to start {python}: {e}. Install the repository with 'pip install -e .' and set AUTORESEARCH_PYTHON if needed.");
            ExitCode::from(127)
        }
    }
}
