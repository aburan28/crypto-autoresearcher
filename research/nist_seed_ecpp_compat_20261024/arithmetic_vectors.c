#include <stdio.h>
#include <stdlib.h>
#include "BigNum.h"
#include "BigZ.h"

int main(void) {
    char sa[2048], sb[2048];
    unsigned row = 0;
    printf("ABI %u %u %u %u\n", (unsigned)sizeof(int),
        (unsigned)sizeof(long), (unsigned)sizeof(void *), (unsigned)sizeof(BigNumDigit));
    if (sizeof(int) != 4 || sizeof(long) != 4 || sizeof(void *) != 4 || sizeof(BigNumDigit) != 4) return 2;
    while (scanf("%2047s %2047s", sa, sb) == 2) {
        BigZ a = BzFromString(sa, 10), b = BzFromString(sb, 10);
        BigZ values[5], remainder;
        unsigned i;
        values[0] = BzAdd(a, b);
        values[1] = BzSubtract(a, b);
        values[2] = BzMultiply(a, b);
        values[3] = BzDivide(a, b, &remainder);
        values[4] = remainder;
        printf("ROW %u", row++);
        for (i = 0; i < 5; i++) {
            char *value;
            if (!values[i]) return 3;
            value = BzToString(values[i], 10);
            if (!value) return 4;
            printf(" %s", value);
            BzFreeString(value);
            BzFree(values[i]);
        }
        printf("\n");
        BzFree(a); BzFree(b);
    }
    return 0;
}
