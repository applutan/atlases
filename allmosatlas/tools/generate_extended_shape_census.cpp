#include <iostream>
#include <fstream>
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

struct ShapeResult {
    vector<int> shape;
    uint64_t partitions_count = 0;
    uint64_t mosaics_count = 0;
    map<int, uint64_t> orbit_sizes;
};

struct RingResult {
    int n = 0;
    int group_order = 0;
    uint64_t bell_n = 0;
    uint64_t total_mosaics = 0;
    vector<ShapeResult> shapes;
    map<int, uint64_t> aggregate_orbit_sizes;
};

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

string format_commas(uint64_t val) {
    string s = to_string(val);
    int n = (int)s.length() - 3;
    while (n > 0) {
        s.insert(n, ",");
        n -= 3;
    }
    return s;
}

string format_orbit_poly(const map<int, uint64_t>& orbit_sizes) {
    if (orbit_sizes.empty()) return "$0$";
    vector<string> terms;
    for (auto const& [sz, cnt] : orbit_sizes) {
        if (cnt == 0) continue;
        ostringstream oss;
        oss << format_commas(cnt) << "\\omega^{" << sz << "}";
        terms.push_back(oss.str());
    }
    if (terms.size() <= 5) {
        ostringstream oss;
        oss << "$";
        for (size_t i = 0; i < terms.size(); ++i) {
            if (i > 0) oss << " + ";
            oss << terms[i];
        }
        oss << "$";
        return oss.str();
    } else {
        ostringstream oss;
        oss << "\\begin{tabular}[t]{@{}l@{}} $";
        for (size_t i = 0; i < 4; ++i) {
            if (i > 0) oss << " + ";
            oss << terms[i];
        }
        oss << " + {}$ \\\\ $\\quad ";
        for (size_t i = 4; i < terms.size(); ++i) {
            if (i > 4) oss << " + ";
            oss << terms[i];
        }
        oss << "$ \\end{tabular}";
        return oss.str();
    }
}

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
        vector<uint32_t> sorted_cur(s);
        for (int i = 0; i < s; ++i) sorted_cur[i] = blocks[i];
        sort(sorted_cur.begin(), sorted_cur.end());

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

    vector<vector<int>> raw_shapes;
    vector<int> cur;
    get_integer_partitions(n, n, cur, raw_shapes);

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

        for (int j = 0; j < s; ++j) caps[j] = sh[j];

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

