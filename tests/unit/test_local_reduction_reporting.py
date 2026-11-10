"""A safe reduction still has supporting obligations to establish."""

import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace

from chc.proof.CFunctionPO import CFunctionPO
from chc.proof.CProofDependencies import CProofDependencies
from chc.reporting.ProofObligations import get_method_count


class LocalReductionReportingTest(unittest.TestCase):
    def obligation(self, deps, local=False):
        assumptions = SimpleNamespace(
            get_assumption_type=lambda index: SimpleNamespace(
                is_local_assumption=local,
                is_api_assumption=not local,
            )
        )
        node = ET.fromstring(f'<po s="g" deps="{deps}" ids="1"/>')
        return CFunctionPO(
            None,
            SimpleNamespace(pod=assumptions),
            status="safe",
            deps=CProofDependencies(None, node),
        )

    def test_reduced_obligation_remains_open_in_report(self):
        obligation = self.obligation("r", local=True)
        self.assertTrue(obligation.is_safe)
        self.assertEqual(obligation.get_display_prefix(), "<R>")
        counts = get_method_count([obligation])
        self.assertEqual(counts["open"], 1)
        self.assertEqual(counts["local"], 0)

    def test_external_dependency_can_include_local_requirement(self):
        obligation = self.obligation("a", local=True)
        self.assertEqual(get_method_count([obligation])["open"], 1)

    def test_plain_local_and_api_dispositions(self):
        local = self.obligation("f")
        delegated = self.obligation("a")
        counts = get_method_count([local, delegated])
        self.assertEqual(counts["local"], 1)
        self.assertEqual(counts["api"], 1)
        self.assertEqual(counts["open"], 0)


if __name__ == "__main__":
    unittest.main()
