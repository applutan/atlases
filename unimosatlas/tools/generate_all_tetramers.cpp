#include <iostream>
#include <vector>
#include <algorithm>
#include <cstdint>
#include <fstream>
#include <chrono>
#include <tuple>
#include <array>
#include <unordered_map>
#include <iomanip>

using namespace std;

// 16 vertices: 0..15
// A 4-element block is represented by uint16_t mask with popcount 4.
// Total blocks: C(16, 4) = 1820.

struct BlockStride {
    uint8_t s[4];
    bool operator<(const BlockStride& o) const {
        for(int i=0; i<4; ++i) if(s[i] != o.s[i]) return s[i] < o.s[i];
        return false;
    }
    bool operator==(const BlockStride& o) const {
        for(int i=0; i<4; ++i) if(s[i] != o.s[i]) return false;
        return true;
    }
};

struct Partition {
    uint16_t b[4]; // sorted b[0] < b[1] < b[2] < b[3]
    bool operator<(const Partition& o) const {
        for(int i=0; i<4; ++i) if(b[i] != o.b[i]) return b[i] < o.b[i];
        return false;
    }
    bool operator==(const Partition& o) const {
        for(int i=0; i<4; ++i) if(b[i] != o.b[i]) return false;
        return true;
    }
};

// Global lookup tables
vector<uint16_t> all_blocks; // 1820
int block_to_id[65536];
uint16_t d_table[32][1820];
uint16_t mu3_table[1820];
bool is_sym_table[1820];
int chord_energy_table[1820];
BlockStride stride_table[1820];

void init_tables() {
    for(int m = 0; m < 65536; ++m) {
        if(__builtin_popcount(m) == 4) {
            block_to_id[m] = all_blocks.size();
            all_blocks.push_back(m);
        } else {
            block_to_id[m] = -1;
        }
    }

    // Symmetry & Energy & Strides for each block
    for(size_t i = 0; i < all_blocks.size(); ++i) {
        uint16_t m = all_blocks[i];
        vector<int> v;
        for(int k = 0; k < 16; ++k) if((m >> k) & 1) v.push_back(k);

        // Check bilateral symmetry
        bool sym = false;
        for(int c = 0; c < 16; ++c) {
            uint16_t ref_m = 0;
            for(int x : v) ref_m |= (1 << ((-x + c + 160) % 16));
            if(ref_m == m) { sym = true; break; }
        }
        is_sym_table[i] = sym;

        // Chord energy
        int E = 0;
        for(int a = 0; a < 4; ++a) {
            for(int b = a + 1; b < 4; ++b) {
                int d = min((v[b] - v[a] + 16) % 16, (v[a] - v[b] + 16) % 16);
                E += d * d;
            }
        }
        chord_energy_table[i] = E;

        // Cyclic strides
        vector<int> raw_s(4);
        for(int k = 0; k < 4; ++k) raw_s[k] = (v[(k+1)%4] - v[k] + 16) % 16;
        vector<vector<int>> cands;
        for(int shift = 0; shift < 4; ++shift) {
            vector<int> rot(4);
            for(int k = 0; k < 4; ++k) rot[k] = raw_s[(shift + k) % 4];
            cands.push_back(rot);
            vector<int> rev(4);
            for(int k = 0; k < 4; ++k) rev[k] = rot[3 - k];
            cands.push_back(rev);
        }
        sort(cands.begin(), cands.end());
        for(int k = 0; k < 4; ++k) stride_table[i].s[k] = cands[0][k];
    }

    // Dihedral actions: 16 rotations (a=1), 16 reflections (a=-1)
    for(int g = 0; g < 32; ++g) {
        int a = (g < 16) ? 1 : 15;
        int b = g % 16;
        for(size_t i = 0; i < all_blocks.size(); ++i) {
            uint16_t m = all_blocks[i];
            uint16_t gm = 0;
            for(int k = 0; k < 16; ++k) {
                if((m >> k) & 1) {
                    int img = (a * k + b) % 16;
                    gm |= (1 << img);
                }
            }
            d_table[g][i] = block_to_id[gm];
        }
    }

    // Multiplier mu_3: x -> 3x % 16
    for(size_t i = 0; i < all_blocks.size(); ++i) {
        uint16_t m = all_blocks[i];
        uint16_t mu_m = 0;
        for(int k = 0; k < 16; ++k) {
            if((m >> k) & 1) {
                int img = (3 * k) % 16;
                mu_m |= (1 << img);
            }
        }
        mu3_table[i] = block_to_id[mu_m];
    }
}

