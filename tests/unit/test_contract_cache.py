"""Repeated contract reads must preserve every formal and condition."""
import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace

from chc.api.CFunctionContract import CFunctionContract


class ContractCacheTest(unittest.TestCase):
    def test_multiple_conditions_and_repeated_reads(self):
        class Dictionary:
            calls = 0

            def parse_mathml_xpredicate(self, node, signature):
                assert signature == {"first": 1, "second": 2}
                self.calls += 1
                return self.calls

            def get_xpredicate(self, index):
                return index

        dictionary = Dictionary()
        file = SimpleNamespace(interfacedictionary=dictionary)
        contract = CFunctionContract(SimpleNamespace(cfile=file), ET.fromstring('''
          <function name="two_outputs">
            <parameters><par name="first" nr="1"/><par name="second" nr="2"/></parameters>
            <preconditions><pre/><pre/></preconditions>
            <postconditions><post/><post/></postconditions>
            <sideeffects><sideeffect/><sideeffect/></sideeffects>
          </function>'''))
        for attribute in ["preconditions", "postconditions", "sideeffects"]:
            first = getattr(contract, attribute)
            self.assertEqual(len(first), 2)
            self.assertIs(getattr(contract, attribute), first)
            self.assertEqual(contract.signature, {"first": 1, "second": 2})
        self.assertEqual(dictionary.calls, 6)


if __name__ == "__main__":
    unittest.main()
