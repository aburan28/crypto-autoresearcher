# m3closure PILOT summary (INTERIM, exploratory, not program evidence)

Status at handback: background drivers still running (driver1: n11/n13 + nulls; driver2 queued: n9 dense null, n15, rand-V, n17; driver19: n19 W4). Tables below are a snapshot; rerun `python3 summarize.py` to refresh data.csv/tables.md.

## Host
nproc=4; RAM=15 GB; M4RI libm4ri 0.0.20200125 (apt); gcc 13.3; numpy 2.4.6; Python 3.11.15

## Single-instance probes (tmp/probe13.txt, tmp/probe17.txt; run concurrently with other jobs)
```
13 unsat 0 M4 completed one False rank 5541 cols 24158 rows 5668 its 2 dims [0, 1, 48, 1069, 4423] std 380960 ev [] mm 0 wall 1.1 rss 70
13 unsat 0 W3 completed one False rank 967 cols 3683 rows 1736 its 4 dims [0, 1, 48, 918] std None ev [] mm 0 wall 0.1 rss 32
13 unsat 0 W4 completed one True rank 24158 cols 24158 rows 78826 its 5 dims [1, 28, 378, 3276, 20475] std None ev [] mm 0 wall 41.3 rss 412
13 unsat 0 myW4 completed one True rank 24109 cols 24158 rows 72164 its 0 dims [1, 21, 336, 3276, 20475] std None ev [] mm None wall 14.1 rss 81
13 sat 12 M4 completed one False rank 5541 cols 24158 rows 5668 its 2 dims [0, 1, 48, 1069, 4423] std 384672 ev [0, 0, 0] mm 0 wall 1.0 rss 70
13 sat 12 W3 completed one False rank 967 cols 3683 rows 1736 its 4 dims [0, 1, 48, 918] std None ev [0, 0, 0] mm 0 wall 0.1 rss 32
13 sat 12 W4 completed one False rank 24146 cols 24158 rows 181198 its 6 dims [0, 19, 376, 3276, 20475] std 12 ev [0, 0, 0] mm 0 wall 78.9 rss 769
13 sat 12 myW4 completed one False rank 24146 cols 24158 rows 102788 its 0 dims [0, 19, 376, 3276, 20475] std None ev [0, 0, 0] mm None wall 72.9 rss 81
17 unsat 0 M4 completed one False rank 11140 cols 59536 rows 11339 its 2 dims [0, 1, 62, 1765, 9312] std None ev [] mm 0 wall 7.0 rss 283
17 unsat 0 W4 completed one True rank 59536 cols 59536 rows 169991 its 6 dims [1, 35, 595, 6545, 52360] std None ev [] mm 0 wall 498.2 rss 1889
17 sat 6 M4 completed one False rank 11140 cols 59536 rows 11339 its 2 dims [0, 1, 62, 1765, 9312] std None ev [0, 0, 0] mm 0 wall 7.0 rss 283
17 sat 6 W4 completed one False rank 59530 cols 59536 rows 480685 its 7 dims [0, 31, 594, 6545, 52360] std 6 ev [0, 0, 0] mm 0 wall 1035.4 rss 4667
```

## Tables (snapshot)
### Target census (enumeration labels, all labelled targets incl. not run)

| cell | q | targets | unique | UNSAT | SAT | enum agree (curve vs Boolean) | eval at zeros ok |
|---|---|---|---|---|---|---|---|
| m2ctrl | - | 60 | 60 | 25 | 35 | 60/60 | 60/60 |
| n11-poly | 997 | 150 | 133 | 96 | 37 | 150/150 | 150/150 |
| n13-poly | 4133 | 150 | 144 | 47 | 97 | 150/150 | 150/150 |
| n13-rand | 4133 | 100 | 99 | 47 | 52 | 100/100 | 100/100 |
| n15-poly | 16249 | 150 | 149 | 127 | 22 | 150/150 | 150/150 |
| n17-poly | 65843 | 150 | 149 | 103 | 46 | 150/150 | 150/150 |
| n17-rand | 65843 | 100 | 100 | 68 | 32 | 100/100 | 100/100 |
| n19-poly | 262007 | 40 | 40 | 21 | 19 | 40/40 | 40/40 |
| n9-poly | 271 | 150 | 91 | 83 | 8 | 150/150 | 150/150 |
| n9-rand | 271 | 100 | 69 | 59 | 10 | 100/100 | 100/100 |

