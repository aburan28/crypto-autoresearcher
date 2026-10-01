// SPDX-License-Identifier: Apache-2.0

/** @file
 *
 * @brief Known-answer tests for randombytes() against the NIST CAVP SP 800-90A CTR_DRBG vectors.
 *
 * randombytes() in test builds is the NIST-supplied AES-256 CTR_DRBG in src/common/ref/randombytes_ctrdrbg.c, linked
 * through sqisign_common_test. Every KAT in the KAT/ directory is generated with it, so an error here would silently
 * become an error in vectors we publish. This file pins it to an authority.
 *
 * The vectors are transcribed from the CAVS 14.3 SP 800-90A DRBG response files
 * (https://csrc.nist.gov/projects/cryptographic-algorithm-validation-program/random-number-generators), specifically
 * drbgvectors_no_reseed/CTR_DRBG.rsp, section [AES-256 no df], [PredictionResistance = False], [EntropyInputLen = 384],
 * [NonceLen = 0], [AdditionalInputLen = 0], [ReturnedBitsLen = 512]. Fifteen records come from the first
 * [PersonalizationStringLen = 0] group and one from the first [PersonalizationStringLen = 384] group; nothing in the
 * library passes a personalization string, so one record is enough to cover that argument.
 *
 * Because every CAVP record requests exactly 512 bits, the records alone never exercise a request that is not a whole
 * number of AES blocks, a zero-length request, or the boundary between two calls. The checks after the record loop
 * cover those, deriving their expected values from the same vectors.
 */

#include <rng.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

// randombytes_init() copies exactly this many bytes from entropy_input, and the same from personalization_string when
// it is non-NULL. The length is hard-coded there and no header exposes it, so it is restated here: it is what makes the
// [EntropyInputLen = 384] / [PersonalizationStringLen = 384] records the matching ones.
#define DRBG_SEED_BYTES 48

// [ReturnedBitsLen = 512] for every record below
#define DRBG_RETURNED_BYTES 64

typedef struct
{
    const char *name;
    const char *entropy_input; // 2 * DRBG_SEED_BYTES hex chars
    const char *pers;          // 2 * DRBG_SEED_BYTES hex chars, or NULL for an absent personalization string
    const char *returned_bits; // 2 * DRBG_RETURNED_BYTES hex chars
} drbg_kat_t;

// drbgvectors_no_reseed/CTR_DRBG.rsp, [AES-256 no df], [PersonalizationStringLen = 0], COUNT = 0 through 14
static const char v_c0_entropy[] =
    "df5d73faa468649edda33b5cca79b0b05600419ccb7a879ddfec9db32ee494e5531b51de16a30f769262474c73bec010";
static const char v_c0_returned[] = "d1c07cd95af8a7f11012c84ce48bb8cb87189e99d40fccb1771c619bdf82ab22"
                                    "80b1dc2f2581f39164f7ac0c510494b3a43c41b7db17514c87b107ae793e01c5";

static const char v_c1_entropy[] =
    "3b6fb634d35bb386927374f991c1cbc9fafba3a43c432dc411b7b2fa96cfcce8d305e135ff9bc460dbc7ba3990bf8060";
static const char v_c1_returned[] = "083a836fe1cde053164555529409337dc4fec6844594fdf15083ba9d1001eb94"
                                    "5c3b96a1bcee3990e1e51f85c80e9f4e04de34e57b640f6cae8ed68e99624712";

static const char v_c2_entropy[] =
    "0217a8acf2f8e2c4ab7bdcd5a694bca28d038018869dcbe2160d1ce0b4c78ead5592efed98662f2dff87f32f4835c677";
static const char v_c2_returned[] = "aa36779726f52875312507fb084744d4d7f3f9468a5b246ccde316d2ab91879c"
                                    "2e29f5a0938a3bcd722bb718d01bbfc35831c9e64f5b6410ae908d3061f76c84";

static const char v_c3_entropy[] =
    "37d851fb20ab3ba73b1d8d81f323901a55529c26a8f753d32980d6d2aba3da278b907400a19406e255206e1d0858f384";
static const char v_c3_returned[] = "96eabafb45c77967b14a6663a39238306ce58038a3dc0b8aecaf0231c404ecba"
                                    "50f1ab0a17b1894cf6acb630fe165f8a9d7c5412e1bab4eb4efe9ae84f5b4a03";

