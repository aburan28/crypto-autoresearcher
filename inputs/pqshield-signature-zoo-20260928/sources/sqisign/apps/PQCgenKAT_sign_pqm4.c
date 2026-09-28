// pqm4 glue generator

// SPDX-License-Identifier: Apache-2.0 and Unknown

/*
NIST-developed software is provided by NIST as a public service. You may use,
copy, and distribute copies of the software in any medium, provided that you
keep intact this entire notice. You may improve, modify, and create derivative
works of the software or any portion of the software, and you may copy and
distribute such modifications or works. Modified works should carry a notice
stating that you changed the software and should note the date and nature of any
such change. Please explicitly acknowledge the National Institute of Standards
and Technology as the source of the software.

NIST-developed software is expressly provided "AS IS." NIST MAKES NO WARRANTY OF
ANY KIND, EXPRESS, IMPLIED, IN FACT, OR ARISING BY OPERATION OF LAW, INCLUDING,
WITHOUT LIMITATION, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE, NON-INFRINGEMENT, AND DATA ACCURACY. NIST NEITHER REPRESENTS
NOR WARRANTS THAT THE OPERATION OF THE SOFTWARE WILL BE UNINTERRUPTED OR
ERROR-FREE, OR THAT ANY DEFECTS WILL BE CORRECTED. NIST DOES NOT WARRANT OR MAKE
ANY REPRESENTATIONS REGARDING THE USE OF THE SOFTWARE OR THE RESULTS THEREOF,
INCLUDING BUT NOT LIMITED TO THE CORRECTNESS, ACCURACY, RELIABILITY, OR
USEFULNESS OF THE SOFTWARE.

You are solely responsible for determining the appropriateness of using and
distributing the software and you assume all risks associated with its use,
including but not limited to the risks and costs of program errors, compliance
with applicable laws, damage to or loss of data, programs or equipment, and the
unavailability or interruption of operation. This software is not intended to be
used in any situation where a failure could cause risk of injury or damage to
property. The software developed by NIST employees is not subject to copyright
protection within the United States.
*/

#include "api.h"
#include "rng.h"
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define STRINGIFY2(x) #x
#define STRINGIFY(x) STRINGIFY2(x)

#define KAT_SUCCESS 0
#define KAT_FILE_OPEN_ERROR -1
#define KAT_CRYPTO_FAILURE -4

// Message length used by the host self-check below; matches the MLEN of pqm4's test.c/stack.c
#define MSG_LEN 32

void output_header(FILE *fp) {
  const char header[] =
    "// SPDX-License-Identifier: Apache-2.0\n"
    "\n"
    "#ifndef api_h\n"
    "#define api_h\n"
    "\n"
    "#include <stddef.h>\n"
    "#include <sqisign_namespace.h>\n"
    "\n"
    "#define CRYPTO_SECRETKEYBYTES " STRINGIFY(CRYPTO_SECRETKEYBYTES) "\n"
    "#define CRYPTO_PUBLICKEYBYTES " STRINGIFY(CRYPTO_PUBLICKEYBYTES) "\n"
    "#define CRYPTO_BYTES " STRINGIFY(CRYPTO_BYTES) "\n"
    "\n"
    "#define CRYPTO_ALGNAME \"SQIsign_" STRINGIFY(SQISIGN_VARIANT) "\"\n"
    "\n"
    "SQISIGN_API\n"
    "int\n"
    "crypto_sign_keypair(unsigned char *pk, unsigned char *sk);\n"
    "\n"
    "SQISIGN_API\n"
    "int\n"
    "crypto_sign(unsigned char *sm, size_t *smlen,\n"
    "            const unsigned char *m, size_t mlen,\n"
    "            const unsigned char *sk);\n"
    "\n"
    "SQISIGN_API\n"
    "int\n"
    "crypto_sign_open(unsigned char *m, size_t *mlen,\n"
    "                 const unsigned char *sm, size_t smlen,\n"
    "                 const unsigned char *pk);\n"
    "\n"
    "#endif /* api_h */\n";

  fputs(header, fp);
}

void output_rng(FILE *fp) {
  const char rng[] =
    "// SPDX-License-Identifier: Apache-2.0\n"
    "\n"
    "#ifndef rng_h\n"
    "#define rng_h\n"
    "\n"
    "#include \"randombytes.h\"\n"
    "\n"
    "#endif /* rng_h */\n";

  fputs(rng, fp);
}

