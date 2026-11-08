"""Match the engine's nullary null-termination preservation predicate."""
import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace

from chc.api.InterfaceDictionary import InterfaceDictionary


class NullTerminationEffectTest(unittest.TestCase):
    def test_engine_predicate_renders_without_a_term(self):
        d = InterfaceDictionary(SimpleNamespace(), None)
        pred = d.get_xpredicate(d.mk_xpredicate(["prn"], []))
        self.assertEqual(str(pred), "preserves-null-termination")
        self.assertTrue(pred.is_preserves_null_termination)
        self.assertEqual(pred.args, [])

    def test_xml_and_dictionary_copy_stay_nullary(self):
        d = InterfaceDictionary(SimpleNamespace(), None)
        node = ET.fromstring("<sideeffect><math><apply><preserves-null-termination/></apply></math></sideeffect>")
        pred = d.get_xpredicate(d.parse_mathml_xpredicate(node, {}))
        other = InterfaceDictionary(SimpleNamespace(), None)
        copied = other.get_xpredicate(other.index_xpredicate(pred))
        self.assertEqual(str(copied), "preserves-null-termination")
        self.assertEqual(copied.args, [])


if __name__ == "__main__":
    unittest.main()
