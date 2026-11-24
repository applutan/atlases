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
#include <cmath>

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

vector<uint16_t> all_blocks;
int block_to_id[65536];
uint16_t d_table[32][1820];
uint16_t mu3_table[1820];
bool is_sym_table[1820];
int chord_energy_table[1820];
BlockStride stride_table[1820];
vector<vector<int>> block_vertices;

// Precomputed trigonometry for 16-gon vertices (radius 1.0)
float trig_cos[16];
float trig_sin[16];

void init_tables() {
    for(int k = 0; k < 16; ++k) {
        float angle = (90.0f - k * 22.5f) * (M_PI / 180.0f);
        trig_cos[k] = cos(angle);
        trig_sin[k] = sin(angle);
    }

    for(int m = 0; m < 65536; ++m) {
        if(__builtin_popcount(m) == 4) {
            block_to_id[m] = all_blocks.size();
            all_blocks.push_back(m);
        } else {
            block_to_id[m] = -1;
        }
    }

    block_vertices.resize(all_blocks.size());
    for(size_t i = 0; i < all_blocks.size(); ++i) {
        uint16_t m = all_blocks[i];
        vector<int> v;
        for(int k = 0; k < 16; ++k) if((m >> k) & 1) v.push_back(k);
        block_vertices[i] = v;

        bool sym = false;
        for(int c = 0; c < 16; ++c) {
            uint16_t ref_m = 0;
            for(int x : v) ref_m |= (1 << ((-x + c + 160) % 16));
            if(ref_m == m) { sym = true; break; }
        }
        is_sym_table[i] = sym;

        int E = 0;
        for(int a = 0; a < 4; ++a) {
            for(int b = a + 1; b < 4; ++b) {
                int d = min((v[b] - v[a] + 16) % 16, (v[a] - v[b] + 16) % 16);
                E += d * d;
            }
        }
        chord_energy_table[i] = E;

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

void render_single_mosaic(ostream& out, float cx, float cy, float r, const Partition& part) {
    // 16-gon boundary wireframe
    out << "    \\draw[gray!35, line width=0.20pt] ";
    for(int k = 0; k < 16; ++k) {
        float vx = cx + r * trig_cos[k];
        float vy = cy + r * trig_sin[k];
        out << "(" << fixed << setprecision(2) << vx << "," << vy << ")" << (k == 15 ? " -- cycle;\n" : " -- ");
    }

    // 4 blocks
    for(int blk_idx = 0; blk_idx < 4; ++blk_idx) {
        int b_id = part.b[blk_idx];
        const auto& v = block_vertices[b_id];
        const char* col = is_sym_table[b_id] ? "mosaicblue" : "mosaicpink";

        out << "    \\fill[" << col << ", fill opacity=0.62] ";
        for(int k = 0; k < 4; ++k) {
            float vx = cx + r * trig_cos[v[k]];
            float vy = cy + r * trig_sin[v[k]];
            out << "(" << fixed << setprecision(2) << vx << "," << vy << ")" << (k == 3 ? " -- cycle;\n" : " -- ");
        }

        out << "    \\draw[black!85, line width=0.25pt] ";
        for(int k = 0; k < 4; ++k) {
            float vx = cx + r * trig_cos[v[k]];
            float vy = cy + r * trig_sin[v[k]];
            out << "(" << fixed << setprecision(2) << vx << "," << vy << ")" << (k == 3 ? " -- cycle;\n" : " -- ");
        }
    }
}

void render_cartouche(ostream& out, float cx, float cy, int id, int orb_sz,
                      const Partition& p1, const Partition& p2, const Partition& p3, const Partition& p4) {
    const float r = 0.28f;
    const float d_inner = 0.68f;
    const float pad_x = 0.38f;
    const float pad_y = 0.18f;
    const float w_half = 1.5f * d_inner + pad_x; // 1.02 + 0.38 = 1.40 cm
    const float h_half = r + pad_y;              // 0.28 + 0.18 = 0.46 cm

    float bx1 = cx - w_half;
    float bx2 = cx + w_half;
    float by1 = cy - h_half;
    float by2 = cy + h_half;

    out << "  \\draw[draw=blue!20!black!25, fill=blue!1.5!black!0.8, rounded corners=3.5pt, line width=0.35pt] "
        << "(" << fixed << setprecision(2) << bx1 << "," << by1 << ") rectangle (" << bx2 << "," << by2 << ");\n";

    // Badges
    out << "  \\node[anchor=west, fill=white, draw=blue!30!black!30, rounded corners=1.5pt, inner sep=1.0pt, font=\\tiny\\bfseries\\sffamily] at ("
        << bx1 + 0.10f << "," << by2 << ") {" << id << "};\n";
    out << "  \\node[anchor=east, font=\\tiny\\color{black!50}] at ("
        << bx2 - 0.10f << "," << by1 + 0.10f << ") {" << orb_sz << "};\n";

    // 4 mosaics: p1, p2, p3, p4
    render_single_mosaic(out, cx - 1.5f * d_inner, cy, r, p1);
    render_single_mosaic(out, cx - 0.5f * d_inner, cy, r, p2);
    render_single_mosaic(out, cx + 0.5f * d_inner, cy, r, p3);
    render_single_mosaic(out, cx + 1.5f * d_inner, cy, r, p4);
}

void write_part_tex(const string& filename, const vector<Tetramer>& tetramers,
                    size_t start_idx, size_t end_idx) {
    ofstream out(filename);
    out << "% Tetramers Atlas Plate Part\n"
        << "\\documentclass[11pt,a4paper]{article}\n"
        << "\\usepackage[utf8]{inputenc}\n"
        << "\\usepackage{amsmath,amssymb}\n"
        << "\\usepackage{geometry}\n"
        << "\\geometry{a4paper, margin=1.2cm, top=2.5cm, bottom=1.5cm}\n"
        << "\\usepackage{tikz}\n"
        << "\\usetikzlibrary{calc}\n"
        << "\\colorlet{mosaicblue}{blue!30}\n"
        << "\\colorlet{mosaicpink}{red!25}\n"
        << "\\pagestyle{empty}\n"
        << "\\begin{document}\n\n";

    const float col_x[4] = {2.30f, 6.70f, 11.10f, 15.50f};
    const float row_dy = 1.05f;

    size_t curr = start_idx;
    while(curr < end_idx) {
        out << "\\noindent\\makebox[\\textwidth][c]{\\begin{tikzpicture}[>=latex, line join=round, line cap=round, scale=1.0]\n";

        for(int row = 0; row < 24 && curr < end_idx; ++row) {
            float cy = -(row * row_dy);
            for(int col = 0; col < 4 && curr < end_idx; ++col) {
                float cx = col_x[col];
                const auto& t = tetramers[curr];
                int id = curr + 1;
                render_cartouche(out, cx, cy, id, t.orbit_size, t.p1, t.p2, t.p3, t.p4);
                curr++;
            }
        }

        out << "\\end{tikzpicture}}\\clearpage\n\n";
    }

    out << "\\end{document}\n";
    out.close();
    cout << "✓ Wrote " << filename << " (Tetramers " << start_idx + 1 << ".." << end_idx << ")" << endl;
}

int main() {
    auto t0 = chrono::high_resolution_clock::now();
    cout << "Initializing combinatorial lookup tables..." << endl;
    init_tables();

    cout << "Generating raw partitions..." << endl;
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

    vector<bool> visited(d_orbits.size(), false);
    vector<Tetramer> tetramers;

    for(size_t i = 0; i < d_orbits.size(); ++i) {
        if(visited[i]) continue;
        Partition o1 = d_orbits[i].first;
        int sz = d_orbits[i].second;

        Partition o2 = canonicalize_d(apply_mu3(o1)).first;
        if(o2 == o1) { visited[i] = true; continue; }

        Partition o3 = canonicalize_d(apply_mu3(o2)).first;
        if(o3 == o1) {
            visited[i] = true;
            visited[orbit_lookup[p_hash(o2)]] = true;
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
    cout << "Sorted " << tetramers.size() << " tetramers." << endl;

    // Divide 20,721 into 4 parts (54 pages each: 54 * 96 = 5184 per part)
    // Part 1: 0..5184 (54 pp)
    // Part 2: 5184..10368 (54 pp)
    // Part 3: 10368..15552 (54 pp)
    // Part 4: 15552..20721 (54 pp, last page has 81 items)
    const size_t part_size = 54 * 96; // 5184
    write_part_tex("unimosatlas/plates/tetramers_part1.tex", tetramers, 0, part_size);
    write_part_tex("unimosatlas/plates/tetramers_part2.tex", tetramers, part_size, 2 * part_size);
    write_part_tex("unimosatlas/plates/tetramers_part3.tex", tetramers, 2 * part_size, 3 * part_size);
    write_part_tex("unimosatlas/plates/tetramers_part4.tex", tetramers, 3 * part_size, tetramers.size());

    auto t1 = chrono::high_resolution_clock::now();
    cout << "✓ All 4 LaTeX part files generated in "
         << chrono::duration_cast<chrono::milliseconds>(t1 - t0).count() / 1000.0 << " s." << endl;

    return 0;
}
