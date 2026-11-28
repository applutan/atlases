#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdint>
#include <chrono>

using namespace std;

// Eight 2-cycles of r^8 on Z_16: (k, k+8) for k in 0..7
// We want to generate all 428,131 partitions of Z_16 fixed by r^8.
// A partition is represented as vector of block bitmasks.

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

// 16 reflections in D_16: x -> b - x (mod 16) for b in 0..15
bool has_reflection_symmetry(const vector<uint32_t>& sorted_blocks) {
    int s = (int)sorted_blocks.size();
    vector<uint32_t> trans(s);
    for (int b = 0; b < 16; ++b) {
        for (int i = 0; i < s; ++i) {
            trans[i] = transform_mask(sorted_blocks[i], -1, b, 16);
        }
        sort(trans.begin(), trans.end());
        if (trans == sorted_blocks) {
            return true;
        }
    }
    return false;
}

// Check if fixed by r^4: x -> (x + 4) % 16
bool is_fixed_by_r4(const vector<uint32_t>& sorted_blocks) {
    int s = (int)sorted_blocks.size();
    vector<uint32_t> trans(s);
    for (int i = 0; i < s; ++i) {
        trans[i] = transform_mask(sorted_blocks[i], 1, 4, 16);
    }
    sort(trans.begin(), trans.end());
    return trans == sorted_blocks;
}

uint64_t total_generated = 0;
uint64_t achiral_count = 0;
uint64_t chiral_count = 0;
uint64_t chiral_fixed_by_r4 = 0;

struct BlockInfo {
    uint32_t mask;
    int partner_idx; // if self-conjugate, partner_idx == self
};

vector<BlockInfo> cur_blocks;

void backtrack(int k) {
    if (k == 8) {
        total_generated++;
        // Construct canonical block list
        int s = (int)cur_blocks.size();
        vector<uint32_t> blks(s);
        for (int i = 0; i < s; ++i) blks[i] = cur_blocks[i].mask;
        sort(blks.begin(), blks.end());

        bool achiral = has_reflection_symmetry(blks);
        if (achiral) {
            achiral_count++;
        } else {
            chiral_count++;
            if (is_fixed_by_r4(blks)) {
                chiral_fixed_by_r4++;
            }
        }
        return;
    }

    int p0 = k;
    int p1 = k + 8;

    int num_blocks = (int)cur_blocks.size();

    // Option 1: Put both p0 and p1 into an existing self-conjugate block
    for (int i = 0; i < num_blocks; ++i) {
        if (cur_blocks[i].partner_idx == i) {
            cur_blocks[i].mask |= (1U << p0) | (1U << p1);
            backtrack(k + 1);
            cur_blocks[i].mask ^= (1U << p0) | (1U << p1);
        }
    }

    // Option 2: Put p0 into an existing block i and p1 into its partner j (i != j)
    for (int i = 0; i < num_blocks; ++i) {
        int j = cur_blocks[i].partner_idx;
        if (i < j) {
            // Put p0 in i, p1 in j
            cur_blocks[i].mask |= (1U << p0);
            cur_blocks[j].mask |= (1U << p1);
            backtrack(k + 1);
            cur_blocks[i].mask ^= (1U << p0);
            cur_blocks[j].mask ^= (1U << p1);

            // Put p0 in j, p1 in i
            cur_blocks[j].mask |= (1U << p0);
            cur_blocks[i].mask |= (1U << p1);
            backtrack(k + 1);
            cur_blocks[j].mask ^= (1U << p0);
            cur_blocks[i].mask ^= (1U << p1);
        }
    }

    // Option 3: Start a new self-conjugate block with {p0, p1}
    int new_idx = (int)cur_blocks.size();
    cur_blocks.push_back({(1U << p0) | (1U << p1), new_idx});
    backtrack(k + 1);
    cur_blocks.pop_back();

    // Option 4: Start a new paired block pair: {p0} and {p1}
    int idx_a = (int)cur_blocks.size();
    int idx_b = idx_a + 1;
    cur_blocks.push_back({(1U << p0), idx_b});
    cur_blocks.push_back({(1U << p1), idx_a});
    backtrack(k + 1);
    cur_blocks.pop_back();
    cur_blocks.pop_back();
}

int main() {
    auto t0 = chrono::high_resolution_clock::now();
    backtrack(0);
    auto t1 = chrono::high_resolution_clock::now();
    double el = chrono::duration<double>(t1 - t0).count();

    cout << "Total generated partitions fixed by r^8: " << total_generated << " (Expected: 428131)\n";
    cout << "Achiral (fixed by some reflection): " << achiral_count << "\n";
    cout << "Chiral (no reflection symmetry): " << chiral_count << "\n";
    cout << "Chiral fixed by r^4: " << chiral_fixed_by_r4 << "\n";
    cout << "Elapsed: " << el << " s\n";

    return 0;
}
