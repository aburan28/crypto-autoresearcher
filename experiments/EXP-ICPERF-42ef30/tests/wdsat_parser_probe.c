/* Parser-only admission check; this does not invoke the WDSat search. */
#include "dimacs.h"
#include "config.h"
#include <stdlib.h>

int main(int argc, char **argv)
{
    FILE *input;
    long expected_equations;
    int read_to_eof;
    if (argc != 3) return 2;
    expected_equations = strtol(argv[2], NULL, 10);
    input = fopen(argv[1], "r");
    if (!input) return 3;
    dimacs_read_formula(input);
    read_to_eof = feof(input);
    fclose(input);
    printf("vars=%lld xor_equations=%lld eof=%d\n",
           (long long)dimacs_nb_vars(),
           (long long)dimacs_nb_xor_equations(),
           read_to_eof);
    /* The vendored enhanced parser leaves dimacs_is_read() false on success. */
    return read_to_eof && dimacs_nb_vars() == __MAX_ID__
           && dimacs_nb_xor_equations() == expected_equations ? 0 : 4;
}
