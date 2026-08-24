import unittest
from .ledger_checks import (
  EXPECTED_COUNTS, check_obligation_ledger, check_memory_map_status,
  check_classification, check_mutation_status, check_no_invented_numerics,
)

class TestPackage(unittest.TestCase):
  def test_counts(self):
    r=check_obligation_ledger()
    self.assertTrue(r["edge_counts_ok"]); self.assertTrue(r["package_ok"])
    self.assertEqual(r["item_count"], EXPECTED_COUNTS["total_items"])
  def test_memory_map(self):
    r=check_memory_map_status(); self.assertTrue(r["passed"])
  def test_classification(self):
    r=check_classification(); self.assertTrue(r["passed"])
  def test_mutation(self):
    r=check_mutation_status(); self.assertTrue(r["passed"])
  def test_no_numerics(self):
    r=check_no_invented_numerics(); self.assertTrue(r["passed"]); self.assertEqual(r["hits"], [])
