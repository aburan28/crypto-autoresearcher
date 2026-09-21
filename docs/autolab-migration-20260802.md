# Autolab task and result migration (2026-08-02)

Port tag: `autolab-migration-20260802-r1`
Source commit: `dca04ac33e9ffcfc51edb3ae7e7bd558b1962d95` (dirty: `true`)
Archive tree SHA-256: `be7c43abb7b4786a08081c795d54f7bcf0d7f42566f2eb41b240865324a4171c`

## Scope and integrity boundary

- 186,032 files / 51,286,418,925 bytes verified across: `tasks`, `research`, `experiments`, `output`, `research_ledger.md`
- 32 top-level Autolab task packages cataloged.
- Source dirty state is explicit. The Git commit identifies the tracked base; per-file SHA-256 values bind tracked and untracked bytes.
- Excluded: AppleDouble metadata, `.DS_Store`, Python bytecode/cache directories, Git internals, and api_direct checkpoint state.
- `CORR-ALMIG-001` records and repairs the first run's omission of three directory-symlink fixture aliases.
- The 48 GB `inputs/refs` mirror is a local working-tree archive and is not carried in this GitHub PR; the portable Git records are the content manifests, catalog, and harness receipts.
- This is archival migration evidence only. It does not re-run tasks, validate scientific claims, or upgrade any claim tier.

## Harness bindings

- Experiment: `EXP-ALMIG-001`
- Run: `RUN-ALMIG-001-import-r1`
- File manifest: `inputs/archive_from_autolab/autolab-migration-20260802-r1/file_manifest.jsonl`
- Task catalog: `inputs/archive_from_autolab/autolab-migration-20260802-r1/task_catalog.json`
- Summary: `inputs/archive_from_autolab/autolab-migration-20260802-r1/migration_summary.json`

## Materialize the local byte mirror

The source was dirty, so reproducing the exact tree requires the same source
worktree, not only its recorded base commit. Populate `inputs/refs` without
overwriting the immutable canonical receipt:

```bash
python3 tools/migrate_autolab_archive.py --source /path/to/autolab \
  --no-harness-output \
  --metadata-dir /tmp/autolab-migration-20260802-r1-materialize
```

The command copies only missing or differing entries, then SHA-256 checks every
selected destination entry. Compare its temporary summary and tree hash with
the canonical `autolab-migration-20260802-r1` records before relying on it.

## Structured historical experiment packages

The earlier structured port is retained alongside the complete raw mirror: 84
historical EXP/RUN packages (32 `ALPF`, 11 `ALBIN`, 38 `ALISO`, and 3 `ALECF`)
are grouped by `EV-ALPF-001`, `EV-ALBIN-001`, `EV-ALISO-001`, and
`EV-ALECF-001`. See `docs/autolab-port-inventory-20260731.md`. Those records
remain historical imports with their original toy/feasibility ceilings; this
migration does not promote them.

## Task packages