static const char v_c4_entropy[] =
    "e62eab30b9338593076104ee9c148a6c22f796daedb71bacdda207b19768b5fed5d20c9eea12ed5ab959c143f773cda6";
static const char v_c4_returned[] = "f5ea040c670f83c26ff2c38f66169b572fecc7283e902f0f4b2f6a4440f5b897"
                                    "0807d58ca01466cec7fb68b4cf952355e780050bf48ad5b20c17c78aa0fc0352";

static const char v_c5_entropy[] =
    "6245755cb02ae883911c0d82009035715b2304f78ce2a0d8fa22d47e7e1e394fd9a7a13862ef2393bb3818ec49cb70f2";
static const char v_c5_returned[] = "3cd590a0dfece30940c11ff243d99e552b531ae11b31a454b42ed04f2c77f2e2"
                                    "f58f9bd1cd0a36480f845256bc82723c2de5c6d15bc8be2040e5ae8b5331516e";

static const char v_c6_entropy[] =
    "bc10b0985a1da8d0bcbced029cf52f0fe12b6d6bc500ddffbaf37a2090356cf1aacb1bf30ad948f87f899c544d115716";
static const char v_c6_returned[] = "8575f0f1f959589e2695891dfac56db72b79981c6077de92154c5557c3e89ab7"
                                    "737827069ecc700de18317b5a1fa38c11d675bbb9ba235f153c4f9899bc4bb8f";

static const char v_c7_entropy[] =
    "0398b1bb37f9673a2d88ef418b4cca3d6009950fae93f08095a4960283329ce75312bb21c30d26b0ddfabf296006065c";
static const char v_c7_returned[] = "22816b8c4bcf34f8d54257c217b529cf038b6f6fb1863017a343d50c883696d4"
                                    "43fa76c259daae46a763382bcc289de55b224f8db99d46838c951b3e18a9fc26";

static const char v_c8_entropy[] =
    "4bfa09839da460e5b088411eb312a3c89a858ee88cf3cb2ad4f8f9896bcfcae72fbd28f6bb428811ba34fbe4f8c8f518";
static const char v_c8_returned[] = "46a574ebbd566861757680a5a3a050beca92fa6993ba72bced22bc0a46ed0058"
                                    "4e61db698e352e31c74af4f5711b0aa1d9d41894ffdb9c8837c38b1b3782e381";

static const char v_c9_entropy[] =
    "86d115f1d3a154c50b45562a02c955e307c17febecab4d13e0d5b6c7258b4bfeb91e316ad0f87bbc0ae1d09d4d60d31a";
static const char v_c9_returned[] = "ff0250e026ef966434062c875545bc436605bb5d02877a1bd3fd03ab8752b196"
                                    "3749ea208df53f6c51826434f5c6e6d991845c6154f6b2000de640d030288965";

static const char v_c10_entropy[] =
    "ce4c6c498e5df8b61debfaf1c24c479109c87c7d38782f50bb60877127a5480594428bd7a9fd71fff2fe0d1db3ce6e2f";
static const char v_c10_returned[] = "1389f2a6134235e08e7a0b41c4a1b5fd77bce469fb6845e519ccad385d74649f"
                                     "2207c84488556741d27d6435437ad088d11f52265b882e47642402d1c0882562";

static const char v_c11_entropy[] =
    "c1dad0e376aa2c350e0d89fcd24040992c08c141adc373d4360786a08812d2919329b4f5a5fae4016cb7699b0647edfa";
static const char v_c11_returned[] = "d38991536fb03509531ffae44c7494f05a73030920c2bafd833be1a8c7f6d741"
                                     "6077d0089bb651b96ad964c26f11b31bb0364b4f5e0dc7e11504054b5110211a";

static const char v_c12_entropy[] =
    "75173e81ce87e7c8d0345761ee59a3fd1c555f37f7c236f7e3aaa5f5ddcb8089462e8edbe4e19aec2467684a57716788";
static const char v_c12_returned[] = "58bbc5ce5c2d8b6330c5857a888ee6b3d74b2ba009c8553cc7b8adb51793862e"
                                     "9c9c933959ea73d720786e471dfdd2bed572e25f683dcd6f7e729db0254f74ad";

