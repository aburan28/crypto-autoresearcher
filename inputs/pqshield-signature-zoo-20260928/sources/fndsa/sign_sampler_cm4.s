	.syntax	unified
	.cpu	cortex-m4
	.file	"sign_sampler_cm4.s"
	.text

@ =======================================================================
@ int32_t fndsa_gaussian0_helper(uint64_t lo, uint32_t hi)
@ =======================================================================

	.align	2
	.global	fndsa_gaussian0_helper
	.thumb
	.thumb_func
	.type	fndsa_gaussian0_helper, %function
fndsa_gaussian0_helper:
	push.w	{ r4, r5, r6, r7, r8, r10 }

	adr.w	r12, fndsa_gaussian0_helper__gauss0_low

	@ 0 and 1
	ldm	r12!, { r4, r5, r6, r7 }
	subs	r8, r0, r4
	sbcs	r8, r1, r5
	sbcs	r8, r2, #163  @ high[0]
	lsr.w	r3, r8, #31
	subs	r8, r0, r6
	sbcs	r8, r1, r7
	sbcs	r8, r2, #84   @ high[1]
	add.w	r3, r3, r8, lsr #31

	@ 2 and 3
	ldm	r12!, { r4, r5, r6, r7 }
	subs	r8, r0, r4
	sbcs	r8, r1, r5
	sbcs	r8, r2, #34   @ high[2]
	add.w	r3, r3, r8, lsr #31
	subs	r8, r0, r6
	sbcs	r8, r1, r7
	sbcs	r8, r2, #10   @ high[3]
	add.w	r3, r3, r8, lsr #31

	@ 4 and 5
	ldm	r12!, { r4, r5, r6, r7 }
	subs	r8, r0, r4
	sbcs	r8, r1, r5
	sbcs	r8, r2, #2    @ high[4]
	add.w	r3, r3, r8, lsr #31

	@ Subsequent values are less than 2^63, thus they can modify the
	@ result only if r2 = 0 and r1 < 2^31; in that case the top bit of
	@ the subtraction of r1 is correct. We will keep making the
	@ operations, but omitting the third subtraction, and accumulating
	@ bits into r10.
	movw	r10, #0

	subs	r8, r0, r6
	sbcs	r8, r1, r7
	@sbcs	r8, r2, #0    @ high[5]
	add.w	r10, r10, r8, lsr #31

	@ 6 and 7
	ldm	r12!, { r4, r5, r6, r7 }
	subs	r8, r0, r4
	sbcs	r8, r1, r5
	@sbcs	r8, r2, #0    @ high[6]
	add.w	r10, r10, r8, lsr #31
	subs	r8, r0, r6
	sbcs	r8, r1, r7
	@sbcs	r8, r2, #0    @ high[7]
	add.w	r10, r10, r8, lsr #31

	@ 8 and 9
	ldm	r12!, { r4, r5, r6, r7 }
	subs	r8, r0, r4
	sbcs	r8, r1, r5
	@sbcs	r8, r2, #0    @ high[8]
	add.w	r10, r10, r8, lsr #31
	subs	r8, r0, r6
	sbcs	r8, r1, r7
	@sbcs	r8, r2, #0    @ high[9]
	add.w	r10, r10, r8, lsr #31

	@ 10, 11 and 12
	ldm	r12!, { r4, r5, r6, r7 }
	subs	r8, r0, r4
	sbcs	r8, r1, r5
	@sbcs	r8, r2, #0    @ high[10]
	add.w	r10, r10, r8, lsr #31
	subs	r8, r0, r6
	sbcs	r8, r1, #148  @ mid[11]
	@sbcs	r8, r2, #0    @ high[11]
	add.w	r10, r10, r8, lsr #31
	subs	r8, r0, r7
	sbcs	r8, r1, #3    @ mid[12]
	@sbcs	r8, r2, #0    @ high[12]
	add.w	r10, r10, r8, lsr #31

	@ 13, 14, 15, 16
	ldm	r12!, { r4, r5, r6, r7 }
	subs	r8, r0, r4
	sbcs	r8, r1, #0    @ mid[13]
	@sbcs	r8, r2, #0    @ high[13]
	add.w	r10, r10, r8, lsr #31
	subs	r8, r0, r5
	sbcs	r8, r1, #0    @ mid[14]
	@sbcs	r8, r2, #0    @ high[14]
	add.w	r10, r10, r8, lsr #31
	subs	r8, r0, r6
	sbcs	r8, r1, #0    @ mid[15]
	@sbcs	r8, r2, #0    @ high[15]
	add.w	r10, r10, r8, lsr #31
	subs	r8, r0, r7
	sbcs	r8, r1, #0    @ mid[16]
	@sbcs	r8, r2, #0    @ high[16]
	add.w	r10, r10, r8, lsr #31

	@ 17
	ldr.w	r4, [r12]
	subs	r8, r0, r4
	sbcs	r8, r1, #0    @ mid[17]
	@sbcs	r8, r2, #0    @ high[17]
	add.w	r10, r10, r8, lsr #31

	@ Result is split into r10 and r3. If r2 != 0 or r1 >= 2^31, then
	@ result in r10 is incorrect and must be cleared.
	orr	r2, r2, r1, lsr #31
	sub	r2, #1
	and	r10, r10, r2, asr #31
	add	r0, r3, r10

	@mov.w	r0, r3
	pop	{ r4, r5, r6, r7, r8, r10 }
	bx	lr
	.align	3