| Task | Domain | Files | Result-like | Bytes | Tree SHA-256 |
|---|---|---:|---:|---:|---|
| `aes128_ctr` | system_optimization | 12 | 0 | 45470 | `1d2e68954d67c7c0188edccfcbf7dab60b3c77cc9c9ac0aadc3ba63064df3745` |
| `aes_related_differential_distinguishers` | puzzle_and_challenge | 9 | 0 | 33716 | `3d92c7cf4b7dc87d38b2410cf690eefeba42a74c313a5ac6c0e2ca84c3b73caa` |
| `bm25_search_go` | system_optimization | 20 | 0 | 21476 | `389f8c5505ad3786c0231cc46202e5ec9d759dd951f03ae06e5c89b82e9cc418` |
| `bvh_raytracer` | system_optimization | 11 | 0 | 30197 | `c9bb840d68238fd0047c389be48731661be6352bada6da68b2b1f7b2314ebf88` |
| `concurrent_kv_wal` | system_optimization | 17 | 0 | 31934 | `e3d2eeb254852b63042b352e0589717e075e4fa7ff5f6a78d64d97c435739169` |
| `data_select_ifeval` | model_development | 14 | 0 | 24506 | `b58f5e5c8f859976bd2e6b62e0fe8cb50f76ab71eddd4b62ab26949633b42a92` |
| `discover_sorting` | puzzle_and_challenge | 9 | 0 | 11085 | `2ffb01d4c3ac7cb8d9635f240dffb6f5e1ff1b14aa80f4d02d600579586efd55` |
| `ecc2k130_break` | puzzle_and_challenge | 11 | 0 | 66736 | `d6eaa068e4b7aa895a1ac492d7db72814a9a99a0742e093cf96a23d9218a8b79` |
| `ecc2k130_pollard_rho` | system_optimization | 1221 | 49 | 964762918 | `244d114e86df67dddf8eb6d686cd548f34f52fb3e621ebab12ce5a6679f82074` |
| `ecdlp_index_calculus` | puzzle_and_challenge | 1705 | 262 | 95819107 | `3b9881d9167393ad2f8d1a91bf4e935ed92b1c5f354a5e36ab09eff5ab75a87e` |
| `ecdlp_nonuniform_breakthrough` | puzzle_and_challenge | 20 | 3 | 66308 | `bb30b13215825cd36f039bbe715864f96dc7ae2382f0d35df5e213fb50353777` |
| `ecdlp_public_slice_predictor` | puzzle_and_challenge | 624 | 32 | 68645225 | `92d50a7c1ad59d2b8660002dea235128fb362824c111b55404e66691964ef1c2` |
| `fft_rust` | system_optimization | 12 | 0 | 25375 | `33ee83b06159bd336af3b858531e9cdf20da04b0bcc7aded58624bfb94780e91` |
| `flash_attention` | system_optimization | 12 | 0 | 34745 | `be722af71d512787b8a16bcf1d1859204ef04e4f0c35edd7f02166d673d80197` |
| `fredkin_sort_network` | puzzle_and_challenge | 8 | 0 | 10537 | `27740315042cf47791f0718345aed5dd66ef2e98836e28502908addcc55fe9a1` |
| `gaussian_blur` | system_optimization | 13 | 0 | 37378 | `8dd29cb93ad53fa8418189a07f1af96acbe297bb6423bb2d9bc4cacd6911cc5f` |
| `grpo_multisource` | model_development | 12 | 0 | 39157 | `aecc1c71fbdd76ba469cfea0f168cb3528d8bc39f9e0a910cd5e92ae09bb2d1d` |
| `hash_join` | system_optimization | 12 | 0 | 31548 | `72e13a17c9c3729cc6bd3e8c478c35d3f502c925a1b36327fc54022a2355bd89` |
| `llm_online_serving` | model_development | 12 | 0 | 19636 | `e17c5ecaff51ee219bd16b20af031b5f55b5376877fb8a23de463f1f847c7f55` |
| `lmfdb_weak_ec` | puzzle_and_challenge | 11 | 0 | 81319 | `7159af3f2b15993056b5c019e55bfc036a383a761583529244da80d64fa243ec` |
| `multilingual_ocr` | model_development | 11 | 0 | 35569 | `e6d91b84923b2ff38077da3cf17262609a5e963f5ae2a3dadfb03fca4f0bb7ca` |
| `radix_sort` | system_optimization | 12 | 0 | 23472 | `c3064675184b5c6492ec282fb036ee843e46ddb62ca5468a6b351c2925b07320` |
| `regex_engine` | system_optimization | 12 | 0 | 39304 | `15d68509d8c21c6fb96b62882b9124fcad31a26c8f54a369a99c677b8247d825` |
| `scaling_law` | model_development | 11 | 0 | 34920 | `f121cb9fec8a1de55671d9ec347c5a4e2c8def1a39547904f3e55bf6a295e2eb` |
| `sha1_diffpath_search` | puzzle_and_challenge | 368 | 19 | 33233021 | `870f90fb216d9b247d897ac0ed3a93b05288ab907d07ad1b6530988a878997ab` |
| `sha1_metric_frontier` | puzzle_and_challenge | 34744 | 45 | 2419365063 | `3d2141fdab162fbd2ce82957fdabfdfdda20e829cddc87b14972ce2e6ce43319` |
| `sha256_throughput` | system_optimization | 16 | 0 | 49140 | `5fc980fd84d27da11f3b7439eae87e82f8e1d97bef5ac3192c2734accc04f160` |
| `smallest_game_player` | puzzle_and_challenge | 10 | 0 | 25000 | `e25919936536b3d38bf70485dd73ff3d6e0799c6d4c23e43165f97a9af5e1bb8` |
| `sstable_compaction_rs` | system_optimization | 21 | 0 | 30007 | `8ba643a5b67181fc8455f2acd689e3cc02a7c5a26befbbcf95f9815b1647f90a` |
| `stack_machine_golf` | puzzle_and_challenge | 11 | 0 | 17806 | `f532609c9a87155ba3f7477bfd4c668ac3a2c3223d092753888d9cb080c343bc` |
| `toy_isa_opt` | puzzle_and_challenge | 10 | 0 | 29851 | `a8bc2b6ced1606e9bb08ebcc2ef741145599df8b6f0a265e2d4e69adc36baf80` |
| `vliw_scheduler` | puzzle_and_challenge | 18 | 0 | 104280 | `309ce6f1b9102d2854ea0f581e95cce7bb830a0e889432eb00e76f55bf87dfa4` |

## Verify without mutating the canonical receipt

```bash
python3 tools/migrate_autolab_archive.py --verify-only --no-harness-output \
  --source /path/to/autolab \
  --metadata-dir /tmp/autolab-migration-20260802-r1-verify
python3 tools/validate_ledger.py
```

The canonical run is immutable. The migration tool refuses to overwrite its
existing harness receipt; any successor migration must use a new experiment or
run identifier.