### Refutation of UNSAT instances, false refutation of SAT instances (libclosure / M4RI unless 'my')

| cell | family | task | UNSAT refuted [CP95] | SAT refuted (must be 0) | censored/errors |
|---|---|---|---|---|---|
| m2ctrl | M2CTRL | M_3 | 0/25 [0.00,0.14] | 0/35 | 0 |
| m2ctrl | M2CTRL | M_4 | 22/25 [0.69,0.97] | 0/35 | 0 |
| m2ctrl | M2CTRL | W_3 | 25/25 [0.86,1.00] | 0/35 | 0 |
| m2ctrl | M2CTRL | W_4 | 25/25 [0.86,1.00] | 0/35 | 0 |
| m2ctrl | M2CTRL | myM_4 | 22/25 [0.69,0.97] | 0/35 | 0 |
| m2ctrl | M2CTRL | myW_4 | 25/25 [0.86,1.00] | 0/35 | 0 |
| n9-poly | NULL | M_3 | 0/11 [0.00,0.28] | 0/29 | 0 |
| n9-poly | NULL | M_4 | 0/11 [0.00,0.28] | 0/29 | 0 |
| n9-poly | NULL | M_5 | 0/11 [0.00,0.28] | 0/29 | 0 |
| n9-poly | NULL | W_3 | 1/11 [0.00,0.41] | 0/29 | 0 |
| n9-poly | NULL | W_4 | 11/11 [0.72,1.00] | 0/29 | 0 |
| n9-poly | NULL | W_5 | 11/11 [0.72,1.00] | 0/29 | 0 |
| n9-poly | NULL | myW_4 | 11/11 [0.72,1.00] | 0/29 | 0 |
| n9-poly | S3 | M_3 | 0/60 [0.00,0.06] | 0/8 | 0 |
| n9-poly | S3 | M_4 | 0/60 [0.00,0.06] | 0/8 | 0 |
| n9-poly | S3 | M_5 | 0/60 [0.00,0.06] | 0/8 | 0 |
| n9-poly | S3 | M_6 | 60/60 [0.94,1.00] | 0/8 | 0 |
| n9-poly | S3 | W_3 | 0/60 [0.00,0.06] | 0/8 | 0 |
| n9-poly | S3 | W_4 | 60/60 [0.94,1.00] | 0/8 | 0 |
| n9-poly | S3 | W_5 | 20/20 [0.83,1.00] | 0/8 | 0 |
| n9-poly | S3 | myM_4 | 0/60 [0.00,0.06] | 0/8 | 0 |
| n9-poly | S3 | myM_5 | 0/20 [0.00,0.17] | 0/8 | 0 |
| n9-poly | S3 | myW_4 | 60/60 [0.94,1.00] | 0/8 | 0 |
| n9-poly | S3 | myW_5 | 20/20 [0.83,1.00] | 0/8 | 0 |
| n11-poly | S3 | M_3 | 0/34 [0.00,0.10] | 0/0 | 0 |
| n11-poly | S3 | M_4 | 0/34 [0.00,0.10] | 0/0 | 0 |
| n11-poly | S3 | M_5 | 0/33 [0.00,0.11] | 0/0 | 0 |
| n11-poly | S3 | W_3 | 0/33 [0.00,0.11] | 0/0 | 0 |
| n11-poly | S3 | W_4 | 33/33 [0.89,1.00] | 0/0 | 0 |
| n19-poly | S3 | M_4 | 0/1 [0.00,0.98] | 0/0 | 0 |
| n19-poly | S3 | W_3 | 0/1 [0.00,0.98] | 0/0 | 0 |

