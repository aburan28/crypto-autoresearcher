#!/usr/bin/python
""" generate interpolation coefficients and program codes """
import sys
import random
import json
from pathlib import Path

inf = float("inf")
indent = " " * 4

class F:
    q = 31
    def __init__(self, n):
        assert n is not None
        if type(n) == F:
            self.n = n.n
        else:
            self.n = n
        self.n %= F.q
        if self.n < 0:
            self.n += F.q
    def __add__(self, other):
        return F(self.n + F(other).n)
    def __sub__(self, other):
        return F(self.n - F(other).n)
    def __mul__(self, other):
        return F(self.n * F(other).n)
    def __truediv__(self, other):
        return F(self.n * F.inv(other))
    def __radd__(self, other):
        return F(F(other).n + self.n)
    def __rsub__(self, other):
        return F(F(other).n - self.n)
    def __rmul__(self, other):
        return F(F(other).n * self.n)
    def __rtruediv__(self, other):
        return F(F(other).n * F.inv(self))
    def __int__(self):
        return self.n
    @classmethod
    def inv(cls, n):
        return F(pow(F(n).n, -1, F.q))
    @classmethod
    def pow(cls, n, k):
        return F(pow(F(n).n, k, F.q))
    @classmethod
    def rand(cls):
        return F(random.randrange(F.q))
    def __str__(self):
        return f"F({self.n})"
    def __repr__(self):
        return f"F({self.n})"
    def __eq__(self, other):
        return self.n == F(other).n

def qruov_set_params(q, ell):
    global QRUOV_q, QRUOV_L, QRUOV_fc, QRUOV_fe, QRUOV_fc0
    if q == 7 and ell == 10:
        QRUOV_q = F.q = 7
        QRUOV_L = 10
        QRUOV_fc = 2
        QRUOV_fe = 1
        QRUOV_fc0 = 1
    elif q == 31 and ell == 3:
        QRUOV_q = F.q = 31
        QRUOV_L = 3
        QRUOV_fc = 1
        QRUOV_fe = 1
        QRUOV_fc0 = 1
    elif q == 31 and ell == 10:
        QRUOV_q = F.q = 31
        QRUOV_L = 10
        QRUOV_fc = 5
        QRUOV_fe = 3
        QRUOV_fc0 = 1
    elif q == 127 and ell == 3:
        QRUOV_q = F.q = 127
        QRUOV_L = 3
        QRUOV_fc = 1
        QRUOV_fe = 1
        QRUOV_fc0 = 1
    elif q == 127 and ell == 10:
        QRUOV_q = F.q = 127
        QRUOV_L = 10
        QRUOV_fc = 2
        QRUOV_fe = 3
        QRUOV_fc0 = 1
    else:
        raise ValueError
qruov_set_params(31, 3)

def Fmat(mat):
    a = len(mat)
    b = len(mat[0])
    ans = [[None for j in range(b)] for i in range(a)]
    for i in range(a):
        for j in range(b):
            ans[i][j] = F(mat[i][j])
    return ans

def Nmat(mat):
    a = len(mat)
    b = len(mat[0])
    ans = [[None for j in range(b)] for i in range(a)]
    for i in range(a):
        for j in range(b):
            assert type(mat[i][j]) == F
            ans[i][j] = mat[i][j].n
    return ans


def matrix_mul(mat_x, mat_y):
    a = len(mat_x)
    b = len(mat_x[0])
    assert b == len(mat_y)
    c = len(mat_y[0])
    ans = [[F(0) for j in range(c)] for i in range(a)]
    for i in range(a):
        for j in range(c):
            for k in range(b):
                ans[i][j] += mat_x[i][k] * mat_y[k][j]
    return ans

