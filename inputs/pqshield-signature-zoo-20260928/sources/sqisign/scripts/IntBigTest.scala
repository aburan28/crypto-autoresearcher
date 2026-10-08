/**
 * Code to analyze instrumented code from the SQIsign IntBig module.
 *
 * Features:
 * - verifies arithmetic
 * - aggregate number of errors / ok per function
 * - aggregate minimum / maximum values per function
 *
 * Prerequisite: enable debug output in intbig.x: #define DEBUG_VERBOSE
 * Usage: ./<test app> | scala IntBigTest.scala
 * Usage with unit test: sqisign_test_intbig <reps> <bits> | scala IntBigTest.scala
 *
 * Run option -v: verbose full output
 */

object IntBigTest {

  // Test functions
  object IntBigTestFuns {
    def ibz_add(a: Array[BigInt]) = IntBigRes(a(0) == a(1) + a(2), a(1) + a(2), a)
    def ibz_sub(a: Array[BigInt]) = IntBigRes(a(0) == a(1) - a(2), a(1) - a(2), a)
    def ibz_mul(a: Array[BigInt]) = IntBigRes(a(0) == a(1) * a(2), a(1) * a(2), a)
    def ibz_div(a: Array[BigInt]) = IntBigRes(a(0) == a(2) / a(3) && a(1) == a(2) % a(3), a(2) / a(3), a)
    def ibz_pow_mod(a: Array[BigInt]) = IntBigRes(a(0) == a(1).modPow(a(2), a(3)),  a(1).modPow(a(2), a(3)), a)
    def ibz_cmp(a: Array[BigInt]) = IntBigRes(
      if (a(1) == a(2)) a(0) == 0 else if (a(1) < a(2)) a(0) < 0 else a(0) > 0,
      if (a(1) == a(2)) -1 else if (a(1) < a(2)) 1 else 0,
      a)
    def ibz_is_zero(a: Array[BigInt]) = IntBigRes(if (a(1) == 0) a(0) == 1 else a(0) == 0, if (a(1) == 0) 1 else 0, a)
    def ibz_is_one(a: Array[BigInt]) = IntBigRes(if (a(1) == 1) a(0) == 1 else a(0) == 0, if (a(1) == 1) 1 else 0, a)
    def ibz_probab_prime(a: Array[BigInt]) = IntBigRes(if (a(1).isProbablePrime(a(2).toInt)) a(0) > 0 else a(0) == 0, if (a(1).isProbablePrime(a(2).toInt)) 1 else 0, a)
    def ibz_gcd(a: Array[BigInt]) = IntBigRes(a(1).gcd(a(2)) == a(0), a(1).gcd(a(2)), a)
    def ibz_sqrt_mod_p(in: Array[BigInt]): IntBigRes = {
      val sqrt = in(0)
      val p = in(2)
      val a = if (in(1).mod(p) < 0) p + in(1).mod(p) else in(1).mod(p)
      val exp0 = sqrt.modPow(2, p)
      IntBigRes(exp0 == a || (p - exp0) == a, sqrt.modPow(2, p), in)
    }
    def ibz_sqrt_mod_2p(a: Array[BigInt]): IntBigRes = IntBigRes(a(0).modPow(2, 2 * a(2)) == a(1), a(0), a)

    // mp module (src/mp/ref/generic/mp.c, instrumented with DEBUG_VERBOSE)
    // MUL,out,a,b  =>  out is the exact double-wide product a*b
    def MUL(a: Array[BigInt]) = IntBigRes(a(0) == a(1) * a(2), a(1) * a(2), a)
    // mp_mul,c,a,b,bitwidth  =>  c == (a*b) mod 2^bitwidth (low limbs only)
    // (also used for mp_mul64, whose bitwidth field is 64*nwords)
    def mp_mul(a: Array[BigInt]): IntBigRes = {
      val m = BigInt(2).pow(a(3).toInt)
      IntBigRes(a(0) == (a(1) * a(2)).mod(m), (a(1) * a(2)).mod(m), a)
    }
    // mp_add64,c,a,b,bitwidth  =>  c == (a+b) mod 2^bitwidth
    def mp_add64(a: Array[BigInt]): IntBigRes = {
      val m = BigInt(2).pow(a(3).toInt)
      IntBigRes(a(0) == (a(1) + a(2)).mod(m), (a(1) + a(2)).mod(m), a)
    }
    // mp_inv_2e,b,a,w  =>  (a*b) mod 2^w == 1
    def mp_inv_2e(a: Array[BigInt]): IntBigRes = {
      val m = BigInt(2).pow(a(2).toInt)
      IntBigRes((a(0) * a(1)).mod(m) == 1, BigInt(1), a)
    }
    // mp_invert_matrix,inv(r1,r2,s1,s2),in(r1,r2,s1,s2),w  =>  M_in * M_inv == I mod 2^w
    def mp_invert_matrix(a: Array[BigInt]): IntBigRes = {
      val m = BigInt(2).pow(a(8).toInt)
      val p11 = (a(4) * a(0) + a(5) * a(2)).mod(m)
      val p12 = (a(4) * a(1) + a(5) * a(3)).mod(m)
      val p21 = (a(6) * a(0) + a(7) * a(2)).mod(m)
      val p22 = (a(6) * a(1) + a(7) * a(3)).mod(m)
      IntBigRes(p11 == 1 && p12 == 0 && p21 == 0 && p22 == 1, p11, a)
    }
  }

