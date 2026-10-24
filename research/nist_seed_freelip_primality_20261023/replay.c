#include <stdio.h>
#include <string.h>
#include "lip.h"

int main(int argc, char **argv) {
    verylong n = 0;
    long consumed, probable_1, probable_5, prime_1;

    if (argc != 2) {
        fprintf(stderr, "usage: replay DECIMAL_ORDER\n");
        return 2;
    }
    zstart();
    consumed = zstrtoz(argv[1], &n);
    if (consumed != (long) strlen(argv[1])) {
        fprintf(stderr, "input parse mismatch: %ld of %lu bytes\n",
                consumed, (unsigned long) strlen(argv[1]));
        return 3;
    }
    zrstarts(7157891L);
    probable_1 = zprobprime(n, 1L);
    zrstarts(7157891L);
    probable_5 = zprobprime(n, 5L);
    prime_1 = zprime(n, 1L, 2L);
    printf("%ld %ld %ld\n", probable_1, probable_5, prime_1);
    zfree(&n);
    return 0;
}
