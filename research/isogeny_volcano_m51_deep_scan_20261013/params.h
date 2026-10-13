#ifndef ISOGENY_VOLCANO_M51_DEEP_SCAN_PARAMS_H
#define ISOGENY_VOLCANO_M51_DEEP_SCAN_PARAMS_H

/*
 * Parameters for the m=51 Koblitz isogeny-class candidate sieve.
 *
 * Field: F_2^51 = F_2[z]/(z^51 + z^6 + z^3 + z + 1).
 * Curves: E_b: y^2 + xy = x^3 + b, with b != 0.
 * Target group order: NORD = 130972 * 17192986687.
 *
 * Passing the sieve is not a cardinality or conductor certificate.  Every
 * emitted b requires an independent exact-cardinality and endomorphism-ring
 * computation downstream.
 */
#define M 51
#define RED 0x4bULL
#define ELL 17192986687ULL
#define COF 130972ULL
#define NORD 2251799852369764ULL

#define KNOWN_CRATER_B 1ULL
#define KNOWN_FLOOR_271_B 623162416261ULL

#endif