// Canonicalize a partition under D_16
pair<Partition, int> canonicalize_d(const Partition& p) {
    Partition best = p;
    Partition seen[32];
    int n_seen = 0;

    for(int g = 0; g < 32; ++g) {
        Partition gp;
        for(int i = 0; i < 4; ++i) gp.b[i] = d_table[g][p.b[i]];
        sort(gp.b, gp.b + 4);
        if(gp < best) best = gp;

        bool duplicate = false;
        for(int j = 0; j < n_seen; ++j) {
            if(seen[j] == gp) { duplicate = true; break; }
        }
        if(!duplicate) seen[n_seen++] = gp;
    }
    return {best, n_seen};
}

Partition apply_mu3(const Partition& p) {
    Partition res;
    for(int i = 0; i < 4; ++i) res.b[i] = mu3_table[p.b[i]];
    sort(res.b, res.b + 4);
    return res;
}

string format_partition_slash(const Partition& p) {
    const char hex_chars[] = "0123456789ABCDEF";
    string s = "/";
    for(int k = 0; k < 4; ++k) {
        uint16_t m = all_blocks[p.b[k]];
        for(int v = 0; v < 16; ++v) {
            if((m >> v) & 1) s += hex_chars[v];
        }
        s += "/";
    }
    return s;
}

string get_chirality_sig(const Partition& p) {
    string sig = "";
    for(int k = 0; k < 4; ++k) {
        sig += is_sym_table[p.b[k]] ? 's' : 'n';
    }
    return sig;
}

struct Tetramer {
    int orbit_size;
    int s_count;
    int energy;
    array<BlockStride, 4> strides;
    Partition p1, p2, p3, p4;

    bool operator<(const Tetramer& o) const {
        if(orbit_size != o.orbit_size) return orbit_size < o.orbit_size;
        if(s_count != o.s_count) return s_count > o.s_count; // descending
        if(energy != o.energy) return energy > o.energy;       // descending
        if(strides != o.strides) return strides < o.strides;
        return p1 < o.p1;
    }
};