static const char v_c13_entropy[] =
    "a7c57c5af28a258926838c39ae62194005c93afffe5592a685b150c9de3ccf79c223616674d676517f4bd1a2fc3bd6ec";
static const char v_c13_returned[] = "a0ea3af0cc95103ba3e89e5e4a6b792bfb19eef9580255ed76e71ed0e5325848"
                                     "497d7757eb5cb319475b77926abb6a2bfb4437ccff0c8356c1b5705d85842d93";

static const char v_c14_entropy[] =
    "b7f7e4e68356b2ac2c2c0075c0ef5ec6f5a6f225a18db00830261a95765771eba739a7cf8a1126c58994c43b2d28024a";
static const char v_c14_returned[] = "a15e8cc437a600a51dcfb778afa23d577d0e56b004f56eeb286e6c949d982bdb"
                                     "9353cbc63d33d7d397ceb4fea51a6df0b4d6d4cd32b9065bc4110d790c610e44";

// Same section with [PersonalizationStringLen = 384], COUNT = 0. randombytes_init() XORs the personalization string
// into the entropy input, so this is the only record that covers that argument.
static const char v_pers_entropy[] =
    "22a89ee0e37b54ea636863d9fed10821f1952a428488d528eceb9d2ec69d573ec6216216fb3e8f72a148a5ada9d620b1";
static const char v_pers_pers[] =
    "953c10badcbcd45fb4e5475826477fc137ac96a49ad5005fb14bdaf6468ae7f46c5d0de22d304afc67989615adc2e983";
static const char v_pers_returned[] = "f7fab6a6fcf445f0a0434b2aa0c610bdef5489ecd95414634623add18a9f888b"
                                      "ca6be151312d1b9e8f83bd0acad6234d3bccc11b63a40d6fbff448f67db0b91f";

static const drbg_kat_t drbg_kats[] = {
    {  "nopers/0",   v_c0_entropy,        NULL,   v_c0_returned },
    {  "nopers/1",   v_c1_entropy,        NULL,   v_c1_returned },
    {  "nopers/2",   v_c2_entropy,        NULL,   v_c2_returned },
    {  "nopers/3",   v_c3_entropy,        NULL,   v_c3_returned },
    {  "nopers/4",   v_c4_entropy,        NULL,   v_c4_returned },
    {  "nopers/5",   v_c5_entropy,        NULL,   v_c5_returned },
    {  "nopers/6",   v_c6_entropy,        NULL,   v_c6_returned },
    {  "nopers/7",   v_c7_entropy,        NULL,   v_c7_returned },
    {  "nopers/8",   v_c8_entropy,        NULL,   v_c8_returned },
    {  "nopers/9",   v_c9_entropy,        NULL,   v_c9_returned },
    { "nopers/10",  v_c10_entropy,        NULL,  v_c10_returned },
    { "nopers/11",  v_c11_entropy,        NULL,  v_c11_returned },
    { "nopers/12",  v_c12_entropy,        NULL,  v_c12_returned },
    { "nopers/13",  v_c13_entropy,        NULL,  v_c13_returned },
    { "nopers/14",  v_c14_entropy,        NULL,  v_c14_returned },
    {    "pers/0", v_pers_entropy, v_pers_pers, v_pers_returned },
};

#define DRBG_SECURITY_STRENGTH 256

static int
hex_digit(char c)
{
    if (c >= '0' && c <= '9')
        return c - '0';
    if (c >= 'a' && c <= 'f')
        return c - 'a' + 10;
    if (c >= 'A' && c <= 'F')
        return c - 'A' + 10;
    return -1;
}

// Decodes exactly out_len bytes, rejecting anything else so that a truncated transcription cannot quietly turn a record
// into a test of zero-padded input.
static int
hex_to_bytes(const char *hex, uint8_t *out, size_t out_len)
{
    if (strlen(hex) != 2 * out_len)
        return 0;

    for (size_t i = 0; i < out_len; i++) {
        int hi = hex_digit(hex[2 * i]);
        int lo = hex_digit(hex[2 * i + 1]);

        if (hi < 0 || lo < 0)
            return 0;
        out[i] = (uint8_t)((hi << 4) | lo);
    }

    return 1;
}

static void
print_hex(const char *label, const uint8_t *buf, size_t len)
{
    printf("    %s ", label);
    for (size_t i = 0; i < len; i++)
        printf("%02x", buf[i]);
    printf("\n");
}

