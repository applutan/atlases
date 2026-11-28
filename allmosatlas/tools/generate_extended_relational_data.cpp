#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>
#include <iomanip>
#include <algorithm>
#include <map>
#include <unordered_map>
#include <unordered_set>
#include <chrono>
#include <cstdint>
#include <omp.h>

using namespace std;

struct PolyInfo {
    string class_id;
    string composition;
    bool is_achiral = true;
    int orbit_size = 1;
};

struct BlockRecord {
    int n;
    int mosaic_id;
    int block_idx;
    string vertices;
    int size;
    string poly_class;
    string canon_comp;
    string realised_comp;
    int root;
    char chirality;
};

struct MosaicRecord {
    int n;
    int id;
    string shape_str;
    string slash;
    int orbit_size;
    int stab_size;
    int s_count;
    string chirality;
    int energy;
    string poly_profile;
    string manifest;
    vector<BlockRecord> blocks;
};

// Converts an integer subset to a canonical string key for hashing
inline string subset_to_key(int n, const vector<int>& sub) {
    ostringstream oss;
    oss << n << ":";
    for (size_t i = 0; i < sub.size(); ++i) {
        if (i > 0) oss << ",";
        oss << sub[i];
    }
    return oss.str();
}

unordered_map<string, PolyInfo> load_polyatlas(const string& inngons_path, int max_n) {
    unordered_map<string, PolyInfo> poly_map;
    ifstream fin(inngons_path);
    if (!fin.is_open()) {
        cerr << "Error: Could not open " << inngons_path << endl;
        exit(1);
    }
    string line;
    getline(fin, line); // header: composition, class_id, n, k, subset, orbit_size, is_achiral
    while (getline(fin, line)) {
        if (line.empty()) continue;
        stringstream ss(line);
        string comp, class_id, n_str, k_str, subset_slash, orb_sz_str, achiral_str;
        if (!getline(ss, comp, '\t')) continue;
        if (!getline(ss, class_id, '\t')) continue;
        if (!getline(ss, n_str, '\t')) continue;
        if (!getline(ss, k_str, '\t')) continue;
        if (!getline(ss, subset_slash, '\t')) continue;
        if (!getline(ss, orb_sz_str, '\t')) continue;
        if (!getline(ss, achiral_str, '\t')) continue;

        int n = stoi(n_str);
        if (n < 1 || n > max_n) continue;
        int k = stoi(k_str);
        if (k == 0) continue; // skip empty set

        // parse subset hex digits
        vector<int> sub;
        for (char ch : subset_slash) {
            if (ch == '/') continue;
            if (ch >= '0' && ch <= '9') sub.push_back(ch - '0');
            else if (ch >= 'A' && ch <= 'F') sub.push_back(ch - 'A' + 10);
            else if (ch >= 'a' && ch <= 'f') sub.push_back(ch - 'a' + 10);
        }
        sort(sub.begin(), sub.end());

        PolyInfo pi;
        pi.class_id = class_id;
        pi.composition = comp;
        pi.orbit_size = stoi(orb_sz_str);
        pi.is_achiral = (stoi(achiral_str) != 0);

        poly_map[subset_to_key(n, sub)] = pi;
    }
    return poly_map;
}

vector<pair<int, int>> get_dihedral_ops(int n) {
    vector<pair<int, int>> ops;
    if (n == 1) {
        ops.push_back({1, 0});
    } else if (n == 2) {
        ops.push_back({1, 0});
        ops.push_back({1, 1});
    } else {
        for (int a : {1, -1}) {
            for (int b = 0; b < n; ++b) {
                ops.push_back({a, b});
            }
        }
    }
    return ops;
}

vector<int> canonicalise_subset(const vector<int>& subset, int n, const vector<pair<int, int>>& ops) {
    if (subset.empty()) return {};
    vector<int> best;
    for (const auto& op : ops) {
        vector<int> cand(subset.size());
        for (size_t i = 0; i < subset.size(); ++i) {
            int val = (op.first * subset[i] + op.second) % n;
            if (val < 0) val += n;
            cand[i] = val;
        }
        sort(cand.begin(), cand.end());
        if (best.empty() || cand < best) {
            best = cand;
        }
    }
    return best;
}

bool is_block_symmetric(const vector<int>& block, int n) {
    if (n == 1 || block.size() <= 2) return true;
    uint32_t mask = 0;
    for (int x : block) mask |= (1U << x);

    // check reflection involutions: x -> (b - x) % n
    for (int b = 0; b < n; ++b) {
        uint32_t refl = 0;
        for (int x : block) {
            int rx = (b - x) % n;
            if (rx < 0) rx += n;
            refl |= (1U << rx);
        }
        if (refl == mask) return true;
    }
    return false;
}

