#include "common.hpp"

#include <bit>
#include <filesystem>
#include <iostream>
#include <limits>
#include <map>
#include <set>

// Enumerative algebraic controls. These programs do not implement a cheap
// coefficient oracle, a target-local quotient, or a new ECDLP algorithm.
namespace {
using lab::I;
using U = std::uint64_t;

struct Counts {
    U truth_point_comparisons = 0;
    U truth_entries = 0;
    U anf_xors = 0;
    U fp_interpolation_subtractions = 0;
    U fp_evaluation_additions = 0;
    U prefix_truth_additions = 0;
    U prefix_coefficient_xors = 0;
    U prefix_checks = 0;
    U fp_prefix_count_checks = 0;
    U fp_boolean_root_tests = 0;
    U singletons = 0;
    U empties = 0;
    U mutation_detections = 0;
    U max_support = 0;
    U min_support = std::numeric_limits<U>::max();
    unsigned max_degree = 0;
};

std::size_t dimension(unsigned ell) {
    lab::require(ell < 20, "enumerative control bit width exceeds supported bound");
    return std::size_t{1} << ell;
}

std::vector<unsigned char> anf(std::vector<unsigned char> values, unsigned ell,
                               Counts& count) {
    const std::size_t m = dimension(ell);
    lab::require(values.size() == m, "incorrect Boolean truth-table dimension");
    for (unsigned bit = 0; bit < ell; ++bit) {
        const std::size_t flag = std::size_t{1} << bit;
        for (std::size_t mask = 0; mask < m; ++mask) if ((mask & flag) != 0) {
            values[mask] ^= values[mask ^ flag];
            ++count.anf_xors;
        }
    }
    return values;
}

std::vector<I> interpolate_fp(const std::vector<unsigned char>& values,
                              unsigned ell, const lab::Curve& c, Counts& count) {
    const std::size_t m = dimension(ell);
    lab::require(values.size() == m, "incorrect interpolation dimension");
    std::vector<I> coefficients(values.begin(), values.end());
    for (unsigned bit = 0; bit < ell; ++bit) {
        const std::size_t flag = std::size_t{1} << bit;
        for (std::size_t mask = 0; mask < m; ++mask) if ((mask & flag) != 0) {
            coefficients[mask] = c.mod(coefficients[mask] - coefficients[mask ^ flag]);
            ++count.fp_interpolation_subtractions;
        }
    }
    return coefficients;
}

I evaluate_fp(const std::vector<I>& coefficients, std::size_t assignment,
              const lab::Curve& c, Counts& count) {
    I sum = 0;
    // On Boolean assignments, a monomial is one exactly for masks contained
    // in the assignment. This does not evaluate arbitrary field inputs.
    for (std::size_t mask = assignment;; mask = (mask - 1) & assignment) {
        sum = c.mod(sum + coefficients[mask]);
        ++count.fp_evaluation_additions;
        if (mask == 0) break;
    }
    return sum;
}

unsigned degree_fp(const std::vector<I>& coefficients) {
    unsigned degree = 0;
    for (std::size_t mask = 0; mask < coefficients.size(); ++mask)
        if (coefficients[mask] != 0)
            degree = std::max(degree, static_cast<unsigned>(std::popcount(mask)));
    return degree;
}

unsigned top_restricted_coefficient(const std::vector<unsigned char>& coefficients,
                                    unsigned ell, unsigned prefix_length,
                                    std::size_t prefix, Counts& count) {
    const unsigned remaining = ell - prefix_length;
    const std::size_t lower = dimension(remaining) - 1;
    unsigned parity = 0;
    for (std::size_t upper = prefix;; upper = (upper - 1) & prefix) {
        parity ^= coefficients[(upper << remaining) | lower];
        ++count.prefix_coefficient_xors;
        if (upper == 0) break;
    }
    return parity;
}

void check_prefixes(const std::vector<unsigned char>& truth,
                    const std::vector<unsigned char>& coefficients, unsigned ell,
                    Counts& count, bool record_integer_counts) {
    for (unsigned length = 0; length <= ell; ++length) {
        const unsigned remaining = ell - length;
        const std::size_t width = dimension(remaining);
        for (std::size_t prefix = 0; prefix < dimension(length); ++prefix) {
            U integer_count = 0;
            const std::size_t first = prefix << remaining;
            for (std::size_t i = first; i < first + width; ++i) {
                integer_count += truth[i];
                ++count.prefix_truth_additions;
            }
            const unsigned top = top_restricted_coefficient(coefficients, ell, length,
                                                            prefix, count);
            lab::require(top == (integer_count & 1U), "restricted top coefficient disagrees with truth parity");
            ++count.prefix_checks;
            if (record_integer_counts) {
                lab::require(integer_count <= 1, "singleton Boolean encoding has multiple inputs");
                ++count.fp_prefix_count_checks;
                if (integer_count == 0) ++count.empties;
                else ++count.singletons;
            }
        }
    }
    // The checker must reject an explicitly corrupted full coefficient.
    auto corrupted = coefficients;
    corrupted.back() ^= 1U;
    const unsigned bad = top_restricted_coefficient(corrupted, ell, 0, 0, count);
    unsigned parity = 0;
    for (unsigned char value : truth) parity ^= value;
    lab::require(bad != parity, "wrong-prefix mutation was not distinguished");
    ++count.mutation_detections;
}

U rank_fp(std::vector<std::vector<I>> matrix, const lab::Curve& c, U& operations) {
    if (matrix.empty()) return 0;
    const std::size_t rows = matrix.size(), columns = matrix.front().size();
    std::size_t rank = 0;
    for (std::size_t column = 0; column < columns && rank < rows; ++column) {
        std::size_t pivot = rank;
        while (pivot < rows && matrix[pivot][column] == 0) ++pivot;
        if (pivot == rows) continue;
        std::swap(matrix[pivot], matrix[rank]);
        const I inverse = c.inv(matrix[rank][column]);
        ++operations; // one explicitly named inversion, not one bit operation
        for (std::size_t j = column; j < columns; ++j) {
            matrix[rank][j] = c.mod(matrix[rank][j] * inverse);
            ++operations;
        }
        for (std::size_t i = 0; i < rows; ++i) if (i != rank && matrix[i][column] != 0) {
            const I multiplier = matrix[i][column];
            for (std::size_t j = column; j < columns; ++j) {
                matrix[i][j] = c.mod(matrix[i][j] - multiplier * matrix[rank][j]);
                operations += 2;
            }
        }
        ++rank;
    }
    return static_cast<U>(rank);
}

struct BranchResults {
    U idempotent_multiplications = 0;
    U orthogonality_products = 0;
    U sum_checks = 0;
    U rank_field_operations = 0;
    U branch_endpoint_lookups = 0;
    U target_truth_comparisons = 0;
    U target_bit_inputs_visited = 0;
    U singleton_targets = 0;
    U empty_wrong_prefix_targets = 0;
    U point_merge_lost_labels = 0;
    U duplicate_label_checks = 0;
    std::vector<U> dimensions;
    std::vector<U> point_images;
    std::vector<U> ranks;
    std::vector<U> canonical_support;
    I first_collision_left = -1, first_collision_right = -1;
    U peak_matrix_entries = 0;
};

BranchResults branch_controls(const lab::Fixture& f, const std::vector<lab::Point>& points) {
    BranchResults out;
    const std::size_t order = static_cast<std::size_t>(f.r);
    for (unsigned t = 1; t <= 6; ++t) {
        const std::size_t m = dimension(t);
        std::vector<std::vector<I>> evaluation(m, std::vector<I>(m));
        for (std::size_t label = 0; label < m; ++label)
            for (std::size_t assignment = 0; assignment < m; ++assignment) {
                I value = 1;
                for (unsigned bit = 0; bit < t; ++bit) {
                    const I x = static_cast<I>((assignment >> bit) & 1U);
                    const I factor = ((label >> bit) & 1U) != 0 ? x : 1 - x;
                    value = f.c.mod(value * factor);
                    ++out.idempotent_multiplications;
                }
                evaluation[assignment][label] = value;
                lab::require(value == (assignment == label ? 1 : 0), "Boolean branch idempotent is not a delta");
            }
        for (std::size_t i = 0; i < m; ++i) {
            I sum = 0;
            for (std::size_t label = 0; label < m; ++label) sum = f.c.mod(sum + evaluation[i][label]);
            lab::require(sum == 1, "branch idempotents do not partition unity");
            ++out.sum_checks;
            for (std::size_t j = 0; j < m; ++j) for (std::size_t k = 0; k < m; ++k) {
                const I product = f.c.mod(evaluation[i][j] * evaluation[i][k]);
                lab::require(product == (j == k ? evaluation[i][j] : 0), "branch idempotents not orthogonal");
                ++out.orthogonality_products;
            }
        }
        const U rank = rank_fp(evaluation, f.c, out.rank_field_operations);
        lab::require(rank == m, "CRT evaluation map lacks full branch rank");
        std::map<lab::Point, std::size_t> image;
        std::set<std::pair<std::size_t, unsigned>> explicitly_tagged_copies;
        for (std::size_t label = 0; label < m; ++label) {
            const lab::Point endpoint = points[label % order];
            ++out.branch_endpoint_lookups;
            const auto [iterator, inserted] = image.emplace(endpoint, label);
            if (!inserted && out.first_collision_left < 0) {
                out.first_collision_left = static_cast<I>(iterator->second);
                out.first_collision_right = static_cast<I>(label);
                lab::require(iterator->second != label, "point-merge collision does not have distinct labels");
            }
            explicitly_tagged_copies.emplace(label, 0U);
            explicitly_tagged_copies.emplace(label, 1U);
        }
        lab::require(explicitly_tagged_copies.size() == 2 * m, "component tags failed to preserve branches");
        ++out.duplicate_label_checks;
        lab::require(image.size() == std::min(m, order), "point image unexpectedly noninjective before orbit wrap");
        out.point_merge_lost_labels += static_cast<U>(m - image.size());
        out.dimensions.push_back(static_cast<U>(m));
        out.ranks.push_back(rank);
        out.point_images.push_back(static_cast<U>(image.size()));
        out.canonical_support.push_back(static_cast<U>(std::min(m, order)));
        out.peak_matrix_entries = std::max(out.peak_matrix_entries, static_cast<U>(m * m));
    }
    // Canonical full graph, with target and full scalar-prefix pins. These are
    // truth-table controls, not a cheap quotient construction.
    const unsigned ell = lab::bits(static_cast<U>(f.r - 1));
    const std::size_t m = dimension(ell);
    for (std::size_t target = 0; target < order; ++target) {
        U solutions = 0, wrong_prefix_solutions = 0;
        const std::size_t wrong_prefix = target ^ 1U;
        for (std::size_t b = 0; b < m; ++b) {
            const bool accepted = b < order && points[b] == points[target];
            ++out.target_bit_inputs_visited;
            if (b < order) ++out.target_truth_comparisons;
            if (accepted) {
                ++solutions;
                if (b == wrong_prefix) ++wrong_prefix_solutions;
            }
        }
        lab::require(solutions == 1 && wrong_prefix_solutions == 0, "target-local singleton control failed");
        ++out.singleton_targets;
        ++out.empty_wrong_prefix_targets;
    }
    return out;
}

void print_array(std::ostream& out, const std::vector<U>& values) {
    out << '[';
    for (std::size_t i = 0; i < values.size(); ++i) { if (i != 0) out << ','; out << values[i]; }
    out << ']';
}

void emit_branch(std::ostream& out, const lab::Fixture& f, const BranchResults& r) {
    out << "{\"track\":\"L5\",\"fixture\":" << lab::json_quote(f.id)
        << ",\"scope\":\"exploratory_toy_diagnostic\",\"outcome\":\"complete_control\",\"depths\":[1,2,3,4,5,6],\"labelled_support\":";
    print_array(out, r.dimensions);
    out << ",\"crt_evaluation_rank\":"; print_array(out, r.ranks);
    out << ",\"point_image_size\":"; print_array(out, r.point_images);
    out << ",\"canonical_range_support\":"; print_array(out, r.canonical_support);
    out << ",\"idempotent_field_multiplications\":" << r.idempotent_multiplications
        << ",\"orthogonality_products\":" << r.orthogonality_products
        << ",\"partition_unity_checks\":" << r.sum_checks
        << ",\"rank_field_operations_including_inversions\":" << r.rank_field_operations
        << ",\"branch_endpoint_table_lookups\":" << r.branch_endpoint_lookups
        << ",\"point_merge_lost_labels_sum_over_depths\":" << r.point_merge_lost_labels
        << ",\"first_point_merge_collision_labels\":";
    if (r.first_collision_left >= 0) out << '[' << r.first_collision_left << ',' << r.first_collision_right << ']';
    else out << "null";
    out << ",\"duplicate_selector_support_checks\":" << r.duplicate_label_checks
        << ",\"canonical_target_truth_comparisons\":" << r.target_truth_comparisons
        << ",\"canonical_bit_inputs_visited\":" << r.target_bit_inputs_visited
        << ",\"singleton_targets\":" << r.singleton_targets
        << ",\"empty_incompatible_full_prefix_targets\":" << r.empty_wrong_prefix_targets
        << ",\"peak_evaluation_matrix_entries\":" << r.peak_matrix_entries
        << ",\"enumerated_orbit_entries_charged\":" << f.r
        << ",\"orbit_group_additions_charged\":" << f.r
        << ",\"original_theorem_deferred_solver_executed\":false,\"remaining_gap\":\"No target-local constructive invariant or quotient solver supplied; this is a Boolean branch/CRT control.\"}\n";
}

struct CoefficientResults {
    Counts counts;
    unsigned ell = 0;
    unsigned range_constraint_degree = 0;
    unsigned target_constraint_degree_min = std::numeric_limits<unsigned>::max();
    unsigned target_constraint_degree_max = 0;
    U maximum_degree_sum = 0;
    U minimum_degree_sum = std::numeric_limits<U>::max();
    U nonboolean_field_roots = 0;
    U fp_interpolation_checks = 0;
    U fp_range_checks = 0;
    U full_singleton_targets = 0;
    U full_empty_controls = 0;
    U boolean_constraint_root_checks = 0;
    U affine_control_prefix_checks = 0;
    U permutation_control_prefix_checks = 0;
    U many_solution_parity_traps = 0;
    U zero_polynomial_orientation_traps = 0;
    U naive_or_traps = 0;
    U nilpotent_double_witness_traps = 0;
    U divided_count_traps = 0;
    U bytes_truth_and_coefficients = 0;
};

U calibration_prefixes(const std::vector<std::size_t>& images, unsigned ell) {
    const std::size_t m = dimension(ell);
    lab::require(images.size() == m, "calibration map dimension mismatch");
    std::set<std::size_t> unique(images.begin(), images.end());
    lab::require(unique.size() == m && *unique.rbegin() < m, "calibration map is not a permutation");
    Counts counts;
    for (std::size_t target = 0; target < m; ++target) {
        std::vector<unsigned char> truth(m);
        for (std::size_t b = 0; b < m; ++b) truth[b] = static_cast<unsigned char>(images[b] == target);
        check_prefixes(truth, anf(truth, ell, counts), ell, counts, false);
    }
    return counts.prefix_checks;
}

CoefficientResults coefficient_controls(const lab::Fixture& f, const std::vector<lab::Point>& points) {
    CoefficientResults result;
    const unsigned ell = lab::bits(static_cast<U>(f.r - 1));
    const std::size_t m = dimension(ell), order = static_cast<std::size_t>(f.r);
    result.ell = ell;
    lab::require(order <= 4096, "all-target coefficient diagnostic currently limited to r<=4096");
    Counts& count = result.counts;
    std::vector<unsigned char> range(m);
    for (std::size_t b = 0; b < m; ++b) range[b] = static_cast<unsigned char>(b < order);
    auto range_coefficients = interpolate_fp(range, ell, f.c, count);
    for (std::size_t b = 0; b < m; ++b) {
        lab::require(evaluate_fp(range_coefficients, b, f.c, count) == range[b], "canonical-range interpolation disagrees");
        ++result.fp_range_checks;
    }
    range_coefficients[0] = f.c.mod(range_coefficients[0] - 1);
    result.range_constraint_degree = degree_fp(range_coefficients);
    // Every field solution of z(z-1)=0 is Boolean. Enumerating the single
    // coordinate validates this premise; the written product argument then
    // counts all multivariable solutions without enumerating p^ell tuples.
    for (I x = 0; x < f.c.p; ++x) {
        const bool root = f.c.mod(x * (x - 1)) == 0;
        lab::require(root == (x == 0 || x == 1), "non-Boolean field root in z(z-1)");
        ++result.boolean_constraint_root_checks;
        if (root && x != 0 && x != 1) ++result.nonboolean_field_roots;
    }
    for (std::size_t target = 0; target < order; ++target) {
        std::vector<unsigned char> truth(m);
        U full_integer_count = 0;
        for (std::size_t b = 0; b < m; ++b) {
            const bool accepted = b < order && points[b] == points[target];
            truth[b] = static_cast<unsigned char>(accepted);
            if (b < order) ++count.truth_point_comparisons;
            ++count.truth_entries;
            full_integer_count += truth[b];
        }
        lab::require(full_integer_count == 1, "canonical point graph is not singleton");
        ++result.full_singleton_targets;
        const auto coefficients = anf(truth, ell, count);
        U support = 0;
        unsigned degree = 0;
        for (std::size_t mask = 0; mask < m; ++mask) if (coefficients[mask] != 0) {
            ++support;
            degree = std::max(degree, static_cast<unsigned>(std::popcount(mask)));
        }
        count.max_support = std::max(count.max_support, support);
        count.min_support = std::min(count.min_support, support);
        count.max_degree = std::max(count.max_degree, degree);
        check_prefixes(truth, coefficients, ell, count, true);

        auto field_coefficients = interpolate_fp(truth, ell, f.c, count);
        for (std::size_t b = 0; b < m; ++b) {
            lab::require(evaluate_fp(field_coefficients, b, f.c, count) == truth[b], "Fp interpolation disagrees with EC truth");
            ++result.fp_interpolation_checks;
        }
        // Explicit constraints: b_i(b_i-1)=0 (ell degree-two equations),
        // C_range(b)-1=0, and P_Q(b)-1=0. Prefix pins add degree-one equations.
        field_coefficients[0] = f.c.mod(field_coefficients[0] - 1);
        const unsigned target_degree = degree_fp(field_coefficients);
        result.target_constraint_degree_min = std::min(result.target_constraint_degree_min, target_degree);
        result.target_constraint_degree_max = std::max(result.target_constraint_degree_max, target_degree);
        const U degree_sum = U{2} * ell + result.range_constraint_degree + target_degree;
        result.maximum_degree_sum = std::max(result.maximum_degree_sum, degree_sum + ell);
        result.minimum_degree_sum = std::min(result.minimum_degree_sum, degree_sum);
        const U maximum_degree = std::max(2U, std::max(result.range_constraint_degree, target_degree));
        for (unsigned prefix_length = 0; prefix_length <= ell; ++prefix_length) {
            const I numerator = static_cast<I>(ell) - static_cast<I>(degree_sum + prefix_length);
            const I denominator = static_cast<I>(maximum_degree);
            // C++ signed division truncates toward zero, which is ceiling
            // for a negative numerator and positive denominator.
            const I ceiling = numerator > 0 ? (numerator + denominator - 1) / denominator : numerator / denominator;
            const I exponent = std::max(I{0}, ceiling);
            lab::require(exponent == 0, "unexpected positive Ax-Katz exponent on known singleton");
        }
        // An incompatible full prefix leaves no solution. Its integer count
        // is checked directly, not inferred from divisibility.
        const std::size_t wrong = target ^ 1U;
        U empty_count = 0;
        for (std::size_t b = 0; b < m; ++b) if (b == wrong) empty_count += truth[b];
        lab::require(empty_count == 0, "incompatible-prefix empty control failed");
        ++result.full_empty_controls;
        // Ordinary parity can be zero for a nonempty set. No singleton
        // existence conclusion can be reused after adding auxiliary freedom.
        const unsigned erased = coefficients.back() ^ coefficients.back();
        lab::require(erased == 0 && full_integer_count == 1, "double witness parity trap failed");
        ++result.nilpotent_double_witness_traps;
    }
    {
        std::vector<unsigned char> many(m);
        many[0] = 1; many[1] = 1;
        Counts local;
        const auto coefficients = anf(many, ell, local);
        lab::require(coefficients.back() == 0, "two-solution parity trap did not cancel");
        ++result.many_solution_parity_traps;
    }
    {
        std::vector<unsigned char> zero(m);
        Counts local;
        const auto coefficients = anf(zero, ell, local);
        lab::require(std::all_of(coefficients.begin(), coefficients.end(),
                                [](unsigned char x) { return x == 0; }),
                     "zero polynomial calibration failed");
        // As an indicator, zero accepts nothing; as the equation 0=0 it
        // accepts the entire Boolean domain. The equation orientation is
        // part of the contract, not information supplied by its coefficient.
        lab::require(m > 0, "empty zero-polynomial calibration domain");
        ++result.zero_polynomial_orientation_traps;
    }
    // x OR x is x, whereas a naive replacement of OR with F2 addition gives
    // x+x=0. This is an invalid counting shortcut deliberately detected.
    lab::require((1U | 1U) == 1U && (1U ^ 1U) == 0U, "naive OR negative control failed");
    ++result.naive_or_traps;
    lab::require(0 % f.c.p == 0 && f.c.p % f.c.p == 0 && f.c.p > 0,
                 "empty/positive divisible receipt trap failed");
    ++result.divided_count_traps;
    const unsigned control_bits = std::min(ell, 4U);
    const std::size_t control_m = dimension(control_bits);
    std::vector<std::size_t> affine(control_m);
    for (std::size_t b = 0; b < control_m; ++b)
        affine[b] = ((b << 1) | (b >> (control_bits - 1))) & (control_m - 1);
    for (std::size_t& b : affine) b ^= (control_m - 1);
    result.affine_control_prefix_checks = calibration_prefixes(affine, control_bits);
    std::vector<I> random_labels(control_m);
    for (std::size_t i = 0; i < control_m; ++i) random_labels[i] = static_cast<I>(i);
    lab::RNG rng(f.seed ^ 0xb4c3a207518e9d6fULL);
    rng.shuffle(random_labels);
    std::vector<std::size_t> permutation(control_m);
    for (std::size_t i = 0; i < control_m; ++i) permutation[i] = static_cast<std::size_t>(random_labels[i]);
    result.permutation_control_prefix_checks = calibration_prefixes(permutation, control_bits);
    // Three byte arrays and two int64 coefficient arrays can be live together;
    // vector allocator overhead and the orbit are separately disclosed.
    result.bytes_truth_and_coefficients = static_cast<U>(m) * (U{3} + U{2} * sizeof(I));
    return result;
}

void emit_coefficient(std::ostream& out, const lab::Fixture& f, const CoefficientResults& r) {
    const auto& c = r.counts;
    out << "{\"track\":\"L7\",\"fixture\":" << lab::json_quote(f.id)
        << ",\"scope\":\"exploratory_toy_diagnostic\",\"outcome\":\"complete_control\",\"scalar_bits\":" << r.ell
        << ",\"canonical_targets\":" << f.r
        << ",\"truth_entries_constructed\":" << c.truth_entries
        << ",\"ec_truth_point_comparisons\":" << c.truth_point_comparisons
        << ",\"anf_xors\":" << c.anf_xors
        << ",\"prefix_truth_additions\":" << c.prefix_truth_additions
        << ",\"restricted_coefficient_xors\":" << c.prefix_coefficient_xors
        << ",\"all_target_prefix_checks\":" << c.prefix_checks
        << ",\"wrong_prefix_mutations_detected\":" << c.mutation_detections
        << ",\"anf_support_min\":" << c.min_support << ",\"anf_support_max\":" << c.max_support
        << ",\"anf_degree_max\":" << c.max_degree
        << ",\"affine_map_calibration_prefix_checks\":" << r.affine_control_prefix_checks
        << ",\"explicit_permutation_calibration_prefix_checks\":" << r.permutation_control_prefix_checks
        << ",\"calibration_domain_bits\":" << std::min(r.ell, 4U)
        << ",\"calibration_maps_table_entries_charged\":" << U{2} * dimension(std::min(r.ell, 4U))
        << ",\"calibration_truth_entries_charged\":" << U{2} * dimension(std::min(r.ell, 4U)) * dimension(std::min(r.ell, 4U))
        << ",\"permutation_shuffle_draws\":" << dimension(std::min(r.ell, 4U)) - 1
        << ",\"many_solution_parity_traps_detected\":" << r.many_solution_parity_traps
        << ",\"zero_polynomial_orientation_traps_detected\":" << r.zero_polynomial_orientation_traps
        << ",\"naive_or_substitution_traps_detected\":" << r.naive_or_traps
        << ",\"double_auxiliary_witness_traps_detected\":" << r.nilpotent_double_witness_traps
        << ",\"main_phase_truth_coefficient_payload_bytes\":" << r.bytes_truth_and_coefficients
        << ",\"orbit_entries_charged\":" << f.r << ",\"orbit_group_additions_charged\":" << f.r
        << ",\"shared_with_L8\":true,\"remaining_gap\":\"Every target used a charged full truth table; no cheap conditional-coefficient evaluator or new solver.\"}\n";
}

void emit_axkatz(std::ostream& out, const lab::Fixture& f, const CoefficientResults& r) {
    const auto& c = r.counts;
    const unsigned ell = r.ell;
    out << "{\"track\":\"L8\",\"fixture\":" << lab::json_quote(f.id)
        << ",\"scope\":\"exploratory_toy_diagnostic\",\"outcome\":\"complete_control\",\"variables\":" << ell
        << ",\"boolean_equations\":" << ell << ",\"boolean_equation_degree\":2"
        << ",\"range_constraint_degree\":" << r.range_constraint_degree
        << ",\"target_constraint_degree_min\":" << r.target_constraint_degree_min
        << ",\"target_constraint_degree_max\":" << r.target_constraint_degree_max
        << ",\"equations_before_prefix\":" << ell + 2U
        << ",\"prefix_equations_min\":0,\"prefix_equations_max\":" << ell
        << ",\"total_degree_sum_min\":" << r.minimum_degree_sum
        << ",\"total_degree_sum_max_with_prefix\":" << r.maximum_degree_sum
        << ",\"max_equation_degree\":" << std::max(2U, std::max(r.range_constraint_degree, r.target_constraint_degree_max))
        << ",\"ax_katz_nonnegative_divisibility_exponent_all_prefixes\":0"
        << ",\"Fp_interpolation_subtractions\":" << c.fp_interpolation_subtractions
        << ",\"Fp_evaluation_additions\":" << c.fp_evaluation_additions
        << ",\"Fp_target_interpolation_checks\":" << r.fp_interpolation_checks
        << ",\"Fp_range_interpolation_checks\":" << r.fp_range_checks
        << ",\"single_coordinate_boolean_root_tests\":" << r.boolean_constraint_root_checks
        << ",\"nonboolean_field_roots\":" << r.nonboolean_field_roots
        << ",\"singleton_full_targets\":" << r.full_singleton_targets
        << ",\"empty_full_prefix_controls\":" << r.full_empty_controls
        << ",\"integer_prefix_singletons\":" << c.singletons << ",\"integer_prefix_empties\":" << c.empties
        << ",\"integer_prefix_count_checks\":" << c.fp_prefix_count_checks
        << ",\"empty_and_positive_divisible_counts\":[0," << f.c.p << ']'
        << ",\"divisibility_only_existence_inference_counterexamples\":" << r.divided_count_traps
        << ",\"encoding\":\"truth-derived multilinear indicator, not gate-polynomial compilation\""
        << ",\"truth_derived_public_fast_oracle\":false,\"shared_with_L7\":true"
        << ",\"remaining_gap\":\"Exact Fp singleton counts were obtained by charged Boolean truth enumeration; the divisibility lower bound is vacuous and supplies no exact residue evaluator.\"}\n";
}

void execute_fixture(const lab::Fixture& fixture, std::ostream& out) {
    lab::certify(fixture);
    lab::require(fixture.r <= 4096, "algebraic all-target pilot limited to r<=4096");
    const auto points = lab::orbit(fixture);
    const std::set<lab::Point> unique(points.begin(), points.end());
    lab::require(unique.size() == points.size(), "orbit labels are not unique");
    const auto branches = branch_controls(fixture, points);
    const auto coefficients = coefficient_controls(fixture, points);
    emit_branch(out, fixture, branches);
    emit_coefficient(out, fixture, coefficients);
    emit_axkatz(out, fixture, coefficients);
    lab::require(static_cast<bool>(out), "failed writing algebraic diagnostics");
}
} // namespace

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string(argv[1]) == "--self-test") {
            const std::vector<lab::Fixture> fixtures{
                {"unit-p5", "exception", {5, 0, 1}, {0, 1, false}, 3, 6, 1},
                {"unit-p17", "main", {17, 2, 2}, {5, 1, false}, 19, 19, 2},
                {"unit-p23", "main", {23, 1, 1}, {17, 3, false}, 7, 28, 3}
            };
            std::ostringstream sink;
            for (const auto& fixture : fixtures) execute_fixture(fixture, sink);
            const std::string records = sink.str();
            lab::require(std::count(records.begin(), records.end(), '\n') == 9,
                         "development suite omitted a track/fixture row");
            std::cout << "{\"status\":\"pass\",\"scope\":\"development_self_test\",\"fixtures\":3,\"track_rows\":9,\"tracks\":[\"L5\",\"L7\",\"L8\"],\"original_deferred_solver_run\":false}\n";
            return 0;
        }
        if (argc == 4 && std::string(argv[1]) == "--run") {
            const auto fixtures = lab::read_fixtures(argv[2]);
            lab::require(!std::filesystem::exists(argv[3]), "output path already exists; immutable attempts required");
            std::ofstream output(argv[3]);
            lab::require(static_cast<bool>(output), "cannot create output JSONL");
            for (const auto& fixture : fixtures) { execute_fixture(fixture, output); output.flush(); }
            std::cout << "{\"status\":\"complete\",\"scope\":\"exploratory_toy_diagnostic\",\"fixtures\":"
                      << fixtures.size() << ",\"track_rows\":" << fixtures.size() * 3
                      << ",\"remaining_fast_constructors\":\"not supplied\"}\n";
            return 0;
        }
        std::cerr << "usage: algebraic --self-test | --run FIXTURES_TSV OUTPUT_JSONL\n";
        return 2;
    } catch (const std::exception& error) {
        std::cerr << "algebraic failed: " << error.what() << '\n';
        return 1;
    }
}