### Minimal refuting degree per UNSAT instance (among degrees computed)

| cell | family | closure | distribution of min D (instances) |
|---|---|---|---|
| m2ctrl | M2CTRL | M_D | D=4: 22, D=>4 (computed [3, 4]): 3 |
| m2ctrl | M2CTRL | W_D | D=3: 25 |
| n9-poly | NULL | M_D | D=>5 (computed [3, 4, 5]): 11 |
| n9-poly | NULL | W_D | D=3: 1, D=4: 10 |
| n9-poly | S3 | M_D | D=6: 60 |
| n9-poly | S3 | W_D | D=4: 60 |
| n11-poly | S3 | M_D | D=>4 (computed [3, 4]): 1, D=>5 (computed [3, 4, 5]): 33 |
| n11-poly | S3 | W_D | D=4: 33 |
| n19-poly | S3 | M_D | D=>4 (computed [4]): 1 |
| n19-poly | S3 | W_D | D=>3 (computed [3]): 1 |

### SAT instances: does W_D determine the solution set? (codim(W_D in B_<=D) == #solutions)

| cell | family | task | codim == nsol | standard monomials == nsol | eval rows not vanishing at known zeros (total) | evalcheck mismatches |
|---|---|---|---|---|---|---|
| m2ctrl | M2CTRL | M_3 | 0/35 | 0/35 | 0 | 0 |
| m2ctrl | M2CTRL | M_4 | 0/35 | 0/35 | 0 | 0 |
| m2ctrl | M2CTRL | W_3 | 35/35 | 35/35 | 0 | 0 |
| m2ctrl | M2CTRL | W_4 | 35/35 | 35/35 | 0 | 0 |
| m2ctrl | M2CTRL | myM_4 | 0/35 | 0/0 | 0 | 0 |
| m2ctrl | M2CTRL | myW_4 | 35/35 | 0/0 | 0 | 0 |
| n9-poly | NULL | M_3 | 0/29 | 0/29 | 0 | 0 |
| n9-poly | NULL | M_4 | 0/29 | 0/29 | 0 | 0 |
| n9-poly | NULL | M_5 | 0/29 | 0/29 | 0 | 0 |
| n9-poly | NULL | W_3 | 0/29 | 0/29 | 0 | 0 |
| n9-poly | NULL | W_4 | 29/29 | 29/29 | 0 | 0 |
| n9-poly | NULL | W_5 | 29/29 | 29/29 | 0 | 0 |
| n9-poly | NULL | myW_4 | 29/29 | 0/0 | 0 | 0 |
| n9-poly | S3 | M_3 | 0/8 | 0/8 | 0 | 0 |
| n9-poly | S3 | M_4 | 0/8 | 0/8 | 0 | 0 |
| n9-poly | S3 | M_5 | 0/8 | 0/8 | 0 | 0 |
| n9-poly | S3 | M_6 | 0/8 | 8/8 | 0 | 0 |
| n9-poly | S3 | W_3 | 0/8 | 0/8 | 0 | 0 |
| n9-poly | S3 | W_4 | 8/8 | 8/8 | 0 | 0 |
| n9-poly | S3 | W_5 | 8/8 | 8/8 | 0 | 0 |
| n9-poly | S3 | myM_4 | 0/8 | 0/0 | 0 | 0 |
| n9-poly | S3 | myM_5 | 0/8 | 0/0 | 0 | 0 |
| n9-poly | S3 | myW_4 | 8/8 | 0/0 | 0 | 0 |
| n9-poly | S3 | myW_5 | 8/8 | 0/0 | 0 | 0 |

### Cross-check libclosure (M4RI 0.0.20200125) vs independent eliminator (myclosure.c)