int compute_block_energy(const vector<int>& block, int n) {
    if (n <= 1) return 0;
    int e = 0;
    int m = (int)block.size();
    for (int i = 0; i < m; ++i) {
        for (int j = i + 1; j < m; ++j) {
            int d = abs(block[j] - block[i]);
            d = min(d, n - d);
            e += d * d;
        }
    }
    return e;
}

string get_block_strides(const vector<int>& block, int n) {
    int m = (int)block.size();
    if (m <= 1) {
        ostringstream oss;
        oss << hex << uppercase << n;
        return oss.str();
    }
    vector<int> sb = block;
    sort(sb.begin(), sb.end());
    ostringstream oss;
    for (int i = 0; i < m; ++i) {
        int diff = (sb[(i + 1) % m] - sb[i]) % n;
        if (diff < 0) diff += n;
        oss << hex << uppercase << diff;
    }
    return oss.str();
}

string format_slash(const vector<vector<int>>& part) {
    ostringstream oss;
    oss << "/";
    for (const auto& blk : part) {
        for (int x : blk) {
            oss << hex << uppercase << x;
        }
        oss << "/";
    }
    return oss.str();
}

vector<vector<int>> canonicalise_partition(const vector<vector<int>>& part, int n, const vector<pair<int, int>>& ops) {
    vector<vector<int>> best;
    for (const auto& op : ops) {
        vector<vector<int>> cand(part.size());
        for (size_t i = 0; i < part.size(); ++i) {
            cand[i].resize(part[i].size());
            for (size_t j = 0; j < part[i].size(); ++j) {
                int val = (op.first * part[i][j] + op.second) % n;
                if (val < 0) val += n;
                cand[i][j] = val;
            }
            sort(cand[i].begin(), cand[i].end());
        }
        sort(cand.begin(), cand.end(), [](const vector<int>& a, const vector<int>& b) {
            if (a[0] != b[0]) return a[0] < b[0];
            return a < b;
        });

        if (best.empty() || cand < best) {
            best = cand;
        }
    }
    return best;
}

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

void backtrack_collect_partitions(
    int x,
    int n,
    int s,
    const vector<int>& blk_sizes,
    int caps[],
    int blk_lens[],
    uint32_t blocks[],
    vector<vector<uint32_t>>& raw_parts
) {
    if (x == n) {
        vector<uint32_t> cur(s);
        for (int i = 0; i < s; ++i) cur[i] = blocks[i];
        sort(cur.begin(), cur.end());
        raw_parts.push_back(cur);
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

            backtrack_collect_partitions(
                x + 1, n, s, blk_sizes, caps, blk_lens, blocks, raw_parts
            );

            blocks[b] ^= (1U << x);
            blk_lens[b]--;
            caps[b]++;
        }
    }
}

