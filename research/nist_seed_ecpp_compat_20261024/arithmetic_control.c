#include <stdio.h>
#include <stdlib.h>
#include "BigNum.h"
#include "BigZ.h"

int main(void) {
    BigZ a, b, sum, product;
    char *s, *p;
    printf("ABI int=%u long=%u pointer=%u digit=%u\n",
        (unsigned)sizeof(int), (unsigned)sizeof(long),
        (unsigned)sizeof(void *), (unsigned)sizeof(BigNumDigit));
    if (sizeof(int) != 4 || sizeof(long) != 4 || sizeof(void *) != 4 || sizeof(BigNumDigit) != 4) return 2;
    a = BzFromString("340282366920938463463374607431768211455", 10);
    b = BzFromString("18446744073709551617", 10);
    sum = BzAdd(a, b);
    product = BzMultiply(a, b);
    s = BzToString(sum, 10);
    p = BzToString(product, 10);
    printf("SUM %s\nPRODUCT %s\n", s, p);
    BzFree(a); BzFree(b); BzFree(sum); BzFree(product);
    BzFreeString(s); BzFreeString(p);
    return 0;
}