| cell | pair | instances | contains_one agree | rank+dims agree (non-refuted, or M_D) |
|---|---|---|---|---|
| m2ctrl M2CTRL | M_4 vs myM_4 | 60 | 60/60 | 60/60 |
| m2ctrl M2CTRL | W_4 vs myW_4 | 60 | 60/60 | 35/35 |
| n9-poly NULL | W_4 vs myW_4 | 40 | 40/40 | 29/29 |
| n9-poly S3 | M_4 vs myM_4 | 68 | 68/68 | 68/68 |
| n9-poly S3 | M_5 vs myM_5 | 28 | 28/28 | 28/28 |
| n9-poly S3 | W_4 vs myW_4 | 68 | 68/68 | 8/8 |
| n9-poly S3 | W_5 vs myW_5 | 28 | 28/28 | 8/8 |

### Matrix sizes, wall time and peak RSS (libclosure, completed runs; medians [min-max])

| cell | family | task | sat | count | ncols | max rows | final rank | basis nnz | iterations | wall s | peak RSS MB |
|---|---|---|---|---|---|---|---|---|---|---|---|
| m2ctrl | M2CTRL | M_3 | 0 | 25 | 988 | 323 [323-323] | 321 [321-321] | 14744 [13831-15244] | 1 [1-1] | 0.0 [0.0-0.0] | 34 [34-35] |
| m2ctrl | M2CTRL | M_3 | 1 | 35 | 988 | 323 [323-323] | 321 [319-321] | 14720 [13879-15473] | 1 [1-1] | 0.0 [0.0-0.0] | 35 [34-35] |
| m2ctrl | M2CTRL | M_4 | 0 | 25 | 4048 | 2924 [2924-2924] | 2672 [2670-2674] | 24600 [22114-27270] | 1 [1-1] | 0.1 [0.1-0.1] | 34 [34-35] |
| m2ctrl | M2CTRL | M_4 | 1 | 35 | 4048 | 2924 [2924-2924] | 2671 [2645-2672] | 25994 [23665-60480] | 1 [1-1] | 0.1 [0.1-0.1] | 35 [34-35] |
| m2ctrl | M2CTRL | W_3 | 0 | 25 | 988 | 1728 [1728-1728] | 988 [988-988] | 988 [988-988] | 3 [3-3] | 0.0 [0.0-0.0] | 34 [34-35] |
| m2ctrl | M2CTRL | W_3 | 1 | 35 | 988 | 4181 [3493-4631] | 986 [982-986] | 1494 [1021-2504] | 4 [4-4] | 0.0 [0.0-0.0] | 35 [34-35] |
| m2ctrl | M2CTRL | W_4 | 0 | 25 | 4048 | 3740 [3740-3740] | 3047 [3047-3047] | 17753 [17753-17753] | 1 [1-1] | 0.1 [0.1-0.1] | 34 [34-35] |
| m2ctrl | M2CTRL | W_4 | 1 | 35 | 4048 | 56952 [53000-56952] | 4046 [4042-4046] | 5242 [4084-8576] | 3 [3-3] | 0.7 [0.6-1.0] | 86 [83-87] |
| n9-poly | NULL | M_3 | 0 | 11 | 988 | 180 [180-180] | 180 [180-180] | 4942 [2802-5479] | 1 [1-1] | 0.0 [0.0-0.0] | 33 [32-33] |
| n9-poly | NULL | M_3 | 1 | 29 | 988 | 180 [180-198] | 180 [180-198] | 4882 [3039-5488] | 1 [1-1] | 0.0 [0.0-0.0] | 33 [33-33] |
| n9-poly | NULL | M_4 | 0 | 11 | 4048 | 1719 [1719-1719] | 1655 [1646-1658] | 38576 [23050-43513] | 1 [1-1] | 0.1 [0.0-0.1] | 33 [32-33] |
| n9-poly | NULL | M_4 | 1 | 29 | 4048 | 1719 [1719-1872] | 1653 [1644-1800] | 39923 [25633-73478] | 1 [1-1] | 0.1 [0.0-0.1] | 33 [33-33] |
| n9-poly | NULL | M_5 | 0 | 11 | 12616 | 10440 [10440-10440] | 8741 [8671-8756] | 448596 [335005-602908] | 1 [1-1] | 1.1 [0.8-1.7] | 84 [84-84] |
| n9-poly | NULL | M_5 | 1 | 29 | 12616 | 10440 [10440-11256] | 8722 [8667-9347] | 484542 [379646-873441] | 1 [1-1] | 1.4 [0.9-2.0] | 84 [72-84] |
| n9-poly | NULL | W_3 | 0 | 11 | 988 | 2203 [180-2798] | 845 [180-988] | 3612 [988-5479] | 7 [2-10] | 0.0 [0.0-0.1] | 33 [32-33] |
| n9-poly | NULL | W_3 | 1 | 29 | 988 | 1660 [180-2867] | 765 [180-911] | 3955 [1373-5863] | 6 [2-7] | 0.0 [0.0-0.1] | 33 [33-33] |
| n9-poly | NULL | W_4 | 0 | 11 | 4048 | 22966 [16178-30637] | 4045 [4032-4048] | 4048 [4033-4112] | 3 [3-4] | 1.0 [0.7-1.4] | 60 [43-69] |
| n9-poly | NULL | W_4 | 1 | 29 | 4048 | 25136 [18545-36874] | 4046 [4007-4047] | 4606 [4062-8195] | 5 [4-6] | 1.3 [0.9-1.8] | 56 [48-64] |
| n9-poly | NULL | W_5 | 0 | 11 | 12616 | 277172 [205660-313488] | 12614 [12595-12616] | 12615 [12595-12616] | 2 [2-2] | 41.0 [28.6-51.9] | 767 [580-857] |
| n9-poly | NULL | W_5 | 1 | 29 | 12616 | 246401 [207972-305000] | 12614 [12575-12615] | 13558 [12630-20379] | 4 [3-4] | 55.2 [46.7-61.4] | 684 [583-840] |
| n9-poly | S3 | M_3 | 0 | 60 | 988 | 180 [180-180] | 179 [179-179] | 3242 [2855-3480] | 1 [1-1] | 0.0 [0.0-0.1] | 33 [32-33] |
| n9-poly | S3 | M_3 | 1 | 8 | 988 | 180 [180-180] | 179 [179-179] | 3209 [2816-3495] | 1 [1-1] | 0.0 [0.0-0.0] | 33 [33-33] |
| n9-poly | S3 | M_4 | 0 | 60 | 4048 | 1719 [1719-1719] | 1633 [1633-1633] | 63845 [58916-66468] | 1 [1-1] | 0.1 [0.0-0.1] | 33 [32-33] |
| n9-poly | S3 | M_4 | 1 | 8 | 4048 | 1719 [1719-1719] | 1633 [1633-1634] | 63079 [57695-66500] | 1 [1-1] | 0.1 [0.0-0.1] | 33 [33-33] |
| n9-poly | S3 | M_5 | 0 | 60 | 12616 | 10440 [10440-10440] | 8595 [8595-8595] | 508347 [493908-525219] | 1 [1-1] | 1.2 [0.8-1.9] | 84 [84-84] |
| n9-poly | S3 | M_5 | 1 | 8 | 12616 | 10440 [10440-10440] | 8595 [8595-8602] | 508470 [479353-518660] | 1 [1-1] | 1.1 [0.8-1.5] | 85 [84-85] |
| n9-poly | S3 | M_6 | 0 | 60 | 31180 | 45324 [45324-45324] | 27298 [27298-27298] | 44191 [44191-44191] | 1 [1-1] | 21.5 [18.3-26.1] | 426 [426-428] |
| n9-poly | S3 | M_6 | 1 | 8 | 31180 | 45324 [45324-45324] | 27294 [27287-27295] | 55647 [48758-88408] | 1 [1-1] | 20.6 [16.9-21.5] | 426 [426-427] |
| n9-poly | S3 | W_3 | 0 | 60 | 988 | 1609 [1609-2059] | 823 [823-838] | 4148 [2706-4882] | 5 [5-5] | 0.1 [0.0-0.1] | 33 [33-33] |
| n9-poly | S3 | W_3 | 1 | 8 | 988 | 1609 [1609-2059] | 823 [823-845] | 4002 [3434-4574] | 5 [5-5] | 0.0 [0.0-0.1] | 33 [33-33] |
| n9-poly | S3 | W_4 | 0 | 60 | 4048 | 25481 [25462-26297] | 4045 [4041-4046] | 4075 [4046-4178] | 2 [2-2] | 0.6 [0.4-1.0] | 47 [47-51] |
| n9-poly | S3 | W_4 | 1 | 8 | 4048 | 33762 [27599-34855] | 4044 [4037-4045] | 6675 [5841-13201] | 4 [3-4] | 1.1 [0.8-1.3] | 71 [69-72] |
| n9-poly | S3 | W_5 | 0 | 20 | 12616 | 300618 [300618-301434] | 12616 [12616-12616] | 12616 [12616-12616] | 2 [2-2] | 43.9 [41.3-50.2] | 836 [805-843] |
| n9-poly | S3 | W_5 | 1 | 8 | 12616 | 300618 [300618-310594] | 12612 [12605-12613] | 18522 [15702-35319] | 3 [3-3] | 58.9 [44.7-62.6] | 832 [823-864] |
| n11-poly | S3 | M_3 | 0 | 34 | 2048 | 275 [275-275] | 274 [274-274] | 7929 [7004-8287] | 1 [1-1] | 0.0 [0.0-0.1] | 33 [32-33] |
| n11-poly | S3 | M_4 | 0 | 34 | 10903 | 3311 [3311-3311] | 3215 [3215-3215] | 248100 [225710-255277] | 1 [1-1] | 0.2 [0.1-0.4] | 37 [36-37] |
| n11-poly | S3 | M_5 | 0 | 33 | 44552 | 25575 [25575-25575] | 22759 [22759-22759] | 7430288 [7201074-7789756] | 1 [1-1] | 16.8 [12.5-28.2] | 441 [441-442] |
| n11-poly | S3 | W_3 | 0 | 33 | 2048 | 1185 [1185-1185] | 667 [667-667] | 21899 [21253-22837] | 3 [3-3] | 0.1 [0.0-0.1] | 33 [32-33] |
| n11-poly | S3 | W_4 | 0 | 33 | 10903 | 36893 [36893-40581] | 10787 [10787-10797] | 149275 [136690-156591] | 3 [3-3] | 6.3 [4.3-10.8] | 128 [127-155] |
| n19-poly | S3 | M_4 | 0 | 1 | 102091 | 16378 [16378-16378] | 16136 [16136-16136] | 6786453 [6786453-6786453] | 1 [1-1] | 27.3 [27.3-27.3] | 666 [666-666] |
| n19-poly | S3 | W_3 | 0 | 1 | 10701 | 3600 [3600-3600] | 2021 [2021-2021] | 489920 [489920-489920] | 3 [3-3] | 0.3 [0.3-0.3] | 41 [41-41] |

