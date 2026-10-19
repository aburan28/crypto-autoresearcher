// Independent ordered-triple count oracle for prepared arity-3 inputs.
// Uses Euclidean inverses and an unordered pair-sum histogram. The collector
// uses Fermat inverses and a sorted pair table of explicit index pairs.
#include <cstdint>
#include <cstdlib>
#include <exception>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <vector>

using u64 = std::uint64_t;
using u128 = unsigned __int128;
using i128 = __int128;

struct Point {
    u64 x = 0;
    u64 y = 0;
    bool infinity = false;
    bool operator==(const Point& other) const {
        return infinity == other.infinity && (infinity || (x == other.x && y == other.y));
    }
};

struct Hash {
    std::size_t operator()(const Point& point) const {
        if (point.infinity) return 0x9e3779b97f4a7c15ULL;
        auto mix = [](u64 value) {
            value += 0x9e3779b97f4a7c15ULL;
            value = (value ^ (value >> 30)) * 0xbf58476d1ce4e5b9ULL;
            value = (value ^ (value >> 27)) * 0x94d049bb133111ebULL;
            return value ^ (value >> 31);
        };
        return static_cast<std::size_t>(mix(point.x) ^ mix(point.y + 0x517cc1b727220a95ULL));
    }
};

struct Curve { u64 p, a, b, r; };
struct Target { u64 alpha, beta; Point point; };

u64 modsum(u64 left, u64 right, u64 modulus) {
    return static_cast<u64>((static_cast<u128>(left) + right) % modulus);
}
u64 modsub(u64 left, u64 right, u64 modulus) {
    return static_cast<u64>((static_cast<u128>(left) + modulus - right) % modulus);
}
u64 modmul(u64 left, u64 right, u64 modulus) {
    return static_cast<u64>((static_cast<u128>(left) * right) % modulus);
}
u64 inverse(u64 value, u64 modulus) {
    i128 old_remainder = modulus, remainder = value;
    i128 old_coeff = 0, coeff = 1;
    while (remainder) {
        i128 quotient = old_remainder / remainder;
        i128 next_remainder = old_remainder - quotient * remainder;
        old_remainder = remainder;
        remainder = next_remainder;
        i128 next_coeff = old_coeff - quotient * coeff;
        old_coeff = coeff;
        coeff = next_coeff;
    }
    if (old_remainder != 1) throw std::runtime_error("noninvertible field element");
    old_coeff %= static_cast<i128>(modulus);
    if (old_coeff < 0) old_coeff += modulus;
    return static_cast<u64>(old_coeff);
}
Point negate(Point point, u64 modulus) {
    if (!point.infinity && point.y) point.y = modulus - point.y;
    return point;
}
Point add(Point left, Point right, const Curve& curve) {
    if (left.infinity) return right;
    if (right.infinity) return left;
    if (left.x == right.x && modsum(left.y, right.y, curve.p) == 0)
        return Point{0, 0, true};
    u64 numerator, denominator;
    if (left == right) {
        numerator = modsum(modmul(3, modmul(left.x, left.x, curve.p), curve.p), curve.a, curve.p);
        denominator = modmul(2, left.y, curve.p);
    } else {
        numerator = modsub(right.y, left.y, curve.p);
        denominator = modsub(right.x, left.x, curve.p);
    }
    u64 slope = modmul(numerator, inverse(denominator, curve.p), curve.p);
    u64 x = modsub(modsub(modmul(slope, slope, curve.p), left.x, curve.p), right.x, curve.p);
    u64 y = modsub(modmul(slope, modsub(left.x, x, curve.p), curve.p), left.y, curve.p);
    return Point{x, y, false};
}
bool on_curve(Point point, const Curve& curve) {
    if (point.infinity) return true;
    if (point.x >= curve.p || point.y >= curve.p) return false;
    u64 x2 = modmul(point.x, point.x, curve.p);
    u64 rhs = modsum(modsum(modmul(x2, point.x, curve.p), modmul(curve.a, point.x, curve.p), curve.p), curve.b, curve.p);
    return modmul(point.y, point.y, curve.p) == rhs;
}

int run(const char* filename) {
    std::ifstream input(filename);
    if (!input) throw std::runtime_error("cannot open prepared input");
    std::string tag;
    Curve curve{};
    std::size_t nbase, ntarget;
    if (!(input >> tag >> curve.p >> curve.a >> curve.b >> curve.r >> nbase >> ntarget) || tag != "curve")
        throw std::runtime_error("invalid header");
    if (curve.p <= 3 || curve.a >= curve.p || curve.b >= curve.p || nbase == 0 || nbase % 2)
        throw std::runtime_error("invalid curve or base size");
    std::vector<Point> base;
    base.reserve(nbase);
    for (std::size_t index = 0; index < nbase; ++index) {
        std::size_t supplied;
        Point point{};
        if (!(input >> tag >> supplied >> point.x >> point.y) || tag != "base" || supplied != index || !on_curve(point, curve))
            throw std::runtime_error("invalid base line");
        base.push_back(point);
    }
    for (std::size_t index = 0; index < nbase; index += 2)
        if (!(negate(base[index], curve.p) == base[index + 1]))
            throw std::runtime_error("invalid signed pair");
    std::vector<Target> targets;
    targets.reserve(ntarget);
    for (std::size_t index = 0; index < ntarget; ++index) {
        std::size_t supplied;
        Target target{};
        if (!(input >> tag >> supplied >> target.alpha >> target.beta >> target.point.x >> target.point.y)
            || tag != "target" || supplied != index || target.alpha >= curve.r
            || target.beta == 0 || target.beta >= curve.r || !on_curve(target.point, curve))
            throw std::runtime_error("invalid target line");
        targets.push_back(target);
    }
    if (input >> tag) throw std::runtime_error("extra prepared input");
    std::unordered_map<Point, u64, Hash> pair_count;
    pair_count.reserve(nbase * (nbase + 1) / 2);
    for (std::size_t left = 0; left < nbase; ++left)
        for (std::size_t right = left; right < nbase; ++right)
            pair_count[add(base[left], base[right], curve)] += left == right ? 1 : 2;
    std::cout << "count-v1\t" << curve.p << '\t' << curve.r << '\t' << nbase << '\t' << ntarget << '\n';
    for (std::size_t index = 0; index < ntarget; ++index) {
        u64 ordered = 0;
        for (Point point : base) {
            Point residual = add(targets[index].point, negate(point, curve.p), curve);
            auto found = pair_count.find(residual);
            if (found != pair_count.end()) ordered += found->second;
        }
        std::cout << "target\t" << index << '\t' << ordered << '\n';
    }
    return 0;
}

int main(int argc, char** argv) {
    if (argc != 2) {
        std::cerr << "usage: count_verify PREPARED_INPUT\n";
        return 2;
    }
    try {
        return run(argv[1]);
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