fndsa_gaussian0_helper__gauss0_low:
	@ This is the RCDT table from the specification. Only the low 64 bits
	@ of each value are stored here; the high 8 bits are provided in
	@ comments but otherwise hardcoded in the instructions above.
	.word	2889422850, 4159975123  @ high: 163
	.word	1065212802, 3542816799  @ high:  84
	.word	1210696191, 2110640275  @ high:  34
	.word	3348712164, 3514123127  @ high:  10
	.word	4081000303, 2508483758  @ high:   2
	.word	3983850847, 2001389396  @ high:   0
	.word	 729246436,  270851412  @ high:   0
	.word	1705862106,   27394012  @ high:   0
	.word	2323342376,    2064600  @ high:   0
	.word	2986609769,     115709  @ high:   0
	.word	 617624059,       4815  @ high:   0
	@ Starting at value 11, we only store the low 32 bits.
	.word	2676689183  @ mid: 148    high:   0
	.word	1717414296  @ mid:   3    high:   0
	.word	 247426747  @ mid:   0    high:   0
	.word	   3104126  @ mid:   0    high:   0
	.word	     28824  @ mid:   0    high:   0
	.word	       198  @ mid:   0    high:   0
	.word	         1  @ mid:   0    high:   0
	.size	fndsa_gaussian0_helper,.-fndsa_gaussian0_helper

@ =======================================================================
@ void fndsa_ffsamp_fft_inner(sampler_state *ss, unsigned logn, fpr *tmp)
@ =======================================================================

	.align	2
	.global	fndsa_ffsamp_fft_inner
	.thumb
	.thumb_func
	.type	fndsa_ffsamp_fft_inner, %function
fndsa_ffsamp_fft_inner:
	@ We mimic the C implementation (sign_sampler.c); this function
	@ is in assembly so that we can optimize its stack allocation
	@ (GCC uses about 80 bytes per call level, which is a lot, since
	@ this is the main recursive function).

	@ If logn == 1, we tail-call fndsa_ffsamp_fft_deepest
	cmp	r1, #1
	bne	fndsa_ffsamp_fft_inner__L1
	mov.w	r1, r2
	b.w	fndsa_ffsamp_fft_deepest

fndsa_ffsamp_fft_inner__L1:
	push	{ r4, r5, r6, lr }

	@ r4 <- ss
	@ r5 <- logn
	@ r6 <- tmp
	movs	r4, r0
	movs	r5, r1
	movs	r6, r2

	@ Write into rd the address tmp + off*(n/4), expressed in 8-byte
	@ chunk (hence, tmp + 2*off*n, when counting in bytes).
.macro QC  rd, off
	.if ((\off) == 0)
	mov.w	\rd, r6
	.else
	movs	\rd, #(2 * (\off))
	lsls	\rd, r5
	add.w	\rd, \rd, r6
	.endif
.endm

	@ Decompose G into LDL; the decomposed matrix replaces G.
	mov.w	r0, r5
	QC	r1, 12
	QC	r2, 8
	QC	r3, 14
	bl	fndsa_fpoly_LDL_fft

	@ Split d11 into the right sub-tree (right_00, right_01);
	@ right_11 is a copy of right_00.
	mov.w	r0, r5
	QC	r1, 20
	QC	r2, 18
	QC	r3, 14
	bl	fndsa_fpoly_split_selfadj_fft
	QC	r0, 21
	QC	r1, 20
	movs	r2, #2
	lsls	r2, r5
	bl	memcpy

	@ Split t1 and make the first recursive call on the two
	@ halves, using the right sub-tree, then merge the result
	@ into 18..21
	mov.w	r0, r5
	QC	r1, 14
	QC	r2, 16
	QC	r3, 4
	bl	fndsa_fpoly_split_fft
	movs	r0, r4
	subs	r1, r5, #1
	QC	r2, 14
	bl	fndsa_ffsamp_fft_inner
	mov.w	r0, r5
	QC	r1, 18
	QC	r2, 14
	QC	r3, 16
	bl	fndsa_fpoly_merge_fft

	@ Compute tb0 = t0 + (t1 - z1)*l10 (into t0) and move z1 into t1.
	QC	r0, 14
	QC	r1, 4
	movs	r2, #8
	lsls	r2, r5
	bl	memcpy
	mov.w	r0, r5
	QC	r1, 14
	QC	r2, 18
	bl	fndsa_fpoly_sub
	QC	r0, 4
	QC	r1, 18
	movs	r2, #8
	lsls	r2, r5
	bl	memcpy
	mov.w	r0, r5
	QC	r1, 14
	QC	r2, 8
	bl	fndsa_fpoly_mul_fft
	mov.w	r0, r5
	QC	r1, 0
	QC	r2, 14
	bl	fndsa_fpoly_add

	@ Split d00 to obtain the left-subtree.
	mov.w	r0, r5
	QC	r1, 20
	QC	r2, 18
	QC	r3, 12
	bl	fndsa_fpoly_split_selfadj_fft
	QC	r0, 21
	QC	r1, 20
	movs	r2, #2
	lsls	r2, r5
	bl	memcpy

	@ Split tb0 and perform the second recursive call on the
	@ split output; the final merge produces z0, which we write
	@ into t0.
	mov.w	r0, r5
	QC	r1, 14
	QC	r2, 16
	QC	r3, 0
	bl	fndsa_fpoly_split_fft
	movs	r0, r4
	subs	r1, r5, #1
	QC	r2, 14
	bl	fndsa_ffsamp_fft_inner
	mov.w	r0, r5
	QC	r1, 0
	QC	r2, 14
	QC	r3, 16
	bl	fndsa_fpoly_merge_fft

	pop	{ r4, r5, r6, pc }
	.size	fndsa_ffsamp_fft_inner,.-fndsa_ffsamp_fft_inner
