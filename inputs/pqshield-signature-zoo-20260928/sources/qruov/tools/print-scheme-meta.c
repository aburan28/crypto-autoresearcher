#include <stdio.h>

#include "api.h"
#include "qruov.h"

int main(void)
{
    printf("%d\n", CRYPTO_SECRETKEYBYTES);
    printf("%d\n", CRYPTO_PUBLICKEYBYTES);
    printf("%d\n", CRYPTO_BYTES);
    printf("%s\n", CRYPTO_ALGNAME);

    return 0;
}
