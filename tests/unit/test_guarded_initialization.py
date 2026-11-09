"""Return guards must survive parsing, copying, display and MathML export."""
import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace
from chc.api.InterfaceDictionary import InterfaceDictionary
import chc.util.fileutil as UF


class GuardedInitializationTest(unittest.TestCase):
    def setUp(self):
        self.d = InterfaceDictionary(SimpleNamespace(), None)

    def predicate(self, op="ge", value="0"):
        node = ET.fromstring('<post><math><apply><initialized-on-return op="'
            + op + '" value="' + value + '"/><apply><addressed-value/>'
            '<ci>out</ci></apply></apply></math></post>')
        return self.d.get_xpredicate(self.d.parse_mathml_xpredicate(node, {"out": 1}))

    def test_guard_is_distinct_from_unconditional_initialization(self):
        pred = self.predicate()
        self.assertTrue(pred.is_initialized_on_return)
        self.assertFalse(pred.is_initialized)
        self.assertEqual(str(pred), 'initialized-on-return(ge,0,addressed-value(arg-val(par-1)))')

    def test_copy_keeps_comparison_constant_and_addressed_lval(self):
        pred = self.predicate("lt", "-7")
        copied = self.d.get_xpredicate(self.d.index_xpredicate(pred))
        self.assertEqual(copied.tags, ["ior", "lt", "-7"])
        self.assertEqual(str(copied.term), str(pred.term))

    def test_mathml_round_trip_keeps_guard_on_operator(self):
        pred = self.predicate("eq", "19")
        node = ET.Element("post")
        pred.write_mathml(ET.SubElement(node, "math"), ["", "out"])
        copied = self.d.get_xpredicate(self.d.parse_mathml_xpredicate(node, {"out": 1}))
        self.assertEqual(str(copied), str(pred))

    def test_invalid_comparison_is_rejected(self):
        with self.assertRaises(UF.CHCError):
            self.predicate("plus")


if __name__ == '__main__':
    unittest.main()
