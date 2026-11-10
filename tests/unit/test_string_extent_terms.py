"""String scan/extent terms must import the MathML their own writers emit."""
import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace
from chc.api.InterfaceDictionary import InterfaceDictionary
import chc.util.fileutil as UF

class StringExtentTermsTest(unittest.TestCase):
    def setUp(self): self.d=InterfaceDictionary(SimpleNamespace(),None)
    def test_unary_term_roundtrips(self):
        for op in ['index-size','byte-size','nullterminator-pos']:
            with self.subTest(op=op):
                node=ET.fromstring('<apply><'+op+'/><ci>src</ci></apply>')
                term=self.d.get_s_term(self.d.parse_mathml_term(node,{'src':1}))
                copied=self.d.get_s_term(self.d.index_s_term(term))
                self.assertEqual(str(copied),str(term))
                saved=term.get_mathml_node(['','src'])
                reparsed=self.d.get_s_term(self.d.parse_mathml_term(saved,{'src':1}))
                self.assertEqual(str(reparsed),str(term))
    def test_nested_initialized_string_extent(self):
        node=ET.fromstring('<pre><math><apply><initialized-range/><ci>src</ci>'
             '<apply><index-size/><apply><nullterminator-pos/><ci>src</ci></apply>'
             '</apply></apply></math></pre>')
        pred=self.d.get_xpredicate(self.d.parse_mathml_xpredicate(node,{'src':1}))
        self.assertTrue(pred.is_initialized_range)
        self.assertTrue(pred.length.is_index_size)
        self.assertTrue(pred.length.term.is_arg_null_terminator_pos)
        copied=self.d.get_xpredicate(self.d.index_xpredicate(pred))
        self.assertEqual(str(copied),str(pred))
    def test_reject_wrong_arity(self):
        for op in ['index-size','byte-size','nullterminator-pos']:
            for operands in ['', '<ci>src</ci><cn>4</cn>']:
                with self.subTest(op=op,operands=operands),self.assertRaises(UF.CHCError):
                    self.d.parse_mathml_term(ET.fromstring('<apply><'+op+'/>'+operands+'</apply>'),{'src':1})

if __name__=='__main__':unittest.main()
