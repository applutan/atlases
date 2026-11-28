#include <iostream>
#include <vector>
#include <numeric>
#include <algorithm>
#include <map>
#include <string>
#include <sstream>
#include <iomanip>
#include <chrono>
#include <cstdint>
#include <omp.h>

using namespace std;

// Structure to store orbit polynomial for a partition shape
struct ShapeResult {
    vector<int> shape;
    uint64_t partitions_count = 0;
    uint64_t mosaics_count = 0;
    map<int, uint64_t> orbit_sizes; // size -> count of orbits
};

struct RingResult {
    int n = 0;
    int group_order = 0;
    uint64_t bell_n = 0;
    uint64_t total_mosaics = 0;
    vector<ShapeResult> shapes;
    map<int, uint64_t> aggregate_orbit_sizes;
};

// Generate integer partitions of n (shapes) in descending order of parts
void get_integer_partitions(int n, int max_val, vector<int>& cur, vector<vector<int>>& res) {
    if (n == 0) {
        res.push_back(cur);
        return;
    }
    for (int p = min(n, max_val); p >= 1; --p) {
        cur.push_back(p);
        get_integer_partitions(n - p, p, cur, res);
        cur.pop_back();
    }
}

// Dihedral group operation on bitmask
uint32_t transform_mask(uint32_t mask, int a, int b, int n) {
    uint32_t res = 0;
    for (int x = 0; x < n; ++x) {
        if ((mask >> x) & 1) {
            int nx = (a * x + b) % n;
            if (nx < 0) nx += n;
            res |= (1U << nx);
        }
    }
    return res;
}

// Format shape as LaTeX monomial: (2, 2, 1, 1) -> z_2^2 z_1^2
string format_shape_monomial(const vector<int>& shape) {
    map<int, int> counts;
    for (int p : shape) counts[p]++;
    vector<int> distinct_parts;
    for (auto const& [p, _] : counts) distinct_parts.push_back(p);
    sort(distinct_parts.rbegin(), distinct_parts.rend());

    ostringstream oss;
    bool first = true;
    for (int p : distinct_parts) {
        if (!first) oss << " ";
        first = false;
        int c = counts[p];
        if (c == 1) {
            oss << "z_{" << p << "}";
        } else {
            oss << "z_{" << p << "}^{" << c << "}";
        }
    }
    return oss.str();
}

// Format orbit polynomial: e.g. 1\omega^{1} + 2\omega^{2}
string format_orbit_poly(const map<int, uint64_t>& orbit_sizes) {
    if (orbit_sizes.empty()) return "0";
    ostringstream oss;
    bool first = true;
    for (auto const& [sz, cnt] : orbit_sizes) {
        if (cnt == 0) continue;
        if (!first) oss << " + ";
        first = false;
        oss << cnt << "\\omega^{" << sz << "}";
    }
    return oss.str();
}

// Recursive backtrack for set partitions of a fixed shape lambda
void backtrack_partitions(
    int x,
    int n,
    int s,
    const vector<int>& blk_sizes,
    int caps[],
    int blk_lens[],
    uint32_t blocks[],
    const vector<pair<int, int>>& d_ops,
    int group_order,
    map<int, uint64_t>& orbit_partition_counts
) {
    if (x == n) {
        // Sort current blocks by mask value for canonical comparison
        vector<uint32_t> sorted_cur(s);
        for (int i = 0; i < s; ++i) sorted_cur[i] = blocks[i];
        sort(sorted_cur.begin(), sorted_cur.end());

        // Evaluate stabilizer order of current partition
        int stab_order = 0;
        vector<uint32_t> trans_blocks(s);

        for (auto const& op : d_ops) {
            for (int i = 0; i < s; ++i) {
                trans_blocks[i] = transform_mask(sorted_cur[i], op.first, op.second, n);
            }
            sort(trans_blocks.begin(), trans_blocks.end());

            bool fixed = true;
            for (int i = 0; i < s; ++i) {
                if (trans_blocks[i] != sorted_cur[i]) {
                    fixed = false;
                    break;
                }
            }
            if (fixed) {
                stab_order++;
            }
        }

        int orb_sz = group_order / stab_order;
        orbit_partition_counts[orb_sz]++;
        return;
    }

    uint32_t seen_empty_sizes = 0;
    for (int b = 0; b < s; ++b) {
        if (caps[b] > 0) {
            if (blk_lens[b] == 0) {
                int sz = blk_sizes[b];
                if ((seen_empty_sizes >> sz) & 1) continue;
                seen_empty_sizes |= (1U << sz);
            }

            blocks[b] |= (1U << x);
            blk_lens[b]++;
            caps[b]--;

            backtrack_partitions(
                x + 1, n, s, blk_sizes, caps, blk_lens, blocks,
                d_ops, group_order, orbit_partition_counts
            );

            blocks[b] ^= (1U << x);
            blk_lens[b]--;
            caps[b]++;
        }
    }
}