int main(int argc, char* argv[]) {
    int max_n = 12;
    string inngons_path = "/home/paul/gemai/atlases/polyatlas/data/inngons.tsv";
    string out_dir = "/home/paul/gemai/atlases/allmosatlas/data";

    if (argc >= 2) max_n = atoi(argv[1]);
    if (argc >= 3) inngons_path = argv[2];
    if (argc >= 4) out_dir = argv[3];

    cout << "================================================================================" << endl;
    cout << "HIGH-PERFORMANCE RELATIONAL MOSAIC ENGINE (Z_1..Z_" << max_n << ")" << endl;
    cout << "================================================================================" << endl;

    cout << "Loading polyatlas reference from: " << inngons_path << endl;
    auto poly_map = load_polyatlas(inngons_path, max_n);
    cout << "✓ Loaded " << poly_map.size() << " polygon orbits from polyatlas." << endl;

    vector<MosaicRecord> all_mosaics;
    int global_id = 1;

    for (int n = 1; n <= max_n; ++n) {
        auto t0 = chrono::high_resolution_clock::now();
        auto d_ops = get_dihedral_ops(n);
        int group_order = (int)d_ops.size();

        vector<vector<int>> raw_shapes;
        vector<int> cur;
        get_integer_partitions(n, n, cur, raw_shapes);

        // Sort shapes: part count s ascending, then shape descending
        sort(raw_shapes.begin(), raw_shapes.end(), [](const vector<int>& a, const vector<int>& b) {
            if (a.size() != b.size()) return a.size() < b.size();
            return a > b;
        });

        int num_shapes = (int)raw_shapes.size();
        vector<vector<MosaicRecord>> shape_results(num_shapes);

        #pragma omp parallel for schedule(dynamic, 1)
        for (int i = 0; i < num_shapes; ++i) {
            const auto& sh = raw_shapes[i];
            int s = (int)sh.size();
            vector<int> blk_sizes = sh;
            int caps[32];
            int blk_lens[32] = {0};
            uint32_t blocks[32] = {0};
            for (int j = 0; j < s; ++j) caps[j] = sh[j];

            vector<vector<uint32_t>> raw_parts;
            backtrack_collect_partitions(0, n, s, blk_sizes, caps, blk_lens, blocks, raw_parts);

            unordered_set<string> seen_slashes;
            vector<MosaicRecord> cur_shape_mosaics;

            for (const auto& rpart : raw_parts) {
                // Convert bitmask partition to vector<vector<int>>
                vector<vector<int>> part(s);
                for (int b = 0; b < s; ++b) {
                    for (int x = 0; x < n; ++x) {
                        if ((rpart[b] >> x) & 1) part[b].push_back(x);
                    }
                }

                auto canon = canonicalise_partition(part, n, d_ops);
                string slash = format_slash(canon);

                if (seen_slashes.find(slash) == seen_slashes.end()) {
                    seen_slashes.insert(slash);

                    // Compute stabiliser order
                    int stab_order = 0;
                    for (const auto& op : d_ops) {
                        vector<vector<int>> trans(s);
                        for (int b = 0; b < s; ++b) {
                            trans[b].resize(canon[b].size());
                            for (size_t j = 0; j < canon[b].size(); ++j) {
                                int val = (op.first * canon[b][j] + op.second) % n;
                                if (val < 0) val += n;
                                trans[b][j] = val;
                            }
                            sort(trans[b].begin(), trans[b].end());
                        }
                        sort(trans.begin(), trans.end(), [](const vector<int>& a, const vector<int>& b) {
                            if (a[0] != b[0]) return a[0] < b[0];
                            return a < b;
                        });
                        if (trans == canon) stab_order++;
                    }

                    int orb_sz = group_order / stab_order;
                    int s_count = 0;
                    string sig = "";
                    int energy = 0;
                    vector<string> poly_classes;
                    vector<string> manifest_tokens;
                    vector<BlockRecord> blk_records;

                    for (int b = 0; b < s; ++b) {
                        const auto& blk = canon[b];
                        bool sym = is_block_symmetric(blk, n);
                        if (sym) s_count++;
                        sig += (sym ? "s" : "c");
                        energy += compute_block_energy(blk, n);

                        // Polyatlas matching
                        auto canon_sub = canonicalise_subset(blk, n, d_ops);
                        string pkey = subset_to_key(n, canon_sub);
                        auto it = poly_map.find(pkey);
                        if (it == poly_map.end()) {
                            cerr << "FATAL: subset not found in polyatlas: n=" << n << " key=" << pkey << endl;
                            exit(1);
                        }
                        const auto& pinfo = it->second;
                        poly_classes.push_back(pinfo.class_id);

                        int root = blk[0];
                        string realised_comp = get_block_strides(blk, n);

                        // Chirality check
                        bool direct_match = false;
                        for (int rot = 0; rot < n; ++rot) {
                            vector<int> trans(canon_sub.size());
                            for (size_t j = 0; j < canon_sub.size(); ++j) {
                                trans[j] = (canon_sub[j] + rot) % n;
                            }
                            sort(trans.begin(), trans.end());
                            if (trans == blk) {
                                direct_match = true;
                                break;
                            }
                        }

                        char chir = '+';
                        if (!pinfo.is_achiral && !direct_match) {
                            chir = '-';
                        }

                        ostringstream token_oss;
                        token_oss << pinfo.class_id << "@" << root << chir << ":" << realised_comp;
                        manifest_tokens.push_back(token_oss.str());

                        ostringstream vert_oss;
                        for (int x : blk) vert_oss << hex << uppercase << x;

                        BlockRecord br;
                        br.n = n;
                        br.mosaic_id = 0; // will be assigned
                        br.block_idx = b + 1;
                        br.vertices = vert_oss.str();
                        br.size = (int)blk.size();
                        br.poly_class = pinfo.class_id;
                        br.canon_comp = pinfo.composition;
                        br.realised_comp = realised_comp;
                        br.root = root;
                        br.chirality = chir;
                        blk_records.push_back(br);
                    }

                    sort(poly_classes.begin(), poly_classes.end());
                    ostringstream prof_oss;
                    for (size_t k = 0; k < poly_classes.size(); ++k) {
                        if (k > 0) prof_oss << "+";
                        prof_oss << poly_classes[k];
                    }

                    ostringstream man_oss;
                    for (size_t k = 0; k < manifest_tokens.size(); ++k) {
                        if (k > 0) man_oss << "/";
                        man_oss << manifest_tokens[k];
                    }

                    ostringstream sh_oss;
                    sh_oss << "(";
                    for (size_t k = 0; k < sh.size(); ++k) {
                        if (k > 0) sh_oss << ",";
                        sh_oss << sh[k];
                    }
                    sh_oss << ")";

                    MosaicRecord mr;
                    mr.n = n;
                    mr.id = 0; // will be assigned
                    mr.shape_str = sh_oss.str();
                    mr.slash = slash;
                    mr.orbit_size = orb_sz;
                    mr.stab_size = stab_order;
                    mr.s_count = s_count;
                    mr.chirality = sig;
                    mr.energy = energy;
                    mr.poly_profile = prof_oss.str();
                    mr.manifest = man_oss.str();
                    mr.blocks = blk_records;

                    cur_shape_mosaics.push_back(mr);
                }
            }

            // Sort within shape: descending s_count, descending energy, ascending slash
            sort(cur_shape_mosaics.begin(), cur_shape_mosaics.end(), [](const MosaicRecord& a, const MosaicRecord& b) {
                if (a.s_count != b.s_count) return a.s_count > b.s_count;
                if (a.energy != b.energy) return a.energy > b.energy;
                return a.slash < b.slash;
            });

            shape_results[i] = cur_shape_mosaics;
        }

        int local_id = 1;
        int ring_mosaics = 0;
        for (int i = 0; i < num_shapes; ++i) {
            for (auto& mr : shape_results[i]) {
                mr.id = local_id++;
                for (auto& br : mr.blocks) {
                    br.mosaic_id = mr.id;
                }
                all_mosaics.push_back(mr);
                ring_mosaics++;
            }
        }

        auto t1 = chrono::high_resolution_clock::now();
        double elapsed = chrono::duration<double>(t1 - t0).count();
        cout << "Ring Z_" << n << ": " << ring_mosaics << " mosaics extracted in "
             << fixed << setprecision(3) << elapsed << " s" << endl;
    }

    cout << "--------------------------------------------------------------------------------" << endl;
    cout << "Total extracted: " << all_mosaics.size() << " mosaics across Z_1..Z_" << max_n << endl;
    cout << "--------------------------------------------------------------------------------" << endl;

    // Write TSV and CSV files
    string m_tsv = out_dir + "/mosaics.tsv";
    string m_csv = out_dir + "/mosaics.csv";
    string b_tsv = out_dir + "/mosaic_blocks.tsv";
    string b_csv = out_dir + "/mosaic_blocks.csv";

    cout << "Writing " << m_tsv << " and " << m_csv << "..." << endl;
    ofstream fout_m_tsv(m_tsv);
    ofstream fout_m_csv(m_csv);

    fout_m_tsv << "n\tid\tshape\tslash\torbit_size\tstab_size\ts_count\tchirality\tenergy\tpoly_profile\tmanifest\n";
    fout_m_csv << "n,id,shape,slash,orbit_size,stab_size,s_count,chirality,energy,poly_profile,manifest\n";

    for (const auto& mr : all_mosaics) {
        fout_m_tsv << mr.n << "\t" << mr.id << "\t" << mr.shape_str << "\t" << mr.slash << "\t"
                   << mr.orbit_size << "\t" << mr.stab_size << "\t" << mr.s_count << "\t"
                   << mr.chirality << "\t" << mr.energy << "\t" << mr.poly_profile << "\t"
                   << mr.manifest << "\n";

        fout_m_csv << mr.n << "," << mr.id << ",\"" << mr.shape_str << "\"," << mr.slash << ","
                   << mr.orbit_size << "," << mr.stab_size << "," << mr.s_count << ","
                   << mr.chirality << "," << mr.energy << ",\"" << mr.poly_profile << "\",\""
                   << mr.manifest << "\"\n";
    }

    cout << "Writing " << b_tsv << " and " << b_csv << "..." << endl;
    ofstream fout_b_tsv(b_tsv);
    ofstream fout_b_csv(b_csv);

    fout_b_tsv << "n\tmosaic_id\tblock_idx\tvertices\tsize\tpoly_class\tcanon_comp\trealised_comp\troot\tchirality\n";
    fout_b_csv << "n,mosaic_id,block_idx,vertices,size,poly_class,canon_comp,realised_comp,root,chirality\n";

    uint64_t total_blocks = 0;
    for (const auto& mr : all_mosaics) {
        for (const auto& br : mr.blocks) {
            total_blocks++;
            fout_b_tsv << br.n << "\t" << br.mosaic_id << "\t" << br.block_idx << "\t"
                       << br.vertices << "\t" << br.size << "\t" << br.poly_class << "\t"
                       << br.canon_comp << "\t" << br.realised_comp << "\t" << br.root << "\t"
                       << br.chirality << "\n";

            fout_b_csv << br.n << "," << br.mosaic_id << "," << br.block_idx << ","
                       << br.vertices << "," << br.size << "," << br.poly_class << ","
                       << br.canon_comp << "," << br.realised_comp << "," << br.root << ","
                       << br.chirality << "\n";
        }
    }

    cout << "✓ Successfully wrote " << all_mosaics.size() << " mosaics and " << total_blocks << " blocks." << endl;
    return 0;
}
