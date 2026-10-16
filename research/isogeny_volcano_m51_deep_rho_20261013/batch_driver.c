/* Fail-closed arbitrary-plan driver around the verified m=51 rho core.
 *
 * The included rho.c is byte-identical to the completed degree-271 study.
 * This file changes only orchestration: it accepts an explicit numeric plan,
 * invokes the same setup_curve()/solve_one() mechanics, and measures native
 * per-unit setup wall time separately from solve_one().sec and walk_ops.
 */
#define main rho_legacy_main
#include "rho.c"
#undef main

#define PLAN_FIELDS 9

typedef struct {
  uint64_t unit_id;
  char record_id[96];
  uint64_t b;
  uint64_t a2;
  int run_mode;
  uint64_t setup_seed;
  uint64_t target_seed;
  uint64_t walk_seed;
  uint64_t target_index;
} plan_row;

static const char *plan_header =
    "unit_id,record_id,b,a2,mode,setup_seed,target_seed,walk_seed,target_index";

static int parse_plan_row(char *line, plan_row *row) {
  char *parts[PLAN_FIELDS];
  char *save = NULL;
  char *token = strtok_r(line, ",", &save);
  size_t count = 0;
  while (token != NULL && count < PLAN_FIELDS) {
    parts[count++] = token;
    token = strtok_r(NULL, ",", &save);
  }
  if (count != PLAN_FIELDS || token != NULL || parts[1][0] == '\0' ||
      strlen(parts[1]) >= sizeof(row->record_id)) {
    return 0;
  }
  for (const char *p = parts[1]; *p != '\0'; p++) {
    if (!( (*p >= 'A' && *p <= 'Z') || (*p >= 'a' && *p <= 'z') ||
           (*p >= '0' && *p <= '9') || *p == '-' )) {
      return 0;
    }
  }
  if (!parse_u64(parts[0], &row->unit_id) ||
      !parse_u64(parts[2], &row->b) ||
      !parse_u64(parts[3], &row->a2) ||
      !parse_mode(parts[4], &row->run_mode) ||
      !parse_u64(parts[5], &row->setup_seed) ||
      !parse_u64(parts[6], &row->target_seed) ||
      !parse_u64(parts[7], &row->walk_seed) ||
      !parse_u64(parts[8], &row->target_index) || row->b > MASK ||
      row->a2 > MASK || row->run_mode != 0) {
    return 0;
  }
  strcpy(row->record_id, parts[1]);
  return 1;
}

static int flush_sync_close(FILE *handle, const char *path) {
  int status = 0;
  if (fflush(handle) != 0) {
    fprintf(stderr, "cannot flush %s: %s\n", path, strerror(errno));
    status = 2;
  }
  if (handle != stdout && fsync(fileno(handle)) != 0) {
    fprintf(stderr, "cannot fsync %s: %s\n", path, strerror(errno));
    status = 2;
  }
  if (handle != stdout && fclose(handle) != 0) {
    fprintf(stderr, "cannot close %s: %s\n", path, strerror(errno));
    status = 2;
  }
  return status;
}

static void batch_usage(FILE *handle) {
  fprintf(handle,
          "usage:\n"
          "  rho-batch run-plan <plan.csv> <results.csv> <setups.csv>\n"
          "  rho-batch rng-vector <target_seed> <walk_seed> <target_index>\n");
}