def matrix_inv(mat):
    n = len(mat)
    assert len(mat[0]) == n
    augmented_mat = [mat[i] + [F(0) for j in range(n)] for i in range(n)]
    for i in range(n):
        augmented_mat[i][n + i] = F(1)
    for i in range(n):
        pivot = augmented_mat[i][i]
        if pivot == F(0):
            for j in range(i + 1, n):
                if augmented_mat[j][i] != 0:
                    augmented_mat[i], augmented_mat[j] = augmented_mat[j], augmented_mat[i]
                    pivot = augmented_mat[i][i]
                    break
            else:
                raise ValueError("singular")
        inv_pivot = F.inv(pivot)
        augmented_mat[i] = [elem * inv_pivot for elem in augmented_mat[i]]
        for j in range(n):
            if j != i and augmented_mat[j][i] != 0:
                factor = augmented_mat[j][i]
                augmented_mat[j] = [augmented_mat[j][k] - factor * augmented_mat[i][k] for k in range(2*n)]
    return [row[n:] for row in augmented_mat]

def column_vec(L):
    return [[item] for item in L]

def gen_identity_mat(n):
    M = [[0] * n for i in range(n)]
    for i in range(n):
        M[i][i] = 1
    return M

def gen_eval_mat(L, n):
    M = []
    for i in L:
        if i == inf:
            M.append([F(0) for i in range(n-1)] + [F(1)])
        else:
            M.append([F.pow(i, k) for k in range(n)])
    return M

def strc(item):
    if isinstance(item, F) or isinstance(item, int):
        return str(item)
    elif isinstance(item, list) and not isinstance(item[0], list):
        return "{" + ", ".join(strc(val) for val in item) + "}"
    elif isinstance(item, list):
        return "{\n" + ",\n".join(strc(val) for val in item) + "\n}\n"

def polymul(f, g):
    ans = [0] * (len(f) + len(g) - 1)
    for i in range(len(f)):
        for j in range(len(g)):
            ans[i + j] += f[i] * g[j]
    return ans

def polyreduce(f):
    z = list(f)
    for i in range(len(f) - 1, QRUOV_L - 1, -1):
        z[i - QRUOV_L] += QRUOV_fc0 * z[i]
        z[i - QRUOV_L + QRUOV_fe] += QRUOV_fc * z[i]
    return z[:QRUOV_L]

def test_karatsuba(A, B):
    n = len(A[0])
    k = len(A)
    assert len(B[0]) == len(A) == k
    assert len(B) == n * 2 - 1
    for i in range(100):
        f = [F.rand() for i in range(n)]
        g = [F.rand() for i in range(n)]
        fg = polymul(f, g)
        Af = matrix_mul(A, column_vec(f))
        Ag = matrix_mul(A, column_vec(g))
        AfAg = [[Af[i][0] * Ag[i][0]] for i in range(k)]
        Bx = matrix_mul(B, AfAg)
        assert column_vec(fg) == Bx

def flat(ary):
    ans = []
    for item in ary:
        if type(item) is list:
            ans.extend(flat(item))
        else:
            ans.append(item)
    return ans

def reduce_coeff():
    result = [[F(0) for j in range(2 * QRUOV_L - 1)] for i in range(2 * QRUOV_L - 1)]
    for i in range(2 * QRUOV_L - 1):
        result[i][i] = F(1)
    for i in range(2 * QRUOV_L - 2, QRUOV_L - 1, -1):
        for j in range(2 * QRUOV_L - 1):
            result[i - QRUOV_L][j]            += QRUOV_fc0 * result[i][j]
            result[i - QRUOV_L + QRUOV_fe][j] += QRUOV_fc * result[i][j]
    return result[:QRUOV_L]

def calc_q31L3():
    qruov_set_params(31, 3)
    M = gen_eval_mat([0, 1, -1, 2, inf], 5)
    A = gen_eval_mat([0, 1, -1, 2, inf], 3)
    B = matrix_inv(M)
    test_karatsuba(A, B)
    C = matrix_mul(reduce_coeff(), B)
    D = matrix_mul(A, C)
    return Nmat(A), Nmat(C), Nmat(D)

def calc_q31L10():
    qruov_set_params(31, 10)
    M = gen_eval_mat([0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7, 8, -8, 9, inf], 19)
    A = gen_eval_mat([0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7, 8, -8, 9, inf], 10)
    B = matrix_inv(M)
    test_karatsuba(A, B)
    C = matrix_mul(reduce_coeff(), B)
    D = matrix_mul(A, C)
    return Nmat(A), Nmat(C), Nmat(D)

