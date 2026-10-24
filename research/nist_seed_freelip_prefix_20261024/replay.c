#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "lip.h"

static void dump(char *name, verylong value) {
    long i, length = value ? value[0] : 0;
    printf("%s %ld", name, length);
    for (i = 1; i <= length; i++) printf(" %ld", value[i]);
    printf("\n");
}

static void parse(char *text, verylong *value) {
    if (zstrtoz(text, value) != (long)strlen(text)) {
        fprintf(stderr, "decimal parse mismatch\n");
        exit(3);
    }
}

int main(int argc, char **argv) {
    verylong p=0, b=0, n=0, state=0, x=0, rhs=0, temp=0;
    long rounds, prefix_return=-1, tries=0, i;
    char *mode;
    if (argc != 7) return 2;
    mode=argv[1]; rounds=strtol(argv[3],0,10);
    zstart();
    parse(argv[4],&p); parse(argv[5],&b); parse(argv[6],&n);
    zrstarts(strtol(argv[2],0,10));
    printf("NBITS %d\n",NBITS);
    zrseed(&state); dump("INITIAL",state);
    if (!strcmp(mode,"direct")) {
        for (i=0;i<rounds;i++) (void)zrandom(RADIX);
    } else if (!strcmp(mode,"prob-p")) prefix_return=zprobprime(p,rounds);
    else if (!strcmp(mode,"prob-n")) prefix_return=zprobprime(n,rounds);
    else if (!strcmp(mode,"prime-p")) prefix_return=zprime(p,rounds,2L);
    else if (!strcmp(mode,"prime-n") || !strcmp(mode,"classify-n")) prefix_return=zprime(n,rounds,2L);
    else return 4;
    printf("RETURN %ld\n",prefix_return);
    zrseed(&state); dump("PREFIX",state);
    if (strcmp(mode,"classify-n")) {
        for (tries=1;tries<=32;tries++) {
            zrandomb(p,&x);
            zsqmod(x,p,&rhs); zmulmod(rhs,x,p,&rhs);
            zsmul(x,3L,&temp); zsub(rhs,temp,&rhs);
            zadd(rhs,b,&rhs); zmod(rhs,p,&rhs);
            if (zjacobi(rhs,p)==1) break;
        }
        if (tries>32) return 5;
        dump("X",x);
    }
    printf("TRIES %ld\n",tries);
    zrseed(&state); dump("FINAL",state);
    return 0;
}
