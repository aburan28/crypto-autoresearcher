	.syntax	unified
	.cpu	cortex-m4
	.file	"bench_cm4.s"
	.text

	.equ	SYSCNT_ADDR, 0xE0001004

@ =======================================================================
@ This macro defines a public function ('name') that calls another function
@ ('target') and measures its execution time. That time is returned (in
@ clock cycles). Incoming parameters (up to four registers) are passed
@ through to the target; the target's returned value is discarded.
@ =======================================================================
.macro	BENCH	name, target
	.align	2
	.global	\name
	.thumb
	.thumb_func
\name:
	push.w	{ r10, r11, lr }
	movw	r11, #(SYSCNT_ADDR & 0xFFFF)
	movt	r11, #(SYSCNT_ADDR >> 16)
	ldr.w	r10, [r11]
	bl	\target
	ldr.w	r0, [r11]
	sub.w	r0, r0, r10
	pop	{ r10, r11, pc }
	.size	\name,.-\name
.endm

BENCH	bench_none,    do_nothing
BENCH	bench_of32,    fndsa_fpr_of32
BENCH	bench_scaled,  fndsa_fpr_scaled
BENCH	bench_add,     fndsa_fpr_add
BENCH	bench_sqr,     fndsa_fpr_sqr
BENCH	bench_mul,     fndsa_fpr_mul
BENCH	bench_div,     fndsa_fpr_div
BENCH	bench_sqrt,    fndsa_fpr_sqrt
BENCH	bench_keccak,  fndsa_sha3_process_block
BENCH	bench_NTT,     fndsa_mqpoly_int_to_ntt
BENCH	bench_iNTT,    fndsa_mqpoly_ntt_to_int

@ A do-nothing function, used for calibration. Its inherent cost should
@ be 2 cycles (a single 'bx lr' opcode).
	.align	2
	.thumb
	.thumb_func
	.type	do_nothing, %function
do_nothing:
	bx	lr
	.size	do_nothing,.-do_nothing

@ A special bench function for fndsa_fpr_add_sub, which uses a non-standard
@ ABI and requires the caller to save many more registers.
	.align	2
	.global	bench_add_sub
	.thumb
	.thumb_func
bench_add_sub:
	push.w	{ r4, r5, r6, r7, r8, r10, r11, lr }
	movw	r11, #(SYSCNT_ADDR & 0xFFFF)
	movt	r11, #(SYSCNT_ADDR >> 16)
	vmov	s1, r11
	ldr.w	r10, [r11]
	vmov	s0, r10
	bl	fndsa_fpr_add_sub
	vmov	r11, s1
	ldr.w	r0, [r11]
	vmov	r10, s0
	sub.w	r0, r0, r10
	pop	{ r4, r5, r6, r7, r8, r10, r11, pc }
	.size	bench_add_sub,.-bench_add_sub
