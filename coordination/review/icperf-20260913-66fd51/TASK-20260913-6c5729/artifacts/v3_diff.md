## per-cell median diffs (summary.json cells vs validator)

- cells/n15l5/S/m2_f4_cpu_s: summary=None validator=MISSING
- cells/n15l5/U/m2_f4_cpu_s: summary=None validator=MISSING
- cells/n17l6/S/m2_f4_cpu_s: summary=None validator=MISSING
- cells/n17l6/U/m2_f4_cpu_s: summary=None validator=MISSING
- cells/n19l6/S/m2_f4_cpu_s: summary=None validator=MISSING
- cells/n19l6/U/m2_f4_cpu_s: summary=None validator=MISSING

## prediction-value diffs

| where | summary.json | validator | same |
|---|---|---|---|
| P1.holds | False | False | True |
| P1.n_sat_answers | 205 | 205 | True |
| P1.unverified | [('n19l6-19-U', 'wdsat', 'default'), ('n19l6-19-U', 'wdsat', 'core_order'), ('n19l6-19-U', 'wdsat', 'symmetry'), ('n19l6-19-U', 'wdsat', 'gauss_elim'), ('n19l6-19-U', 'cryptominisat5', 'cnf_xor')] | [('n19l6-19-U', 'wdsat', 'default'), ('n19l6-19-U', 'wdsat', 'core_order'), ('n19l6-19-U', 'wdsat', 'symmetry'), ('n19l6-19-U', 'wdsat', 'gauss_elim'), ('n19l6-19-U', 'cryptominisat5', 'cnf_xor')] | True |
| P2.holds | None | None | True |
| P3.core_order_identity.holds | True | True | True |
| n15l5/S/noncore_first_over_default_wall_censored.noncore_lb | 14.2562 | 14.2562 | True |
| n15l5/S/noncore_first_over_default_wall_censored.default_wall_s | 0.0652 | 0.0652 | True |
| n15l5/S/noncore_first_over_default_wall_censored.ratio | 218.65337423312886 | 218.65337423312886 | True |
| n15l5/U/noncore_first_over_default_wall_censored.noncore_lb | 120.0 | 120 | True |
| n15l5/U/noncore_first_over_default_wall_censored.default_wall_s | 0.2159 | 0.2159 | True |
| n15l5/U/noncore_first_over_default_wall_censored.ratio | 555.812876331635 | 555.812876331635 | True |
| n17l6/S/noncore_first_over_default_wall_censored.noncore_lb | 120.0 | 120 | True |
| n17l6/S/noncore_first_over_default_wall_censored.default_wall_s | 0.116 | 0.116 | True |
| n17l6/S/noncore_first_over_default_wall_censored.ratio | 1034.4827586206895 | 1034.4827586206895 | True |
| n17l6/U/noncore_first_over_default_wall_censored.noncore_lb | 120.0 | 120 | True |
| n17l6/U/noncore_first_over_default_wall_censored.default_wall_s | 2.3218 | 2.3218 | True |
| n17l6/U/noncore_first_over_default_wall_censored.ratio | 51.6840382461883 | 51.6840382461883 | True |
| n19l6/S/noncore_first_over_default_wall_censored.noncore_lb | 120.0 | 120 | True |
| n19l6/S/noncore_first_over_default_wall_censored.default_wall_s | 0.0651 | 0.0651 | True |
| n19l6/S/noncore_first_over_default_wall_censored.ratio | 1843.3179723502303 | 1843.3179723502303 | True |
| n19l6/U/noncore_first_over_default_wall_censored.noncore_lb | 120.0 | 120 | True |
| n19l6/U/noncore_first_over_default_wall_censored.default_wall_s | 2.3718 | 2.3718 | True |
| n19l6/U/noncore_first_over_default_wall_censored.ratio | 50.59448520111308 | 50.59448520111308 | True |
| n17l6/S/cms_pure_cnf_over_wdsat.ratio(vs matched) | 83.50030889840438 | 26.070689655172412 | False |
| n17l6/S/cms_pure_cnf_over_wdsat.ratio(vs all10) | 83.50030889840438 | 10.39601237538673 | False |
| n17l6/U/cms_pure_cnf_over_wdsat.ratio(vs matched) | 83.50030889840438 | 34.468128176414844 | False |
| n17l6/U/cms_pure_cnf_over_wdsat.ratio(vs all10) | 83.50030889840438 | 34.47183993452649 | False |
| n19l6/S/cms_pure_cnf_over_wdsat.ratio(vs matched) | 83.50030889840438 | 327.66359447004606 | False |
| n19l6/S/cms_pure_cnf_over_wdsat.ratio(vs all10) | 83.50030889840438 | 67.46015180265655 | False |
| n19l6/U/cms_pure_cnf_over_wdsat.ratio(vs matched) | 83.50030889840438 | 82.62897377519184 | False |
| n19l6/U/cms_pure_cnf_over_wdsat.ratio(vs all10) | 83.50030889840438 | 83.50030889840438 | True |
| P3.holds | True | True | True |
| P4.n15l5/S.gauss_elim | 0.2656 | 0.2656 | True |
| P4.n15l5/S.default | 0.06509999999999999 | 0.06509999999999999 | True |
| P4.n15l5/S.holds | True | True | True |
| P4.n15l5/U.gauss_elim | 1.1183 | 1.1183 | True |
| P4.n15l5/U.default | 0.21595 | 0.21595 | True |
| P4.n15l5/U.holds | True | True | True |
| P4.n17l6/S.gauss_elim | 1.8455000000000001 | 1.8455000000000001 | True |
| P4.n17l6/S.default | 0.2909 | 0.2909 | True |
| P4.n17l6/S.holds | True | True | True |
| P4.n17l6/U.gauss_elim | 16.70675 | 16.70675 | True |
| P4.n17l6/U.default | 2.3215500000000002 | 2.3215500000000002 | True |
| P4.n17l6/U.holds | True | True | True |
| P4.n19l6/S.gauss_elim | 1.9952 | 1.9952 | True |
| P4.n19l6/S.default | 0.3162 | 0.3162 | True |
| P4.n19l6/S.holds | True | True | True |
| P4.n19l6/U.gauss_elim | 16.506300000000003 | 16.506300000000003 | True |
| P4.n19l6/U.default | 2.34705 | 2.34705 | True |
| P4.n19l6/U.holds | True | True | True |
| P4.holds | True | True | True |
| P5.n15l5/wdsat.ratio | 3.6263974246414983 | 3.6263974246414983 | True |
| P5.n15l5/cms_xor.ratio | 11.44833251191063 | 11.44833251191063 | True |
| P5.n15l5/cms_xor.S | 12174.0 | 12174.0 | True |
| P5.n15l5/cms_xor.U | 139372.0 | 139372.0 | True |
| P5.n17l6/wdsat.ratio | 6.688813301113679 | 6.688813301113679 | True |
| P5.n17l6/cms_xor.ratio | 3.670751902076449 | 3.670751902076449 | True |
| P5.n17l6/cms_xor.S | 196561.5 | 196561.5 | True |
| P5.n17l6/cms_xor.U | 721528.5 | 721528.5 | True |
| P5.n19l6/wdsat.ratio | 6.106072564636101 | 6.106072564636101 | True |
| P5.n19l6/cms_xor.ratio | 6.452198868323515 | 6.452198868323515 | True |
| P5.n19l6/cms_xor.S | 215167.5 | 215167.5 | True |
| P5.n19l6/cms_xor.U | 1388303.5 | 1388303.5 | True |
| P5.holds | True | True | True |
| P6.n15l5.null_median | 3540911.5 | 3630846.0 | False |
| P6.n15l5.U_median | 30978.5 | 30978.5 | True |
| P6.n15l5.ratio | 114.30222573720484 | 117.20535209903643 | False |
| P6.n17l6.null_median | 5109609.75 | 5539684 | False |
| P6.n17l6.U_median | 254656.5 | 254656.5 | True |
| P6.n17l6.ratio | 20.06471364367295 | 21.753554297651934 | False |
| P6.n19l6.null_median | None | None | True |
| P6.n19l6.U_median | 255301.0 | 255301.0 | True |
| P6.n19l6.ratio | None | None | True |
| P6.holds (summary) vs validator literal every-cell | True | False | False |
| P6.holds (summary) vs validator ignoring null cells | True | True | True |