int main(int argc, char* argv[]) {
    auto t0 = chrono::high_resolution_clock::now();
    cout << "Initializing combinatorial lookup tables..." << endl;
    init_tables();

    cout << "Generating raw partitions and computing dihedral orbits..." << endl;
    vector<int> b0_candidates;
    for(size_t i = 0; i < all_blocks.size(); ++i) {
        if(all_blocks[i] & 1) b0_candidates.push_back(i);
    }

    vector<Partition> raw_partitions;
    raw_partitions.reserve(2627625);

    for(int i0 : b0_candidates) {
        uint16_t m0 = all_blocks[i0];
        uint16_t rem0 = 0xFFFF ^ m0;
        int v1 = __builtin_ctz(rem0);

        for(size_t i1 = 0; i1 < all_blocks.size(); ++i1) {
            uint16_t m1 = all_blocks[i1];
            if(!(m1 & (1 << v1))) continue;
            if(m1 & m0) continue;

            uint16_t rem1 = rem0 ^ m1;
            int v2 = __builtin_ctz(rem1);

            for(size_t i2 = 0; i2 < all_blocks.size(); ++i2) {
                uint16_t m2 = all_blocks[i2];
                if(!(m2 & (1 << v2))) continue;
                if(m2 & (m0 | m1)) continue;

                uint16_t m3 = rem1 ^ m2;
                int i3 = block_to_id[m3];
                if(i3 >= 0) {
                    Partition p;
                    p.b[0] = i0; p.b[1] = i1; p.b[2] = i2; p.b[3] = i3;
                    sort(p.b, p.b + 4);
                    raw_partitions.push_back(p);
                }
            }
        }
    }

    // Canonicalize all partitions
    vector<pair<Partition, int>> d_orbits;
    {
        vector<Partition> can_list(raw_partitions.size());
        for(size_t i = 0; i < raw_partitions.size(); ++i) {
            Partition best = raw_partitions[i];
            for(int g = 1; g < 32; ++g) {
                Partition gp;
                for(int k = 0; k < 4; ++k) gp.b[k] = d_table[g][raw_partitions[i].b[k]];
                sort(gp.b, gp.b + 4);
                if(gp < best) best = gp;
            }
            can_list[i] = best;
        }
        sort(can_list.begin(), can_list.end());
        can_list.erase(unique(can_list.begin(), can_list.end()), can_list.end());

        for(const auto& can_p : can_list) {
            auto [canon, sz] = canonicalize_d(can_p);
            d_orbits.push_back({canon, sz});
        }
    }

    unordered_map<uint64_t, int> orbit_lookup;
    auto p_hash = [](const Partition& p) -> uint64_t {
        return ((uint64_t)p.b[0]) | (((uint64_t)p.b[1]) << 16) | (((uint64_t)p.b[2]) << 32) | (((uint64_t)p.b[3]) << 48);
    };

    for(size_t i = 0; i < d_orbits.size(); ++i) {
        orbit_lookup[p_hash(d_orbits[i].first)] = i;
    }

    // Decompose into Affine Macro-Orbits
    vector<bool> visited(d_orbits.size(), false);
    vector<Tetramer> tetramers;
    int n_monomers = 0;
    int n_dimers = 0;

    for(size_t i = 0; i < d_orbits.size(); ++i) {
        if(visited[i]) continue;
        Partition o1 = d_orbits[i].first;
        int sz = d_orbits[i].second;

        // mu_3 cycle
        Partition o2 = canonicalize_d(apply_mu3(o1)).first;
        if(o2 == o1) {
            visited[i] = true;
            n_monomers++;
            continue;
        }

        Partition o3 = canonicalize_d(apply_mu3(o2)).first;
        if(o3 == o1) {
            visited[i] = true;
            visited[orbit_lookup[p_hash(o2)]] = true;
            n_dimers++;
            continue;
        }

        Partition o4 = canonicalize_d(apply_mu3(o3)).first;
        visited[i] = true;
        visited[orbit_lookup[p_hash(o2)]] = true;
        visited[orbit_lookup[p_hash(o3)]] = true;
        visited[orbit_lookup[p_hash(o4)]] = true;

        Partition cycle_heads[4] = {o1, o2, o3, o4};
        Tetramer best_t;
        bool first = true;

        for(int ph = 0; ph < 4; ++ph) {
            Partition p_lead = cycle_heads[ph];
            Partition cp1 = p_lead;
            Partition cp2 = apply_mu3(cp1);
            Partition cp3 = apply_mu3(cp2);
            Partition cp4 = apply_mu3(cp3);

            Tetramer t;
            t.orbit_size = sz;
            t.s_count = 0;
            t.energy = 0;
            for(int k = 0; k < 4; ++k) {
                if(is_sym_table[cp1.b[k]]) t.s_count++;
                t.energy += chord_energy_table[cp1.b[k]];
                t.strides[k] = stride_table[cp1.b[k]];
            }
            sort(t.strides.begin(), t.strides.end());
            t.p1 = cp1; t.p2 = cp2; t.p3 = cp3; t.p4 = cp4;

            if(first || t < best_t) {
                best_t = t;
                first = false;
            }
        }
        tetramers.push_back(best_t);
    }

    sort(tetramers.begin(), tetramers.end());

    cout << "Classification complete: " << tetramers.size() << " tetramers." << endl;

    // Export to text file if requested
    string out_path = (argc > 1) ? argv[1] : "unimosatlas/data/tetramers_full_index.txt";
    cout << "Exporting full tetramer index to " << out_path << "..." << endl;
    ofstream fout(out_path);
    fout << "# ==============================================================================\n";
    fout << "# COMPLETE TETRAMER CATALOGUE: 20,721 4-CYCLES UNDER MU_3 ON Z_16\n";
    fout << "# 5-Tier Natural Sorting Cascade: |O| asc, s desc, E desc, strides, lex\n";
    fout << "# Format: ID |O| s E /p1/ [sig1] -> /p2/ [sig2] -> /p3/ [sig3] -> /p4/ [sig4]\n";
    fout << "# ==============================================================================\n";

    for(size_t i = 0; i < tetramers.size(); ++i) {
        const auto& t = tetramers[i];
        fout << "T" << right << setfill('0') << setw(5) << (i + 1) << "  Tetramer  "
             << "|O|=" << right << setfill(' ') << setw(2) << t.orbit_size << "  "
             << "s=" << t.s_count << "  "
             << "E=" << right << setfill(' ') << setw(4) << t.energy << "  "
             << format_partition_slash(t.p1) << " [" << get_chirality_sig(t.p1) << "] -> "
             << format_partition_slash(t.p2) << " [" << get_chirality_sig(t.p2) << "] -> "
             << format_partition_slash(t.p3) << " [" << get_chirality_sig(t.p3) << "] -> "
             << format_partition_slash(t.p4) << " [" << get_chirality_sig(t.p4) << "]\n";
    }
    fout.close();

    auto t1 = chrono::high_resolution_clock::now();
    cout << "✓ Exported " << tetramers.size() << " tetramers to " << out_path
         << " in " << chrono::duration_cast<chrono::milliseconds>(t1 - t0).count() / 1000.0 << " s." << endl;

    return 0;
}