def load_q7L10_23():
    qruov_set_params(7, 10)

    def _expect_matrix(obj, key, rows, cols):
        if key not in obj:
            raise KeyError(f"missing key in pack.json: {key}")
        mat = obj[key]
        if not isinstance(mat, list) or len(mat) != rows:
            raise ValueError(f"{key} must be a {rows}x{cols} matrix")
        for row in mat:
            if not isinstance(row, list) or len(row) != cols:
                raise ValueError(f"{key} must be a {rows}x{cols} matrix")
        return mat

    pack_path = Path(__file__).resolve().parent / "pack.json"
    with pack_path.open("r", encoding="utf-8") as f:
        obj = json.load(f)

    G = Fmat(_expect_matrix(obj, "G_eval_23x10", 23, 10))
    U = Fmat(_expect_matrix(obj, "U_interp_10x23", 10, 23))
    GU = matrix_mul(G, U)
    return Nmat(G), Nmat(U), Nmat(GU)

def calc_q127L3():
    qruov_set_params(127, 3)
    M = gen_eval_mat([0, 1, -1, 2, inf], 5)
    A = gen_eval_mat([0, 1, -1, 2, inf], 3)
    B = matrix_inv(M)
    test_karatsuba(A, B)
    C = matrix_mul(reduce_coeff(), B)
    D = matrix_mul(A, C)
    return Nmat(A), Nmat(C), Nmat(D)

def calc_q127L10():
    qruov_set_params(127, 10)
    points = [0, 1, -1, 2, -2, 3, -3, 4, -4, 5, -5, 6, -6, 7, -7, 8, -8, 9, inf]
    M = gen_eval_mat(points, 19)
    A = gen_eval_mat(points, 10)
    B = matrix_inv(M)
    test_karatsuba(A, B)
    C = matrix_mul(reduce_coeff(), B)
    D = matrix_mul(A, C)
    return Nmat(A), Nmat(C), Nmat(D)

def define_c_array(type, name, ary, static=False):
    storage = "static " if static else ""
    print(f"{storage}const {type} {name}[] = " + strc(ary) + ";")

def param_suffix(q, L):
    return f"q{q}L{L}"

def define_transform_embed_avx2(name, mat):
    a = len(mat[0])
    b = len(mat)
    print(f"""void {name}(uint8_t *output, int plane_out, const uint8_t *input, int plane_in, int size)
{{
    assert(size >= 16);
    for (int i = 0; i < size; i += 16) {{
        const int offset = (i + 15) < size ? i : (size - 16);""")
    for l in range(a):
        print(indent*2 + f"const __m256i y_{l} = _mm256_cvtepu8_epi16(_mm_loadu_si128((__m128i*)&input[{l} * plane_in + offset]));")
    for k in range(b):
        print(indent*2 + f"__m256i val_{k} = _mm256_setzero_si256();")
    maxval = [0] * b
    for k in range(b):
        for l in range(a):
            print(indent*2 + f"val_{k} = _mm256_add_epi16(val_{k}, _mm256_mullo_epi16(_mm256_set1_epi16({mat[k][l]}), y_{l}));")
            maxval[k] += mat[k][l] * (QRUOV_q - 1)
    for k in range(b):
        assert maxval[k] < 2 ** 16
        if maxval[k] >= 2 ** 15:
            print(indent*2 + f"val_{k} = ymm_modq_epi15(ymm_reduceq_epi16(val_{k}));")
        elif maxval[k] >= QRUOV_q:
            print(indent*2 + f"val_{k} = ymm_modq_epi15(val_{k});")
        print(indent*2 + f"_mm_storeu_si128((__m128i*)&output[{k} * plane_out + offset], ymm_cvtusepi16_epi8(val_{k}));")
    print("    }\n}")