// Instantiates the DRBG from a record, i.e. the Instantiate operation of the CAVP procedure.
static int
drbg_instantiate(const drbg_kat_t *kat)
{
    // randombytes_init() takes non-const pointers, hence the local copies
    uint8_t entropy[DRBG_SEED_BYTES];
    uint8_t pers[DRBG_SEED_BYTES];

    if (!hex_to_bytes(kat->entropy_input, entropy, sizeof(entropy))) {
        printf("  FAIL %s: malformed EntropyInput\n", kat->name);
        return 0;
    }
    if (kat->pers != NULL && !hex_to_bytes(kat->pers, pers, sizeof(pers))) {
        printf("  FAIL %s: malformed PersonalizationString\n", kat->name);
        return 0;
    }

    randombytes_init(entropy, kat->pers != NULL ? pers : NULL, DRBG_SECURITY_STRENGTH);

    return 1;
}

// The CAVP procedure for a no-reseed record: instantiate, generate, generate, and compare the second output. The first
// output is discarded, exactly as the response files do.
static int
test_drbg_record(const drbg_kat_t *kat, const char *what)
{
    uint8_t expected[DRBG_RETURNED_BYTES];
    uint8_t got[DRBG_RETURNED_BYTES];

    if (!hex_to_bytes(kat->returned_bits, expected, sizeof(expected))) {
        printf("  FAIL %s/%s: malformed ReturnedBits\n", kat->name, what);
        return 0;
    }
    if (!drbg_instantiate(kat))
        return 0;

    int rc_discarded = randombytes(got, sizeof(got));
    int rc_compared = randombytes(got, sizeof(got));

    if (rc_discarded != 0 || rc_compared != 0) {
        printf("  FAIL %s/%s: randombytes failed\n", kat->name, what);
        return 0;
    }

    if (memcmp(got, expected, sizeof(expected)) != 0) {
        printf("  FAIL %s/%s\n", kat->name, what);
        print_hex("got     ", got, sizeof(got));
        print_hex("expected", expected, sizeof(expected));
        return 0;
    }

    return 1;
}

// A request shorter than ReturnedBitsLen must return a prefix of the same keystream: the generate loop starts from the
// same (Key, V), and the CTR_DRBG_Update that closes a call cannot affect bytes it has already returned. No CAVP record
// requests a length that is not a whole number of AES blocks, so this is the only coverage of the truncating branch of
// randombytes_nist().
static int
test_partial_lengths(const drbg_kat_t *kat)
{
    static const size_t lens[] = { 1, 15, 16, 17, 31, 63, DRBG_RETURNED_BYTES };
    uint8_t expected[DRBG_RETURNED_BYTES];
    int res = 1;

    if (!hex_to_bytes(kat->returned_bits, expected, sizeof(expected))) {
        printf("  FAIL partial-length: malformed ReturnedBits\n");
        return 0;
    }

    for (size_t i = 0; i < sizeof(lens) / sizeof(*lens); i++) {
        uint8_t got[DRBG_RETURNED_BYTES];

        if (!drbg_instantiate(kat))
            return 0;
        if (randombytes(got, sizeof(got)) != 0 || randombytes(got, lens[i]) != 0) {
            printf("  FAIL partial-length/%zu: randombytes failed\n", lens[i]);
            res = 0;
            continue;
        }
        if (memcmp(got, expected, lens[i]) != 0) {
            printf("  FAIL partial-length/%zu\n", lens[i]);
            print_hex("got     ", got, lens[i]);
            print_hex("expected", expected, lens[i]);
            res = 0;
        }
    }

    return res;
}

