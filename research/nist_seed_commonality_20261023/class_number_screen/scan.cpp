// Exact list membership for ordinary-curve CM fields. Build with GMP.
#include <charconv>
#include <chrono>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>
#include <gmp.h>

struct Row {
  std::string label;
  mpz_t delta_abs;
  unsigned long long divisors = 0;
  unsigned long long hits = 0;
  explicit Row(std::string name, const std::string& hex) : label(std::move(name)) {
    mpz_init(delta_abs);
    if (mpz_set_str(delta_abs, hex.c_str(), 16) != 0 || mpz_sgn(delta_abs) <= 0)
      throw std::runtime_error("invalid positive hex discriminant");
  }
  Row(const Row&) = delete;
  Row& operator=(const Row&) = delete;
  ~Row() { mpz_clear(delta_abs); }
};

static unsigned long long parse_number(const char* first, const char* last) {
  unsigned long long n = 0;
  auto result = std::from_chars(first, last, n);
  if (result.ec != std::errc() || result.ptr != last)
    throw std::runtime_error("invalid integer in class-number list");
  return n;
}

int main(int argc, char** argv) {
  try {
    if (argc != 3) throw std::runtime_error("usage: scan LIST.txt CURVES.tsv");
    std::ifstream curves(argv[2]);
    if (!curves) throw std::runtime_error("could not open curves TSV");
    std::vector<Row*> rows;
    std::string line;
    while (std::getline(curves, line)) {
      std::istringstream s(line);
      std::string label, hex, extra;
      if (!(s >> label >> hex) || (s >> extra)) throw std::runtime_error("malformed curves TSV");
      rows.push_back(new Row(label, hex));
    }
    if (rows.size() != 24) throw std::runtime_error("expected 21 curves plus 3 controls");
    std::ifstream in(argv[1]);
    if (!in) throw std::runtime_error("could not open class-number list");
    mpz_t quotient;
    mpz_init(quotient);
    unsigned long long count = 0, prior = 0;
    auto start = std::chrono::steady_clock::now();
    std::cout << "kind\tlabel\tD\th\tconductor\tdivisors\thits\n";
    while (std::getline(in, line)) {
      const char* b = line.data();
      const char* e = b + line.size();
      const char* sep = b;
      while (sep != e && *sep != ' ') ++sep;
      if (sep == e) throw std::runtime_error("missing class number");
      const char* hstart = sep + 1;
      if (hstart == e) throw std::runtime_error("missing class number");
      const auto d = parse_number(b, sep);
      const auto h = parse_number(hstart, e);
      if (d <= prior || h < 1 || h > 2000 || d > 1062350083ULL)
        throw std::runtime_error("list order, class number, or maximum failed");
      prior = d;
      ++count;
      for (Row* row : rows) {
        if (mpz_fdiv_ui(row->delta_abs, d) != 0) continue;
        ++row->divisors;
        mpz_divexact_ui(quotient, row->delta_abs, d);
        if (!mpz_perfect_square_p(quotient)) continue;
        ++row->hits;
        mpz_sqrt(quotient, quotient);
        char* decimal = mpz_get_str(nullptr, 10, quotient);
        std::cout << "hit\t" << row->label << '\t' << d << '\t' << h
                  << '\t' << decimal << "\t\t\n";
        void (*free_func)(void*, size_t);
        mp_get_memory_functions(nullptr, nullptr, &free_func);
        free_func(decimal, std::char_traits<char>::length(decimal) + 1);
      }
      if (count % 1000000ULL == 0) {
        auto elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
        if (elapsed > 240.0) throw std::runtime_error("comparison loop reached 240-second cap");
        std::cerr << "checked=" << count << " elapsed_seconds=" << elapsed << '\n';
      }
    }
    if (count != 16453493ULL || prior != 1062350083ULL)
      throw std::runtime_error("list count or final discriminant failed");
    for (Row* row : rows)
      std::cout << "summary\t" << row->label << "\t\t\t\t"
                << row->divisors << '\t' << row->hits << '\n';
    auto elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - start).count();
    std::cerr << "complete rows=" << count << " elapsed_seconds=" << elapsed << '\n';
    mpz_clear(quotient);
    for (Row* row : rows) delete row;
    return 0;
  } catch (const std::exception& e) {
    std::cerr << "ERROR: " << e.what() << '\n';
    return 2;
  }
}