  val funList = Map(
    //"ibz_add" -> ibz_add _,
    "ibz_sqrt_mod_p" -> IntBigTestFuns.ibz_sqrt_mod_p _,
    "ibz_sqrt_mod_2p" -> IntBigTestFuns.ibz_sqrt_mod_2p _,
    "ibz_add" -> IntBigTestFuns.ibz_add _,
    "ibz_sub" -> IntBigTestFuns.ibz_sub _,
    "ibz_mul" -> IntBigTestFuns.ibz_mul _,
    "ibz_div" -> IntBigTestFuns.ibz_div _,
    "ibz_pow_mod" -> IntBigTestFuns.ibz_pow_mod _,
    "ibz_cmp" -> IntBigTestFuns.ibz_cmp _,
    "ibz_is_zero" -> IntBigTestFuns.ibz_is_zero _,
    "ibz_is_one" -> IntBigTestFuns.ibz_is_one _,
    "ibz_probab_prime" -> IntBigTestFuns.ibz_probab_prime _,
    "ibz_gcd" -> IntBigTestFuns.ibz_gcd _,
    "MUL" -> IntBigTestFuns.MUL _,
    "mp_mul" -> IntBigTestFuns.mp_mul _,
    "mp_inv_2e" -> IntBigTestFuns.mp_inv_2e _,
    "mp_invert_matrix" -> IntBigTestFuns.mp_invert_matrix _,
    // fixed-64-bit-limb routines (same checks; MUL64/mp_mul64 reuse MUL/mp_mul)
    "MUL64" -> IntBigTestFuns.MUL _,
    "mp_mul64" -> IntBigTestFuns.mp_mul _,
    "mp_add64" -> IntBigTestFuns.mp_add64 _
  )

  case class AggregateResults(funName: String, errors: Int, ok: Int, max: Option[Int], min: Option[Int]) {
    def errInc = AggregateResults(funName, errors + 1, ok, max, min)
    def okInc(operands: List[BigInt]) = {
      val operandsBitLen = operands.map(_.bitLength)
      val newMax = Some((max.getOrElse(0) :: operandsBitLen).max)
      val newMin = Some((min.getOrElse(Int.MaxValue) :: operandsBitLen).min)
      AggregateResults(funName, errors, ok + 1, newMax, newMin)
    }

    override def toString: String = s"$funName: $errors errors, $ok ok, max value: ${max.getOrElse(BigInt(0))} bits, min value: ${min.getOrElse(BigInt(0))} bits)"
  }

  def main(args: Array[String]) = {
    val v = args.length >= 1 && args(0) == "-v"
    var err = Map() ++ funList.map(i => (i._1 -> AggregateResults(i._1, 0, 0, None, None)))
    var cont = true
    while (cont) {
      val l = scala.io.StdIn.readLine()
      if (l == null) {
        val numerr =
        err.foreach(i => println(i._2))
        println(s"==========\n${err.values.map(_.errors).sum} errors found\n${err.values.map(_.ok).sum} checks ok")
        cont = false
      } else {
        err = check(l, v, err)
      }
    }
  }

  case class IntBigRes(verif: Boolean, expected: BigInt, got: Array[BigInt])

  def check(line: String, v: Boolean, agg: Map[String, AggregateResults]): Map[String, AggregateResults] = {
    line.split(",").toList match {
      case x :: xs if funList.contains(x) =>
        val funA = xs.map(i => BigInt(i, 16)).toArray
        funList(x)(funA) match {
          case IntBigRes(false, exp, got) =>
            println(s"function: $x\ngot:\n${got.map(_.toString(16)).mkString(",")}\nexpected:\n${exp.toString(16)}")
            agg.map(i => if (i._1 == x) i._1 -> i._2.errInc else i)
          case _ =>
            agg.map(i => if (i._1 == x) i._1 -> i._2.okInc(funA.toList) else i)
        }
      case _ =>
        if (v) println(line)
        agg
    }
  }

}