// A zero-length request must write nothing, yet still advance the state: randombytes_nist() skips the generate loop but
// runs CTR_DRBG_Update unconditionally, so the next request must not return ReturnedBits.
static int
test_zero_length(const drbg_kat_t *kat)
{
    uint8_t expected[DRBG_RETURNED_BYTES];
    uint8_t got[DRBG_RETURNED_BYTES];
    uint8_t canary[DRBG_RETURNED_BYTES];

    if (!hex_to_bytes(kat->returned_bits, expected, sizeof(expected))) {
        printf("  FAIL zero-length: malformed ReturnedBits\n");
        return 0;
    }
    if (!drbg_instantiate(kat))
        return 0;

    memset(canary, 0xa5, sizeof(canary));
    if (randombytes(got, sizeof(got)) != 0 || randombytes(canary, 0) != 0) {
        printf("  FAIL zero-length: randombytes failed\n");
        return 0;
    }

    for (size_t i = 0; i < sizeof(canary); i++) {
        if (canary[i] != 0xa5) {
            printf("  FAIL zero-length: wrote %zu byte(s)\n", sizeof(canary) - i);
            return 0;
        }
    }

    if (randombytes(got, sizeof(got)) != 0) {
        printf("  FAIL zero-length: randombytes failed\n");
        return 0;
    }
    if (memcmp(got, expected, sizeof(expected)) == 0) {
        printf("  FAIL zero-length: state did not advance\n");
        return 0;
    }

    return 1;
}

// The state advances once per call, not once per block, so two half-sized requests must not reproduce the output of one
// full-sized request. Pins the boundary against anyone who later "optimizes" the per-call update away.
static int
test_state_advances_per_call(const drbg_kat_t *kat)
{
    uint8_t expected[DRBG_RETURNED_BYTES];
    uint8_t got[DRBG_RETURNED_BYTES];

    if (!hex_to_bytes(kat->returned_bits, expected, sizeof(expected))) {
        printf("  FAIL per-call-update: malformed ReturnedBits\n");
        return 0;
    }
    if (!drbg_instantiate(kat))
        return 0;

    if (randombytes(got, sizeof(got)) != 0 || randombytes(got, sizeof(got) / 2) != 0 ||
        randombytes(got + sizeof(got) / 2, sizeof(got) / 2) != 0) {
        printf("  FAIL per-call-update: randombytes failed\n");
        return 0;
    }
    if (memcmp(got, expected, sizeof(expected)) == 0) {
        printf("  FAIL per-call-update: two half requests matched one whole request\n");
        return 0;
    }

    return 1;
}

// Passing NULL for the personalization string must equal passing 48 zero bytes, since the XOR at instantiation is a
// no-op either way. Both spellings appear in the tree, and the [PersonalizationStringLen = 0] records only pin NULL.
static int
test_null_personalization(const drbg_kat_t *kat)
{
    uint8_t entropy[DRBG_SEED_BYTES];
    uint8_t zeros[DRBG_SEED_BYTES];
    uint8_t with_null[DRBG_RETURNED_BYTES];
    uint8_t with_zeros[DRBG_RETURNED_BYTES];

    if (!hex_to_bytes(kat->entropy_input, entropy, sizeof(entropy))) {
        printf("  FAIL null-personalization: malformed EntropyInput\n");
        return 0;
    }
    memset(zeros, 0x00, sizeof(zeros));

    randombytes_init(entropy, NULL, DRBG_SECURITY_STRENGTH);
    if (randombytes(with_null, sizeof(with_null)) != 0) {
        printf("  FAIL null-personalization: randombytes failed\n");
        return 0;
    }

    randombytes_init(entropy, zeros, DRBG_SECURITY_STRENGTH);
    if (randombytes(with_zeros, sizeof(with_zeros)) != 0) {
        printf("  FAIL null-personalization: randombytes failed\n");
        return 0;
    }

    if (memcmp(with_null, with_zeros, sizeof(with_null)) != 0) {
        printf("  FAIL null-personalization: NULL differs from 48 zero bytes\n");
        return 0;
    }

    return 1;
}

int
main(void)
{
    int res = 1;

    printf("Running CTR-DRBG known-answer tests\n");

    for (size_t i = 0; i < sizeof(drbg_kats) / sizeof(*drbg_kats); i++)
        res &= test_drbg_record(&drbg_kats[i], "kat");

    res &= test_partial_lengths(&drbg_kats[0]);
    res &= test_zero_length(&drbg_kats[0]);
    res &= test_state_advances_per_call(&drbg_kats[0]);
    res &= test_null_personalization(&drbg_kats[0]);

    // Re-instantiating with a seed already used must reproduce its stream after the state has been driven elsewhere.
    // The loop above relies on this to run more than one record per process; checking it last names the property.
    res &= test_drbg_record(&drbg_kats[0], "reinstantiate");

    if (!res) {
        printf("CTR-DRBG known-answer tests failed\n");
        return 1;
    }

    printf("CTR-DRBG known-answer tests passed\n");

    return 0;
}