// Wrappers adapting the scheme's sqisign_* functions (unsigned long long lengths, NIST convention)
// to pqm4's crypto_sign_* API (size_t lengths)
void output_implementation(FILE *fp) {
  const char api[] =
    "// SPDX-License-Identifier: Apache-2.0\n"
    "\n"
    "#include <api.h>\n"
    "#include <encoded_sizes.h>\n"
    "#include <sig.h>\n"
    "\n"
    "// The CRYPTO_* macros in api.h and the sizes in encoded_sizes.h are generated separately. Callers allocate by\n"
    "// the former, while the library checks lengths against the latter, so a mismatch would mean undersized buffers\n"
    "// at runtime.\n"
    "_Static_assert(CRYPTO_BYTES == SIGNATURE_BYTES, \"api.h and encoded_sizes.h disagree on the signature size\");\n"
    "_Static_assert(CRYPTO_PUBLICKEYBYTES == PUBLICKEY_BYTES,\n"
    "               \"api.h and encoded_sizes.h disagree on the public key size\");\n"
    "_Static_assert(CRYPTO_SECRETKEYBYTES == SECRETKEY_BYTES,\n"
    "               \"api.h and encoded_sizes.h disagree on the secret key size\");\n"
    "\n"
    "int crypto_sign_keypair(unsigned char *pk, unsigned char *sk) {\n"
    "  return sqisign_keypair(pk, sk);\n"
    "}\n"
    "\n"
    "int crypto_sign(unsigned char *sm, size_t *smlen, const unsigned char *m,\n"
    "                size_t mlen, const unsigned char *sk) {\n"
    "  unsigned long long smlen_ull = 0;\n"
    "  int ret = sqisign_sign(sm, &smlen_ull, m, mlen, sk);\n"
    "  if (smlen) {\n"
    "    *smlen = smlen_ull;\n"
    "  }\n"
    "  return ret;\n"
    "}\n"
    "\n"
    "int crypto_sign_open(unsigned char *m, size_t *mlen, const unsigned char *sm,\n"
    "                     size_t smlen, const unsigned char *pk) {\n"
    "  unsigned long long mlen_ull = 0;\n"
    "  int ret = sqisign_open(m, &mlen_ull, sm, smlen, pk);\n"
    "  if (mlen) {\n"
    "    *mlen = mlen_ull;\n"
    "  }\n"
    "  return ret;\n"
    "}\n";

  fputs(api, fp);
}

int main(int argc, char **argv) {
  // Output directory for the generated rng.h/api.h/pqm4_api.c
  const char *outdir = "src/pqm4/sqisign_" STRINGIFY(SQISIGN_VARIANT) "/ref";
  char path[1024];
  unsigned char entropy_input[48];
  const unsigned char m[MSG_LEN] = { 0 };
  unsigned char sm[MSG_LEN + CRYPTO_BYTES];
  unsigned char m1[MSG_LEN];
  unsigned long long smlen, mlen1;
  unsigned char pk[CRYPTO_PUBLICKEYBYTES], sk[CRYPTO_SECRETKEYBYTES];
  int ret_val;

  if (argc > 1) {
    outdir = argv[1];
  }

  for (int i = 0; i < 48; i++)
    entropy_input[i] = i;

  randombytes_init(entropy_input, NULL, 256);

  // Self-check: a keypair/sign/open round trip on the host, so that a broken build cannot
  // silently generate the pqm4 glue
  if ((ret_val = crypto_sign_keypair(pk, sk)) != 0) {
    printf("crypto_sign_keypair returned <%d>\n", ret_val);
    return KAT_CRYPTO_FAILURE;
  }

  if ((ret_val = crypto_sign(sm, &smlen, m, MSG_LEN, sk)) != 0) {
    printf("crypto_sign returned <%d>\n", ret_val);
    return KAT_CRYPTO_FAILURE;
  }

  // Fill m1 with random bytes: the message is all-zero, so the memcmp check below could
  // succeed even if crypto_sign_open never wrote to m1
  randombytes(m1, MSG_LEN);

  if ((ret_val = crypto_sign_open(m1, &mlen1, sm, smlen, pk)) != 0) {
    printf("crypto_sign_open returned <%d>\n", ret_val);
    return KAT_CRYPTO_FAILURE;
  }

  if (mlen1 != MSG_LEN) {
    printf("crypto_sign_open returned bad 'mlen': Got <%llu>, expected <%d>\n", mlen1, MSG_LEN);
    return KAT_CRYPTO_FAILURE;
  }

  if (memcmp(m, m1, MSG_LEN)) {
    printf("crypto_sign_open returned bad 'm' value\n");
    return KAT_CRYPTO_FAILURE;
  }

  // Output rng.h
  snprintf(path, sizeof(path), "%s/rng.h", outdir);
  FILE *fp = fopen(path, "w");

  if (!fp) {
    printf("Couldn't open rng.h file for writing. Are you in the correct folder?\n");
    return KAT_FILE_OPEN_ERROR;
  }

  output_rng(fp);

  fclose(fp);

  // Output the header file
  snprintf(path, sizeof(path), "%s/api.h", outdir);
  fp = fopen(path, "w");

  if (!fp) {
    printf("Couldn't open api.h file for writing. Are you in the correct folder?\n");
    return KAT_FILE_OPEN_ERROR;
  }

  output_header(fp);

  fclose(fp);

  // Output the implementation
  snprintf(path, sizeof(path), "%s/pqm4_api.c", outdir);
  fp = fopen(path, "w");

  if (!fp) {
    printf("Couldn't open pqm4_api.c file for writing. Are you in the correct folder?\n");
    return KAT_FILE_OPEN_ERROR;
  }

  output_implementation(fp);

  fclose(fp);

  return KAT_SUCCESS;
}