def define_transform_embed_q127(name, mat):
    a = len(mat[0])
    b = len(mat)
    print(f"""void {name}(uint8_t *output, int plane_out, const uint8_t *input, int plane_in, int size)
{{
    assert(size >= 16);
    for (int i = 0; i < size; i += 16) {{
        const int offset = (i + 15) < size ? i : (size - 16);""")
    for l in range(a):
        print(indent*2 + f"const __m256i y_{l} = _mm256_cvtepu8_epi16(_mm_loadu_si128((__m128i*)&input[{l} * plane_in + offset]));")
    for k in range(b):
        print(indent*2 + "{")
        print(indent*3 + "__m256i val = _mm256_setzero_si256();")
        maxval = 0
        half_reduce_max = 4 * QRUOV_q + 1
        for l in range(a):
            coeff = mat[k][l]
            if coeff == 0:
                continue
            termmax = coeff * (QRUOV_q - 1)
            if maxval + termmax >= 2 ** 15:
                print(indent*3 + "val = ymm_reduce127_epi16(val);")
                maxval = half_reduce_max
            if coeff == 1:
                print(indent*3 + f"val = _mm256_add_epi16(val, y_{l});")
            else:
                print(indent*3 + f"val = _mm256_add_epi16(val, _mm256_mullo_epi16(_mm256_set1_epi16({coeff}), y_{l}));")
            maxval += termmax
        if maxval >= QRUOV_q:
            print(indent*3 + "val = ymm_mod127_epi15(val);")
        print(indent*3 + f"_mm_storeu_si128((__m128i*)&output[{k} * plane_out + offset], ymm_cvtusepi16_epi8(val));")
        print(indent*2 + "}")
    print("    }\n}")

def define_transform_embed_q7(name, mat):
    a = len(mat[0])
    b = len(mat)
    print(f"""void {name}(uint8_t *output, int plane_out, const uint8_t *input, int plane_in, int size)
{{
    assert(size >= 32);
    for (int i = 0; i < size; i += 32) {{
        const int offset = (i + 31) < size ? i : (size - 32);""")
    for l in range(a):
        print(indent*2 + f"const __m256i y_{l} = _mm256_loadu_si256((__m256i*)&input[{l} * plane_in + offset]);")
    for k in range(b):
        print(indent*2 + "{")
        counter = [0] * 7
        for t in range(1, 7):
            print(indent*3 + f"__m256i val_{k}_{t} = _mm256_setzero_si256();")
            for l in range(a):
                if mat[k][l] == t:
                    print(indent*3 + f"val_{k}_{t} = _mm256_add_epi8(val_{k}_{t}, y_{l});")
                    counter[t] += 1
        positive = (counter[1] + 2*counter[2] + 3*counter[3]) * (QRUOV_q - 1)
        negative = (3*counter[4] + 2*counter[5] + counter[6]) * (QRUOV_q - 1)
        assert positive < 256
        assert negative < 256
        print(indent*3 + f"__m256i val_{k}_23 = _mm256_add_epi8(val_{k}_2, val_{k}_3);")
        print(indent*3 + f"__m256i val_{k}_45 = _mm256_add_epi8(val_{k}_4, val_{k}_5);")
        print(indent*3 + f"__m256i val_{k} = _mm256_add_epi8(val_{k}_1, _mm256_add_epi8(val_{k}_23, _mm256_add_epi8(val_{k}_23, val_{k}_3)));")
        if positive >= 127:
            print(indent*3 + f"val_{k} = ymm_fold126_epi8(val_{k});")
        print(indent*3 + f"__m256i val_{k}_neg = _mm256_add_epi8(val_{k}_6, _mm256_add_epi8(val_{k}_45, _mm256_add_epi8(val_{k}_45, val_{k}_4)));")
        if negative >= 127:
            print(indent*3 + f"val_{k}_neg = ymm_fold126_epi8(val_{k}_neg);")
        print(indent*3 + f"val_{k} = ymm_sub_bias126_epi8(val_{k}, val_{k}_neg);")
        print(indent*3 + f"val_{k} = ymm_mod7_epi8(val_{k});")
        print(indent*3 + f"_mm256_storeu_si256((__m256i*)&output[{k} * plane_out + offset], val_{k});")
        print(indent*2 + "}")
    print("    }\n}")

