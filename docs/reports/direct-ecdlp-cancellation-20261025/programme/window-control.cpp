#include <array>
#include <cstdint>
#include <exception>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// Developer regression control, not an ECDLP solver or performance experiment.
// This intentionally enumerates all tiny point-state boundaries and windows.
namespace {
struct Tag {
    bool constant = false;
    std::uint64_t bits = 0;
    Tag& operator^=(const Tag& other) {
        constant = constant != other.constant;
        bits ^= other.bits;
        return *this;
    }
    bool operator==(const Tag&) const = default;
};
using TaggedMatrix = std::vector<std::vector<Tag>>;

void require(bool value, const std::string& message) {
    if (!value) throw std::runtime_error(message);
}

std::size_t binary_rank(std::vector<std::uint64_t> rows,
                        const unsigned columns) {
    require(columns < 64U, "test matrix exceeds bit-vector capacity");
    std::size_t pivot_row = 0;
    for (unsigned column = 0; column < columns; ++column) {
        const std::uint64_t mask = std::uint64_t{1} << column;
        std::size_t found = pivot_row;
        while (found < rows.size() && (rows[found] & mask) == 0U) ++found;
        if (found == rows.size()) continue;
        std::swap(rows[pivot_row], rows[found]);
        for (std::size_t row = pivot_row + 1U; row < rows.size(); ++row) {
            if ((rows[row] & mask) != 0U) rows[row] ^= rows[pivot_row];
        }
        ++pivot_row;
    }
    return pivot_row;
}

TaggedMatrix window_matrix(const unsigned r, const unsigned d) {
    require(d > 0U && d < 16U, "window outside tiny test domain");
    const unsigned length = 1U << d;
    TaggedMatrix matrix(r, std::vector<Tag>(r));
    for (unsigned a = 0; a < r; ++a) {
        for (unsigned b = 0; b < length; ++b) {
            const unsigned output = (length * a + b) % r;
            matrix[a][output] ^= Tag{true, b};
        }
    }
    return matrix;
}

std::vector<std::uint64_t> constant_part(const TaggedMatrix& matrix) {
    std::vector<std::uint64_t> rows(matrix.size());
    for (std::size_t a = 0; a < matrix.size(); ++a) {
        for (std::size_t b = 0; b < matrix.size(); ++b) {
            if (matrix[a][b].constant) rows[a] ^= std::uint64_t{1} << b;
        }
    }
    return rows;
}

Tag row_sum(const TaggedMatrix& matrix, const unsigned a) {
    Tag sum;
    for (const Tag& entry : matrix[a]) sum ^= entry;
    return sum;
}

Tag column_sum(const TaggedMatrix& matrix, const unsigned b) {
    Tag sum;
    for (const auto& row : matrix) sum ^= row[b];
    return sum;
}

int self_test() {
    constexpr std::array<unsigned, 6> subgroup_orders{3, 5, 7, 11, 13, 17};
    unsigned window_cases = 0;
    unsigned rank_checks = 0;
    unsigned margin_checks = 0;
    unsigned mutation_checks = 0;
    unsigned rank_calibration_checks = 0;
    for (const unsigned r : subgroup_orders) {
        std::vector<std::uint64_t> identity(r);
        for (unsigned a = 0; a < r; ++a) identity[a] = std::uint64_t{1} << a;
        require(binary_rank(identity, r) == r, "identity rank calibration");
        require(binary_rank(std::vector<std::uint64_t>(r), r) == 0U,
                "zero rank calibration");
        require(binary_rank(std::vector<std::uint64_t>(r, (std::uint64_t{1} << r) - 1U), r) == 1U,
                "all-ones rank calibration");
        rank_calibration_checks += 3U;
        for (unsigned d = 1; d <= 4U; ++d) {
            const TaggedMatrix matrix = window_matrix(r, d);
            require(binary_rank(constant_part(matrix), r) == r - 1U,
                    "window rank differs from r-1");
            ++rank_checks;
            // Sum_b (1 + sum_j bit_j(b) eps_j): constant coefficient is 0;
            // each bit occurs 2^(d-1) times, hence eps_0 for d=1 and 0 otherwise.
            const Tag expected{false, d == 1U ? 1U : 0U};
            for (unsigned a = 0; a < r; ++a) {
                require(row_sum(matrix, a) == expected, "tagged row margin");
                require(column_sum(matrix, a) == expected, "tagged column margin");
                margin_checks += 2U;
            }
            TaggedMatrix corrupted = matrix;
            corrupted[0][0].constant = !corrupted[0][0].constant;
            require(!(row_sum(corrupted, 0) == expected), "mutation was not detected");
            ++mutation_checks;
            ++window_cases;
        }
    }
    std::cout << "{\"status\":\"pass\",\"scope\":\"developer_regression_only\","
              << "\"window_cases\":" << window_cases
              << ",\"rank_checks\":" << rank_checks
              << ",\"tagged_margin_checks\":" << margin_checks
              << ",\"mutation_checks\":" << mutation_checks
              << ",\"rank_calibration_checks\":" << rank_calibration_checks
              << "}\n";
    return 0;
}
} // namespace

int main(int argc, char** argv) {
    try {
        if (argc == 2 && std::string(argv[1]) == "--self-test") return self_test();
        std::cerr << "usage: window-control --self-test\n";
        return 2;
    } catch (const std::exception& error) {
        std::cerr << "self-test failure: " << error.what() << '\n';
        return 1;
    }
}
