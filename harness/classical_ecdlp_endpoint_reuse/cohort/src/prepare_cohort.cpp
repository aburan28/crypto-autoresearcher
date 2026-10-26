#include "common.hpp"
#include <iostream>
#include <set>

// Input preparation only. This program never invokes an ECDLP solver.
namespace {
using lab::I;
using lab::Fixture;
using lab::Point;
constexpr I max_p = (I{1} << 20) - 1;
constexpr I max_r = (I{1} << 19) - 1;
constexpr std::uint64_t max_attempts = 1000000;

struct RootCensus {
 std::vector<I> first;
 I count = 1;
 explicit RootCensus(const lab::Curve& c)
     : first(static_cast<std::size_t>(c.p), -1) {
  std::vector<unsigned char> multiplicity(static_cast<std::size_t>(c.p));
  for (I y = 0; y < c.p; ++y) {
   const auto index = static_cast<std::size_t>(c.mod(y * y));
   if (first[index] < 0) first[index] = y;
   ++multiplicity[index];
  }
  for (I x = 0; x < c.p; ++x)
   count += multiplicity[static_cast<std::size_t>(c.mod(x*x*x+c.a*x+c.b))];
 }
};

I euler_census(const lab::Curve& c) {
 I count = 1;
 for (I x = 0; x < c.p; ++x) {
  const I rhs = c.mod(x*x*x+c.a*x+c.b);
  if (rhs == 0) ++count;
  else if (c.pow(rhs, (c.p-1)/2) == 1) count += 2;
 }
 return count;
}

I selected_factor(I n, unsigned target_bits) {
 I selected = 0, remaining = n;
 auto consider = [&](I q) {
  if (lab::bits(static_cast<std::uint64_t>(q)) == target_bits &&
      lab::prime(q) && std::gcd(n/q,q) == 1 && n/q >= 1 && n/q <= 3)
   selected = std::max(selected,q);
 };
 for (I d = 2; d <= remaining/d; ++d) if (remaining % d == 0) {
  consider(d);
  while (remaining % d == 0) remaining /= d;
 }
 if (remaining > 1) consider(remaining);
 return selected;
}

void certificate(const Fixture& f) {
 const auto& c = f.c;
 lab::require(c.p > 3 && c.p <= max_p && lab::prime(c.p), "bad field");
 lab::require(c.a > 0 && c.a < c.p && c.b > 0 && c.b < c.p,
              "special-j or noncanonical coefficients");
 lab::require(c.mod(4*c.a*c.a*c.a+27*c.b*c.b) != 0, "singular curve");
 lab::require(f.r > 2 && f.r <= max_r && lab::prime(f.r) && f.r != c.p,
              "bad prime subgroup");
 lab::require(f.N > 0 && f.N % f.r == 0 && f.N/f.r >= 1 && f.N/f.r <= 3 &&
              std::gcd(f.N/f.r,f.r) == 1, "bad cofactor");
 lab::require(f.N != c.p && f.N != c.p+1, "anomalous or supersingular");
 const I trace = c.p+1-f.N;
 lab::require(trace*trace <= 4*c.p, "Hasse bound");
 lab::require(!f.P.inf && c.valid(f.P) &&
              c.mul(f.P,static_cast<std::uint64_t>(f.r)).inf,
              "base point order certificate fails");
}

void self_test() {
 // Fixed hand-selected conformance fixtures, not a sampled study or sweep.
 const std::vector<Fixture> fixtures{
  {"fixed17","ordinary",{17,2,2},{5,1,false},19,19,1},
  {"fixed37","ordinary",{37,29,3},{30,30,false},17,34,2},
  {"fixed61","ordinary",{61,1,4},{41,55,false},19,57,3},
  {"fixed127","ordinary",{127,13,45},{26,68,false},41,123,4}};
 for (const auto& f : fixtures) {
  certificate(f);
  lab::require(RootCensus(f.c).count == f.N, "root census conformance");
  lab::require(euler_census(f.c) == f.N, "Euler census conformance");
  lab::require(f.c.mul(f.P,0).inf, "zero scalar");
  lab::require(f.c.mul(f.P,1) == f.P, "unit scalar");
  lab::require(f.c.mul(f.P,static_cast<std::uint64_t>(f.r-1)) == f.c.neg(f.P),
               "minus-one scalar");
 }
 lab::require(selected_factor(34,5) == 17 && selected_factor(57,5) == 19 &&
              selected_factor(123,6) == 41, "factor selector");
 lab::require(selected_factor(49,3) == 0, "noncoprime cofactor rejected");
 std::cout << "{\"kind\":\"fixed_input_generator_conformance\",\"passed\":true}\n";
}

void refuse_existing(const std::string& path) {
 std::ifstream in(path);
 lab::require(!in.good(), "refuse existing preparation output");
}

void generate(const std::string& fixture_path, const std::string& history_path,
              const std::string& exclude_path, std::uint64_t curve_seed) {
 refuse_existing(fixture_path);
 refuse_existing(history_path);
 std::set<std::tuple<I,I,I>> used;
 std::ifstream excluded(exclude_path);
 lab::require(bool(excluded), "cannot read exclusion union");
 std::string line;
 while (std::getline(excluded,line)) {
  if (line.empty() || line.rfind("p\t",0) == 0) continue;
  std::istringstream row(line);
  I p=0,a=0,b=0;
  row >> p >> a >> b;
  lab::require(!row.fail(), "bad exclusion row");
  used.emplace(p,a,b);
 }
 lab::require(used.size() == 114, "expected all 114 historical curve models");
 std::ofstream out(fixture_path), hist(history_path);
 lab::require(bool(out) && bool(hist), "cannot create preparation outputs");
 out << "fixture_id\tstratum\tp\ta\tb\tgx\tgy\tr\tN\tseed\n";
 lab::RNG rng(curve_seed);
 std::uint64_t attempt = 0;
 unsigned accepted = 0;
 for (unsigned bits : {12U,14U,16U,18U}) for (unsigned index=0; index<16;) {
  lab::require(attempt < max_attempts, "input search operational limit");
  const auto seed = rng.next();
  lab::RNG draw(seed);
  const I lo = I{1} << (bits-1), hi = I{1} << (bits+1);
  I p = lo+static_cast<I>(draw.bounded(static_cast<std::uint64_t>(hi-lo)));
  if (p % 2 == 0) ++p;
  while (p < hi && !lab::prime(p)) p += 2;
  Fixture f;
  f.seed=seed; f.stratum="ordinary"; f.c.p=p;
  std::string reason;
  if (p >= hi || p <= 3 || p > max_p) reason="range";
  else {
   f.c.a=1+static_cast<I>(draw.bounded(static_cast<std::uint64_t>(p-1)));
   f.c.b=1+static_cast<I>(draw.bounded(static_cast<std::uint64_t>(p-1)));
   if (used.contains({p,f.c.a,f.c.b})) reason="excluded_or_duplicate";
   else if (f.c.mod(4*f.c.a*f.c.a*f.c.a+27*f.c.b*f.c.b) == 0)
    reason="singular";
   else {
    const RootCensus roots(f.c);
    f.N=roots.count;
    if (f.N == p || f.N == p+1) reason="anomalous_or_trace_zero";
    else {
     f.r=selected_factor(f.N,bits);
     if (f.r == 0 || f.r == p) reason="subgroup_or_cofactor";
     else {
      for (I x=0; x<p; ++x) {
       const I y=roots.first[static_cast<std::size_t>(f.c.mod(x*x*x+f.c.a*x+f.c.b))];
       if (y < 0) continue;
       const Point q=f.c.mul({x,y,false},static_cast<std::uint64_t>(f.N/f.r));
       if (!q.inf) { f.P=q; break; }
      }
      if (f.P.inf) reason="cofactor_zero";
      else {
       f.id="er-r"+std::to_string(bits)+"-"+std::to_string(index);
       certificate(f);
       lab::require(euler_census(f.c) == f.N, "independent C++ census mismatch");
       out << f.id << "\tordinary\t" << p << '\t' << f.c.a << '\t' << f.c.b
           << '\t' << f.P.x << '\t' << f.P.y << '\t' << f.r << '\t' << f.N
           << '\t' << seed << '\n';
       used.emplace(p,f.c.a,f.c.b);
       ++index; ++accepted; reason="accepted";
      }
     }
    }
   }
  }
  ++attempt;
  hist << "{\"attempt\":" << attempt << ",\"bits\":" << bits
       << ",\"seed\":" << seed << ",\"p\":" << p << ",\"a\":" << f.c.a
       << ",\"b\":" << f.c.b << ",\"N\":" << f.N << ",\"r\":" << f.r
       << ",\"outcome\":" << lab::json_quote(reason) << "}\n";
 }
 lab::require(accepted == 64, "incomplete fixture cohort");
 std::cout << "{\"scope\":\"input_preparation_only\",\"fixtures\":64,"
              "\"scientific_solver_measurement_performed\":false}\n";
}
}

int main(int argc,char** argv) {
 try {
  lab::require(argc >= 2, "expected --self-test or --curves");
  const std::string mode=argv[1];
  if (mode == "--self-test") {
   lab::require(argc == 2, "bad conformance arguments");
   self_test();
  } else if (mode == "--curves") {
   lab::require(argc == 6, "usage: --curves FIXTURES HISTORY EXCLUSIONS CURVE_SEED_DECIMAL");
   std::size_t used=0;
   const auto seed=std::stoull(argv[5],&used);
   lab::require(used == std::string(argv[5]).size(), "invalid curve seed");
   generate(argv[2],argv[3],argv[4],seed);
  } else throw std::runtime_error("unknown preparation mode");
 } catch (const std::exception& e) {
  std::cerr << e.what() << '\n';
  return 1;
 }
}