def define_transform_embed_q31(name, mat):
    a = len(mat[0])
    b = len(mat)
    print(f"""void {name}(uint8_t *output, int plane_out, const uint8_t *input, int plane_in, int size)
{{
    assert(size >= 32);
    for (int i = 0; i < size; i += 32) {{
        const int offset = (i + 31) < size ? i : (size - 32);""")
    for l in range(a):
        print(indent*2 + f"const __m256i y_{l} = _mm256_loadu_si256((__m256i*)&input[{l} * plane_in + offset]);")
    for k in range(b):
        print(indent*2 + "{")
        print(indent*3 + "__m256i val = _mm256_setzero_si256();")
        valmax = 0
        for t in reversed(range(5)): # 2^t
            for l in range(a):
                if mat[k][l] & (1 << t):
                    if valmax + 30 < 256:
                        print(indent*3 + f"val = _mm256_add_epi8(val, y_{l});")
                        valmax += 30
                    else:
                        print(indent*3 + "val = ymm_fold124_epi8(val);")
                        valmax = max(123, valmax - 124)
                        print(indent*3 + f"val = _mm256_add_epi8(val, y_{l});")
                        valmax += 30
            if t != 0:
                if valmax == 0:
                    pass
                elif valmax * 2 < 256:
                    print(indent*3 + "val = _mm256_add_epi8(val, val);")
                    valmax *= 2
                else:
                    print(indent*3 + "val = ymm_approx_mul2_q31_epi8(val);")
                    valmax = (0x0F << 1) + ((valmax & 0xF0) >> 4)
        if valmax > 30:
            print(indent*3 + "val = ymm_mod31_epi8(val);")
        print(indent*3 + f"_mm256_storeu_si256((__m256i*)&output[{k} * plane_out + offset], val);")
        print(indent*2 + "}")
    print("    }\n}")

def define_transform_embed_scalar(name, mat):
    rows = len(mat)
    cols = len(mat[0])
    print(f"""void {name}(uint8_t *output, int plane_out, const uint8_t *input, int plane_in, int size)
{{
    for (int i = 0; i < size; i++) {{""")
    for r in range(rows):
        print(indent * 2 + "{")
        print(indent * 3 + "int val = 0;")
        for c in range(cols):
            coeff = mat[r][c]
            if coeff == 0:
                continue
            term = f"(int)input[{c} * plane_in + i]"
            if coeff == 1:
                print(indent * 3 + f"val += {term};")
            else:
                print(indent * 3 + f"val += {coeff} * {term};")
        print(indent * 3 + f"output[{r} * plane_out + i] = (uint8_t)(val % QRUOV_q);")
        print(indent * 2 + "}")
    print("    }\n}")

def define_mat(q, L, E, I, R, static=False):
    qruov_set_params(q, L)
    define_c_array("int", "MAT_EVAL", flat(E), static=static)
    define_c_array("int", "MAT_INTERP", flat(I), static=static)
    define_c_array("int", "MAT_REEVAL", flat(R), static=static)

def define_mat_avx2(q, L, E, I, R):
    qruov_set_params(q, L)
    suffix = param_suffix(q, L)
    if not ((q == 31 and L == 3) or (q == 127 and L == 3) or (q == 31 and L == 10)):
        define_transform_embed_avx2(f"evaluate_avx2_{suffix}", E)
    define_transform_embed_avx2(f"interpolate_avx2_{suffix}", I)
    define_transform_embed_avx2(f"reevaluate_avx2_{suffix}", R)

def define_mat_q7(q, L, E, I, R):
    qruov_set_params(q, L)
    suffix = param_suffix(q, L)
    define_transform_embed_q7(f"evaluate_q7_{suffix}", E)
    define_transform_embed_q7(f"interpolate_q7_{suffix}", I)
    define_transform_embed_q7(f"reevaluate_q7_{suffix}", R)

def define_mat_q31(q, L, E, I, R):
    qruov_set_params(q, L)
    suffix = param_suffix(q, L)
    if q != 31 or L not in (3, 10):
        define_transform_embed_q31(f"evaluate_q31_{suffix}", E)
    define_transform_embed_q31(f"interpolate_q31_{suffix}", I)
    define_transform_embed_q31(f"reevaluate_q31_{suffix}", R)