void write_latex_shape_table(const vector<RingResult>& all_rings, const string& filepath) {
    ofstream out(filepath);
    out << "% Auto-generated by generate_extended_shape_census.cpp\n";

    auto emit_table_header = [&](const string& caption_label, const string& caption_title, const string& cont_title) {
        out << "\\begingroup\n\\small\n\\setlength{\\tabcolsep}{5pt}\n";
        out << "\\begin{longtable}{l r r l}\n";
        out << "\\caption{" << caption_label << caption_title << "}\\\\\n";
        out << "\\toprule\n";
        out << "Shape $\\mathbf{z}^\\lambda$ & $\\#p$ & $\\#o$ & Orbit Polynomial $Q_\\lambda(\\omega)$ \\\\\n";
        out << "\\midrule\n\\endfirsthead\n";
        out << "\\caption[]{" << cont_title << "}\\\\\n";
        out << "\\toprule\n";
        out << "Shape $\\mathbf{z}^\\lambda$ & $\\#p$ & $\\#o$ & Orbit Polynomial $Q_\\lambda(\\omega)$ \\\\\n";
        out << "\\midrule\n\\endhead\n";
        out << "\\bottomrule\n\\endfoot\n";
    };

    auto emit_ring_rows = [&](const RingResult& rr, bool emit_subhead) {
        if (emit_subhead) {
            out << "\\midrule\n";
            out << "\\multicolumn{4}{c}{\\textbf{Ring $\\mathbb{Z}_{" << rr.n << "}$}} \\\\\n";
            out << "\\midrule\n";
        }
        for (size_t i = 0; i < rr.shapes.size(); ++i) {
            const auto& sr = rr.shapes[i];
            if (i > 0 && sr.shape.size() != rr.shapes[i-1].shape.size()) {
                out << "\\arrayrulecolor{faintrule}\\midrule[0.25pt]\\arrayrulecolor{black}\n";
            }
            string sh_mon = format_shape_monomial(sr.shape);
            string q_poly = format_orbit_poly(sr.orbit_sizes);
            out << "$" << sh_mon << "$ & " << format_commas(sr.partitions_count) << " & "
                << format_commas(sr.mosaics_count) << " & " << q_poly << " \\\\\n";
        }
    };

    // Table 2.1: Z_1 through Z_6 (29 shapes) on its own page
    out << "\\clearpage\n";
    emit_table_header(
        "\\label{tab:shape-census-z1-z6}",
        "Stratified Partition Shape Inventory for $\\mathbb{Z}_1$ through $\\mathbb{Z}_6$",
        "Stratified Partition Shape Inventory for $\\mathbb{Z}_1$ through $\\mathbb{Z}_6$ (continued)"
    );
    for (int i = 0; i < 6 && i < (int)all_rings.size(); ++i) {
        emit_ring_rows(all_rings[i], true);
    }
    out << "\\bottomrule\n\\end{longtable}\n\\endgroup\n\n";

    // Table 2.2: Z_7 and Z_8 (37 shapes) on its own page
    out << "\\clearpage\n";
    emit_table_header(
        "\\label{tab:shape-census-z7-z8}\\label{tab:shape-census-z7}\\label{tab:shape-census-z8}",
        "Stratified Partition Shape Inventory for $\\mathbb{Z}_7$ and $\\mathbb{Z}_8$",
        "Stratified Partition Shape Inventory for $\\mathbb{Z}_7$ and $\\mathbb{Z}_8$ (continued)"
    );
    for (int i = 6; i < 8 && i < (int)all_rings.size(); ++i) {
        emit_ring_rows(all_rings[i], true);
    }
    out << "\\bottomrule\n\\end{longtable}\n\\endgroup\n\n";

    // Individual tables for Z_9, Z_10, Z_11, Z_12
    for (int i = 8; i < (int)all_rings.size(); ++i) {
        const auto& rr = all_rings[i];
        out << "\\clearpage\n";
        ostringstream cap_lbl, cap_title, cont_title;
        cap_lbl << "\\label{tab:shape-census-z" << rr.n << "}";
        if (rr.n == 12) {
            cap_lbl << "\\label{tab:shape-census-z1-z12}";
        }
        cap_title << "Stratified Partition Shape Inventory for $\\mathbb{Z}_{" << rr.n << "}$";
        cont_title << "Stratified Partition Shape Inventory for $\\mathbb{Z}_{" << rr.n << "}$ (continued)";

        emit_table_header(cap_lbl.str(), cap_title.str(), cont_title.str());
        emit_ring_rows(rr, false);
        out << "\\bottomrule\n\\end{longtable}\n\\endgroup\n\n";
    }

    cout << "✓ Successfully wrote extended shape census to " << filepath << "\n";
}

int main(int argc, char* argv[]) {
    int max_n = 12;
    string out_path = "/home/paul/gemai/atlases/allmosatlas/gen/shape_census_z1_z12.tex";

    if (argc >= 2) max_n = atoi(argv[1]);
    if (argc >= 3) out_path = argv[2];

    vector<RingResult> all_rings;
    for (int n = 1; n <= max_n; ++n) {
        auto t0 = chrono::high_resolution_clock::now();
        RingResult rr = compute_ring(n);
        auto t1 = chrono::high_resolution_clock::now();
        double elapsed = chrono::duration<double>(t1 - t0).count();
        cout << "Ring Z_" << n << " (" << rr.shapes.size() << " shapes, "
             << rr.bell_n << " partitions -> " << rr.total_mosaics << " mosaics) in "
             << fixed << setprecision(3) << elapsed << " s\n";
        all_rings.push_back(rr);
    }

    write_latex_shape_table(all_rings, out_path);
    return 0;
}