int main(int argc, char **argv) {
  if (argc == 5 && strcmp(argv[1], "rng-vector") == 0) {
    uint64_t target_seed, walk_seed, target_index;
    if (!parse_u64(argv[2], &target_seed) ||
        !parse_u64(argv[3], &walk_seed) ||
        !parse_u64(argv[4], &target_index)) {
      batch_usage(stderr);
      return 1;
    }
    printf("target_seed=%" PRIu64 " walk_seed=%" PRIu64
           " target_index=%" PRIu64 " target_scalar=%" PRIu64
           " walk_stream_seed=%" PRIu64 "\n",
           target_seed, walk_seed, target_index,
           target_scalar(target_seed, target_index),
           target_walk_stream(walk_seed, target_index));
    return 0;
  }
  if (argc != 5 || strcmp(argv[1], "run-plan") != 0) {
    batch_usage(stderr);
    return 1;
  }
  FILE *input = fopen(argv[2], "r");
  if (input == NULL) {
    fprintf(stderr, "cannot open plan %s: %s\n", argv[2], strerror(errno));
    return 2;
  }
  FILE *output = open_output(argv[3]);
  if (output == NULL) {
    fclose(input);
    return 2;
  }
  FILE *setups = open_output(argv[4]);
  if (setups == NULL) {
    fclose(input);
    flush_sync_close(output, argv[3]);
    return 2;
  }
  tab = calloc(TB, sizeof(*tab));
  if (tab == NULL) {
    fprintf(stderr, "cannot allocate distinguished-point table\n");
    fclose(input);
    flush_sync_close(output, argv[3]);
    flush_sync_close(setups, argv[4]);
    return 2;
  }

  int status = 0;
  char *line = NULL;
  size_t capacity = 0;
  ssize_t length = getline(&line, &capacity, input);
  if (length < 0 || (line[length - 1] == '\n' && (line[--length] = '\0')) ||
      strcmp(line, plan_header) != 0) {
    fprintf(stderr, "plan header differs from the frozen schema\n");
    status = 2;
    goto done;
  }
  if (fprintf(output,
              "unit_id,record_id,run,target_index,target_scalar,walk_stream_seed,"
              "ops,adds,doubles,setup_ops,setup_adds,setup_doubles,walk_ops,"
              "walk_adds,walk_doubles,canon_calls,canon_x_squares,"
              "canon_y_squares,canon_sign_tests,canon_negations,walks,cycles,"
              "abandoned,useless,ok,sec\n") < 0 ||
      fprintf(setups,
              "unit_id,b,a2,mode,setup_seed,pgen_x,pgen_y,setup_fingerprint,"
              "setup_sec\n") < 0) {
    fprintf(stderr, "cannot write output headers\n");
    status = 2;
    goto done;
  }

  uint64_t expected_unit = 0;
  uint64_t current_unit = UINT64_MAX;
  uint64_t row_number = 1;
  uint64_t result_index = 0;
  plan_row current = {0};
  while ((length = getline(&line, &capacity, input)) >= 0) {
    row_number++;
    if (length == 0 || line[length - 1] != '\n') {
      fprintf(stderr, "plan row %" PRIu64 " is not newline terminated\n", row_number);
      status = 2;
      break;
    }
    line[--length] = '\0';
    if (length > 0 && line[length - 1] == '\r') line[--length] = '\0';
    plan_row row;
    if (!parse_plan_row(line, &row)) {
      fprintf(stderr, "malformed plan row %" PRIu64 "\n", row_number);
      status = 2;
      break;
    }
    if (row.unit_id != current_unit) {
      if (row.unit_id != expected_unit) {
        fprintf(stderr, "noncontiguous unit ID at plan row %" PRIu64 "\n", row_number);
        status = 2;
        break;
      }
      expected_unit++;
      current_unit = row.unit_id;
      current = row;
      B = row.b;
      A2 = row.a2;
      mode = row.run_mode;
      struct timespec start, finish;
      monotonic_now(&start);
      if (!setup_curve(row.setup_seed)) {
        fprintf(stderr, "native curve setup failed for unit %" PRIu64 "\n", row.unit_id);
        status = 2;
        break;
      }
      monotonic_now(&finish);
      double setup_sec = (double)(finish.tv_sec - start.tv_sec) +
                         1e-9 * (double)(finish.tv_nsec - start.tv_nsec);
      if (fprintf(setups,
                  "%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%d,%" PRIu64
                  ",%" PRIu64 ",%" PRIu64 ",%016" PRIx64 ",%.9f\n",
                  row.unit_id, B, A2, mode, row.setup_seed, Pgen.x, Pgen.y,
                  setup_fingerprint, setup_sec) < 0) {
        fprintf(stderr, "cannot write setup receipt\n");
        status = 2;
        break;
      }
    } else if (row.b != current.b || row.a2 != current.a2 ||
               row.run_mode != current.run_mode ||
               row.setup_seed != current.setup_seed) {
      fprintf(stderr, "unit %" PRIu64 " changes native curve/setup\n", row.unit_id);
      status = 2;
      break;
    }

    result value = solve_one(row.target_seed, row.walk_seed, row.target_index);
    if (fprintf(output,
                "%" PRIu64 ",%s,%" PRIu64 ",%" PRIu64 ",%" PRIu64
                ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64
                ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64
                ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64
                ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%" PRIu64
                ",%" PRIu64 ",%" PRIu64 ",%" PRIu64 ",%d,%.9f\n",
                row.unit_id, row.record_id, result_index, value.target_index,
                value.target_scalar, value.walk_stream_seed, value.ops,
                value.adds, value.doubles, value.setup_ops, value.setup_adds,
                value.setup_doubles, value.walk_ops, value.walk_adds,
                value.walk_doubles, value.canon_calls,
                value.canon_x_squares, value.canon_y_squares,
                value.canon_sign_tests, value.canon_negations, value.walks,
                value.cycles, value.abandoned, value.useless, value.ok,
                value.sec) < 0) {
      fprintf(stderr, "cannot write result row\n");
      status = 2;
      break;
    }
    result_index++;
    if (!value.ok) {
      fprintf(stderr, "planted-log verification failed for %s\n", row.record_id);
      status = 2;
      break;
    }
  }
  if (ferror(input)) {
    fprintf(stderr, "cannot read plan %s: %s\n", argv[2], strerror(errno));
    status = 2;
  }
  if (result_index == 0) {
    fprintf(stderr, "plan contains no records\n");
    status = 2;
  }

done:
  free(line);
  if (fclose(input) != 0) status = 2;
  if (flush_sync_close(output, argv[3]) != 0) status = 2;
  if (flush_sync_close(setups, argv[4]) != 0) status = 2;
  free(tab);
  return status;
}
