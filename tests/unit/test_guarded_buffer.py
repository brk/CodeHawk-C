"""A guarded bounded region must remain distinct from unconditional memory facts."""
import unittest
import xml.etree.ElementTree as ET
from types import SimpleNamespace
from chc.api.InterfaceDictionary import InterfaceDictionary
import chc.util.fileutil as UF

class GuardedBufferTest(unittest.TestCase):
    def setUp(self):
        self.d = InterfaceDictionary(SimpleNamespace(), None)

    def predicate(self, op='ge', value='0', capacity='<ci>size</ci>'):
        node = ET.fromstring('<post><math><apply><buffer-on-return op="'
            + op + '" value="' + value + '"/><apply><addressed-value/>'
            '<ci>out</ci></apply>' + capacity + '</apply></math></post>')
        return self.d.get_xpredicate(self.d.parse_mathml_xpredicate(node, {'out':1,'size':2}))

    def test_distinct_guarded_predicate(self):
        pred=self.predicate()
        self.assertTrue(pred.is_buffer_on_return)
        self.assertFalse(pred.is_initialized)
        self.assertFalse(pred.is_initialized_on_return)
        self.assertFalse(pred.is_buffer)
        self.assertEqual(pred.tags,['bor','ge','0'])
        self.assertEqual(str(pred.capacity),'arg-val(par-2)')

    def test_copy_preserves_guard_lval_and_capacity(self):
        pred=self.predicate('lt','-7','<cn>4928</cn>')
        copied=self.d.get_xpredicate(self.d.index_xpredicate(pred))
        self.assertEqual(str(copied),str(pred))
        self.assertEqual(copied.tags,['bor','lt','-7'])

    def test_mathml_roundtrip(self):
        pred=self.predicate('eq','19')
        node=ET.Element('post')
        pred.write_mathml(ET.SubElement(node,'math'),['','out','size'])
        copied=self.d.get_xpredicate(self.d.parse_mathml_xpredicate(node,{'out':1,'size':2}))
        self.assertEqual(str(copied),str(pred))

    def test_reject_invalid_guard(self):
        with self.assertRaises(UF.CHCError):self.predicate('plus')

    def test_reject_missing_capacity(self):
        with self.assertRaises(UF.CHCError):self.predicate(capacity='')

if __name__=='__main__':unittest.main()
