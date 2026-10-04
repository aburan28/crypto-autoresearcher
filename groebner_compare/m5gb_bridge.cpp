// Compile this bridge against the separately downloaded upstream M5GB sources.
// Protocol: n, row count, then each row's count and squarefree monomial masks.
// Upstream owns its debug output; only M5GB_RESULT is parsed as a basis.
#include <algorithm>
#include <iostream>
#include <stdexcept>
#include <vector>
#include "other_fct.h"
#include "lab_poly.h"
#include "M5GB.h"

int main() {
  int n, count;
  if (!(std::cin >> n >> count) || n < 1 || n > 9 || count < 1 || count > 256)
    return 2;
  binom_table = Create_binom_table(n + 17, n + 17);
  table = Create_table(n, 15);  // Bounded upstream table parameter d=15.
  std::vector<polynomial> system;
  for (int row = 0; row < count; ++row) {
    int size;
    if (!(std::cin >> size) || size < 1 || size > (1 << n)) return 2;
    std::vector<monomial> poly;
    for (int j = 0; j < size; ++j) {
      int mask;
      if (!(std::cin >> mask) || mask < 0 || mask >= (1 << n)) return 2;
      term_vec exponents(n, 0);
      for (int i = 0; i < n; ++i) exponents[i] = (mask >> i) & 1;
      auto term = term_to_int(exponents, n) - 1;
      if (term < 0 || term >= static_cast<term_int>(table.size())) return 2;
      poly.emplace_back(term, 1, 2);
    }
    std::sort(poly.begin(), poly.end(), [](const monomial& a, const monomial& b) {
      return a.Get_term() > b.Get_term();
    });
    system.emplace_back(poly);
  }
  auto basis = M5GB(system, n);
  std::cout << "M5GB_RESULT " << basis.size();
  for (const auto& row : basis) {
    std::vector<int> masks;
    for (const auto& monomial : row.Get_monomials()) {
      if (monomial.Get_coeff() % 2 == 0) continue;
      const auto& exponents = table.at(monomial.Get_term()).first;
      int mask = 0;
      for (int i = 0; i < n; ++i) {
        // The upstream basis includes x_i^2+x_i. Reduce its output modulo
        // the frozen Boolean field equations before independent certification.
        mask |= (exponents[i] > 0) << i;
      }
      masks.push_back(mask);
    }
    std::cout << ' ' << masks.size();
    for (int mask : masks) std::cout << ' ' << mask;
  }
  std::cout << std::endl;
}