def test_mat(q, L, E, I, R):
    qruov_set_params(q, L)
    LL = len(E)
    assert len(E[0]) == L
    assert len(E) == LL
    assert len(I[0]) == LL
    assert len(I) == L
    assert len(R) == LL
    assert len(R[0]) == LL
    for i in range(100):
        f = [F.rand() for i in range(L)]
        g = [F.rand() for i in range(L)]
        fg = polyreduce(polymul(f, g))
        Af = matrix_mul(E, column_vec(f))
        Ag = matrix_mul(E, column_vec(g))
        AfAg = [[Af[i][0] * Ag[i][0]] for i in range(LL)]
        Bx = matrix_mul(I, AfAg)
        assert column_vec(fg) == Bx

def main(target):
    E31L3,  I31L3,  R31L3  = calc_q31L3()
    test_mat(31, 3, E31L3, I31L3, R31L3)
    E31L10, I31L10, R31L10 = calc_q31L10()
    test_mat(31, 10, E31L10, I31L10, R31L10)
    E7L10,  I7L10,  R7L10  = load_q7L10_23()
    test_mat(7, 10, E7L10, I7L10, R7L10)
    E127L3, I127L3, R127L3 = calc_q127L3()
    test_mat(127, 3, E127L3, I127L3, R127L3)
    E127L10, I127L10, R127L10 = calc_q127L10()
    test_mat(127, 10, E127L10, I127L10, R127L10)

    if target == "avx2-matrix.c" or target == "opt-matrix.c":
        print("// auto generated by genmat.py")
        print('#include "emi_transform.h"')
        print("#if QRUOV_q == 31 && QRUOV_L == 3")
        define_mat(31, 3, E31L3, I31L3, R31L3)
        print("#elif QRUOV_q == 127 && QRUOV_L == 3")
        define_mat(127, 3, E127L3, I127L3, R127L3)
        print("#elif QRUOV_q == 31 && QRUOV_L == 10")
        define_mat(31, 10, E31L10, I31L10, R31L10)
        print("#elif QRUOV_q == 7 && QRUOV_L == 10")
        define_mat(7, 10, E7L10, I7L10, R7L10)
        print("#elif QRUOV_q == 127 && QRUOV_L == 10")
        define_mat(127, 10, E127L10, I127L10, R127L10)
        print("#endif")
    elif target == "avx2-transform_gen.c":
        print("// auto generated by genmat.py")
        print("#include <stdint.h>")
        print("#include <assert.h>")
        print('#include "emi_transform.h"')
        print('#include "qruov_simd.h"')
        print()
        print("#if QRUOV_q == 7")
        print("static inline __m256i ymm_fold126_epi8(__m256i x)")
        print("{")
        print(indent + "return _mm256_min_epu8(x, _mm256_sub_epi8(x, _mm256_set1_epi8(126)));")
        print("}")
        print("static inline __m256i ymm_sub_bias126_epi8(__m256i a, __m256i b)")
        print("{")
        print(indent + "return _mm256_add_epi8(a, _mm256_sub_epi8(_mm256_set1_epi8(126), b));")
        print("}")
        print("#endif")
        print("#if QRUOV_q == 31")
        print("static inline __m256i ymm_fold124_epi8(__m256i x)")
        print("{")
        print(indent + "return _mm256_min_epu8(x, _mm256_sub_epi8(x, _mm256_set1_epi8(124)));")
        print("}")
        print("static inline __m256i ymm_approx_mul2_q31_epi8(__m256i x)")
        print("{")
        print(indent + "const __m256i MASK_0F = _mm256_set1_epi8(0x0F);")
        print(indent + "const __m256i MASK_F0 = _mm256_set1_epi8((char)0xF0);")
        print(indent + "return _mm256_add_epi8(_mm256_slli_epi16(_mm256_and_si256(x, MASK_0F), 1),")
        print(indent + "                      _mm256_srli_epi16(_mm256_and_si256(x, MASK_F0), 4));")
        print("}")
        print("#endif")
        print("#if QRUOV_q == 31 && QRUOV_L == 3")
        qruov_set_params(31, 3)
        define_transform_embed_q31("interpolate_q31_q31L3", I31L3)
        define_transform_embed_q31("reevaluate_q31_q31L3", R31L3)
        print("#elif QRUOV_q == 127 && QRUOV_L == 3")
        qruov_set_params(127, 3)
        define_transform_embed_avx2("interpolate_avx2_q127L3", I127L3)
        define_transform_embed_avx2("reevaluate_avx2_q127L3", R127L3)
        print("#elif QRUOV_q == 31 && QRUOV_L == 10")
        qruov_set_params(31, 10)
        define_transform_embed_q31("interpolate_q31_q31L10", I31L10)
        define_transform_embed_q31("reevaluate_q31_q31L10", R31L10)
        print("#elif QRUOV_q == 7 && QRUOV_L == 10")
        qruov_set_params(7, 10)
        define_transform_embed_q7("evaluate_q7_q7L10", E7L10)
        define_transform_embed_q7("interpolate_q7_q7L10", I7L10)
        define_transform_embed_q7("reevaluate_q7_q7L10", R7L10)
        print("#elif QRUOV_q == 127 && QRUOV_L == 10")
        qruov_set_params(127, 10)
        define_transform_embed_q127("interpolate_avx2_q127L10", I127L10)
        define_transform_embed_q127("reevaluate_avx2_q127L10", R127L10)
        print("#endif")
    elif target == "opt-transform_gen.c":
        print("// auto generated by genmat.py")
        print('#include "emi_transform.h"')
        print()
        print("#if QRUOV_q == 31 && QRUOV_L == 3")
        qruov_set_params(31, 3)
        define_transform_embed_scalar("reevaluate_scalar_q31L3", R31L3)
        define_transform_embed_scalar("interpolate_scalar_q31L3", I31L3)
        print("#elif QRUOV_q == 127 && QRUOV_L == 3")
        qruov_set_params(127, 3)
        define_transform_embed_scalar("reevaluate_scalar_q127L3", R127L3)
        define_transform_embed_scalar("interpolate_scalar_q127L3", I127L3)
        print("#elif QRUOV_q == 31 && QRUOV_L == 10")
        qruov_set_params(31, 10)
        define_transform_embed_scalar("reevaluate_scalar_q31L10", R31L10)
        define_transform_embed_scalar("interpolate_scalar_q31L10", I31L10)
        print("#elif QRUOV_q == 7 && QRUOV_L == 10")
        qruov_set_params(7, 10)
        define_transform_embed_scalar("evaluate_scalar_q7L10", E7L10)
        define_transform_embed_scalar("reevaluate_scalar_q7L10", R7L10)
        define_transform_embed_scalar("interpolate_scalar_q7L10", I7L10)
        print("#elif QRUOV_q == 127 && QRUOV_L == 10")
        qruov_set_params(127, 10)
        define_transform_embed_scalar("reevaluate_scalar_q127L10", R127L10)
        define_transform_embed_scalar("interpolate_scalar_q127L10", I127L10)
        print("#endif")
    elif target == "emi_transform.h":
        print("// auto generated by genmat.py")
        print("#ifndef EMI_TRANSFORM_H")
        print("#define EMI_TRANSFORM_H")
        print()
        print('#include "qruov.h"')
        print()
        print("#if QRUOV_q == 31 && QRUOV_L == 3")
        print(f"#define QRUOV_LL {len(E31L3)}")
        print("#elif QRUOV_q == 127 && QRUOV_L == 3")
        print(f"#define QRUOV_LL {len(E127L3)}")
        print("#elif QRUOV_q == 31 && QRUOV_L == 10")
        print(f"#define QRUOV_LL {len(E31L10)}")
        print("#elif QRUOV_q == 7 && QRUOV_L == 10")
        print(f"#define QRUOV_LL {len(E7L10)}")
        print("#elif QRUOV_q == 127 && QRUOV_L == 10")
        print(f"#define QRUOV_LL {len(E127L10)}")
        print("#else")
        print('#error "Unsupported (q, L) for EMI tables"')
        print("#endif")
        print()
        for op in ["evaluate", "reevaluate", "interpolate"]:
            print(f"void {op}(uint8_t *output, int plane_out, const uint8_t *input, int plane_in, int size);")
        print()
        print("#endif // EMI_TRANSFORM_H")
    else:
        raise ValueError(f"Unsupported target: {target}. Use 'avx2-matrix.c', 'avx2-transform_gen.c', 'opt-matrix.c', 'opt-transform_gen.c', or 'emi_transform.h'.")

if __name__ == '__main__':
    main(sys.argv[1])