RingResult compute_ring(int n) {
    RingResult rr;
    rr.n = n;

    // Build dihedral group operations (a, b)
    vector<pair<int, int>> d_ops;
    if (n == 1) {
        d_ops.push_back({1, 0});
    } else if (n == 2) {
        d_ops.push_back({1, 0});
        d_ops.push_back({1, 1});
    } else {
        for (int a : {1, -1}) {
            for (int b = 0; b < n; ++b) {
                d_ops.push_back({a, b});
            }
        }
    }
    rr.group_order = (int)d_ops.size();

    // Generate integer partitions of n
    vector<vector<int>> raw_shapes;
    vector<int> cur;
    get_integer_partitions(n, n, cur, raw_shapes);

    // Sort shapes: Tier 2 (part count s ascending), Tier 3 (parts lexicographical descending)
    sort(raw_shapes.begin(), raw_shapes.end(), [](const vector<int>& a, const vector<int>& b) {
        if (a.size() != b.size()) return a.size() < b.size();
        return a > b;
    });

    int num_shapes = (int)raw_shapes.size();
    rr.shapes.resize(num_shapes);

    #pragma omp parallel for schedule(dynamic, 1)
    for (int i = 0; i < num_shapes; ++i) {
        const auto& sh = raw_shapes[i];
        ShapeResult sr;
        sr.shape = sh;

        int s = (int)sh.size();
        vector<int> blk_sizes = sh;
        int caps[32];
        int blk_lens[32] = {0};
        uint32_t blocks[32] = {0};

        for (int j = 0; j < s; ++j) {
            caps[j] = sh[j];
        }

        map<int, uint64_t> orbit_partition_counts;

        backtrack_partitions(
            0, n, s, blk_sizes, caps, blk_lens, blocks,
            d_ops, rr.group_order, orbit_partition_counts
        );

        for (auto const& [sz, p_cnt] : orbit_partition_counts) {
            uint64_t orb_cnt = p_cnt / sz;
            sr.orbit_sizes[sz] = orb_cnt;
            sr.partitions_count += p_cnt;
            sr.mosaics_count += orb_cnt;
        }

        rr.shapes[i] = sr;
    }

    for (const auto& sr : rr.shapes) {
        rr.bell_n += sr.partitions_count;
        rr.total_mosaics += sr.mosaics_count;
        for (auto const& [sz, cnt] : sr.orbit_sizes) {
            rr.aggregate_orbit_sizes[sz] += cnt;
        }
    }

    return rr;
}

int main(int argc, char* argv[]) {
    int min_n = 1;
    int max_n = 12;

    if (argc >= 2) {
        max_n = atoi(argv[1]);
    }
    if (argc >= 3) {
        min_n = atoi(argv[2]);
    }

    cout << "========================================================================\n";
    cout << "COMPUTE STRATIFIED DIHEDRAL MOSAIC CENSUS FOR Z_" << min_n << " TO Z_" << max_n << "\n";
    cout << "========================================================================\n";

    auto start_all = chrono::high_resolution_clock::now();

    for (int n = min_n; n <= max_n; ++n) {
        auto t0 = chrono::high_resolution_clock::now();
        RingResult rr = compute_ring(n);
        auto t1 = chrono::high_resolution_clock::now();
        double elapsed = chrono::duration<double>(t1 - t0).count();

        cout << "Ring Z_" << n << " (" << rr.shapes.size() << " shapes, "
             << rr.bell_n << " partitions -> " << rr.total_mosaics << " mosaics) in "
             << fixed << setprecision(3) << elapsed << " s\n";
        cout << "  Orbit polynomial: " << format_orbit_poly(rr.aggregate_orbit_sizes) << "\n";
    }

    auto end_all = chrono::high_resolution_clock::now();
    cout << "Total elapsed time: " << chrono::duration<double>(end_all - start_all).count() << " s\n";

    return 0;
}