### Growth of per-attempt W_4 refutation cost vs l = k (S3, poly V, UNSAT, refuted runs)


log2(wall s): per-k medians k=3: -0.65 (n_inst=60), k=4: 2.66 (n_inst=33)
OLS slope over instances (k in [3, 4]): 3.35 bits per unit l, bootstrap 95% CI [3.23, 3.46] (resampling instances within each k; 2 sizes)
local slopes (medians): k 3->4: 3.31

log2(max rows x ncols): per-k medians k=3: 26.62 (n_inst=60), k=4: 28.58 (n_inst=33)
OLS slope over instances (k in [3, 4]): 2.00 bits per unit l, bootstrap 95% CI [1.98, 2.02] (resampling instances within each k; 2 sizes)
local slopes (medians): k 3->4: 1.96

## Code hashes
```
a152a07b824b16b355ca5e38aa29f7b93e2c18ca66f9ad9109daecfc2ca6bb42  pilot.py
b06beff5e251e224d2d8e3a4323bce2c9c8f5b3e4645f0243a5e1c3dbb1df87b  pilot_lib.py
ba79d353a5f8aa28fa631b46ea613d597bb42c7bb6b487caa82f60b229eaa110  worker.py
629c2720887b28ec74bd41f76e8bd1904dfdb1a062cfe68c466999903298d3d4  summarize.py
da32ba3a62c3683f218f99d26e5ac1cc05a1030b9a5275c7abd8d942447071ff  count_affu.c
ce2b374fea675ccd09edbefb1f710294cedebfac983848db22b7896c075a7221  myclosure.c
70d12e8f0c082b8d96ef9ed223b8163ef97dd8baa2493b018bc6b87594312d02  driver1.sh
853deaa2b61f9068cea3e9adc5b752d2517dbf8577f66a0e18a41b6da0066a47  driver2.sh
8d1888af72907750045ebfa07bca1ce1c053c6d773d70144678908e5c19eb4ea  driver19.sh
497fcbce098ac917c0858bd2e841077bd5738d98094d375a8e1ed8b131e4a474  vendor/boolsys.py
0edcab87851b7d0fc4d2f7a2afc936699a256955cd51c2f5e3413156ccf80a85  vendor/closure_cert.py
ec7d70d5a48951c28f2b6dbedefbab19d2eaf92fc471172b1787db34ff893acc  vendor/curve.py
805790da8fda86c72a710515ed279ebfb4a8d04645151ad1ad900f80ab9477a3  vendor/gf2_chained_builder.py
5d1e3a6d37f66709008a60ae1e44caea59bce21624fd0f27ed5c0b5c396eda0a  vendor/gf2n.py
fb50e265c05a957226d1b673ee6ef55937be50a267877b11398115b1ae7659f3  vendor/closure.c
4d6ece6638c03328121f091a40ea0acdbf590fe27b32c81c86232e4db1254284  vendor/gf2_echelon.c
042552e04863953482a579e5f46131b1e1e86be9b7920e56029aee3bb8f2c1e5  vendor/Makefile
4e3bacec50c05977a4a858075dd83546955a1a66ac1fdb64d7ab570d7d9d493f  vendor/PATCH_boolsys.diff
a7f655452f171ac91d86f39ba57076ee2e2ea04256ca98265d3bb05141e1aa4b  data.csv

55d0063a0bb6ad7faa96952d7aa5d04aaae123fe61e2712a81a725a1c7853bb6  experiments/EXP-SEMBIN-7e1371/code/boolsys.py
fb50e265c05a957226d1b673ee6ef55937be50a267877b11398115b1ae7659f3  experiments/EXP-SEMBIN-7e1371/code/closure.c
0edcab87851b7d0fc4d2f7a2afc936699a256955cd51c2f5e3413156ccf80a85  experiments/EXP-SEMBIN-7e1371/code/closure_cert.py
4d6ece6638c03328121f091a40ea0acdbf590fe27b32c81c86232e4db1254284  experiments/EXP-SEMBIN-7e1371/code/gf2_echelon.c
042552e04863953482a579e5f46131b1e1e86be9b7920e56029aee3bb8f2c1e5  experiments/EXP-SEMBIN-7e1371/code/Makefile
805790da8fda86c72a710515ed279ebfb4a8d04645151ad1ad900f80ab9477a3  harness/macaulay_fp/fixtures/gf2_chained_builder.py
ec7d70d5a48951c28f2b6dbedefbab19d2eaf92fc471172b1787db34ff893acc  experiments/EXP-CERTBIN-060020/impl/curve.py
5d1e3a6d37f66709008a60ae1e44caea59bce21624fd0f27ed5c0b5c396eda0a  experiments/EXP-CERTBIN-060020/impl/gf2n.py
```
