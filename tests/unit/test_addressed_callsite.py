"""Caller field requirements must name the actual object without losing offsets."""
import unittest
from types import SimpleNamespace

from chc.app.CDictionary import CDictionary
from chc.app.CFileDictionary import CFileDictionary
from chc.app.CAttributes import CAttributes
from chc.util.IndexedTable import IndexedTableValue


class AddressedCallsiteTest(unittest.TestCase):
    def setUp(self):
        self.d = CFileDictionary.__new__(CFileDictionary)
        CDictionary.__init__(self.d)
        self.d._cfile = SimpleNamespace(index=1)
        self.d.index_attributes(CAttributes(self.d, IndexedTableValue(1, [], [])))
        self.no = self.d.mk_offset_index(["n"], [])

    def variable(self, name, vid, offset=None):
        host = self.d.mk_lhost_index(["var", name], [vid])
        lv = self.d.mk_lval_index([], [host, self.no if offset is None else offset])
        return self.d.get_lval(lv)

    def requirement(self):
        zero = self.d.mk_constant_index(["int", "0", "iint"], [])
        index = self.d.mk_exp_index(["const"], [zero])
        offset = self.d.mk_offset_index(["i"], [index, self.no])
        offset = self.d.mk_offset_index(["f", "bytes"], [1, offset])
        formal = self.variable("formal", 1)
        address = self.d.mk_lval_exp(formal.index)
        host = self.d.mk_lhost_index(["mem"], [address])
        return self.d.get_lval(self.d.mk_lval_index([], [host, offset]))

    def test_addressed_subobject_keeps_both_offsets_and_caller_id(self):
        member = self.d.mk_offset_index(["f", "member"], [1, self.no])
        actual = self.variable("caller", 2, member)
        address = self.d.get_exp(self.d.mk_exp_index(["addrof"], [actual.index]))
        other = self.d.get_exp(self.d.mk_lval_exp(self.variable("wrong", 3).index))
        result = self.d.get_lval(self.d.index_lval(self.requirement(), {1: address, 2: other}, 1))
        self.assertTrue(result.lhost.is_var)
        self.assertEqual(result.lhost.vid, 2)
        self.assertEqual(result.offset.fieldname, "member")
        self.assertEqual(result.offset.offset.fieldname, "bytes")
        self.assertTrue(result.offset.offset.offset.is_index)
        self.assertEqual(str(result.offset.offset.offset.index_exp), "0")

    def test_pointer_actual_keeps_indirection(self):
        actual = self.d.get_exp(self.d.mk_lval_exp(self.variable("pointer", 2).index))
        result = self.d.get_lval(self.d.index_lval(self.requirement(), {1: actual}, 1))
        self.assertTrue(result.lhost.is_mem)
        self.assertEqual(result.lhost.exp.lval.lhost.vid, 2)
        self.assertEqual(result.offset.fieldname, "bytes")

    def test_casted_address_keeps_indirection(self):
        actual = self.variable("caller", 2)
        address = self.d.mk_exp_index(["addrof"], [actual.index])
        typ = self.d.mk_typ_index(["tint", "iint"], [])
        ptr = self.d.mk_typ_index(["tptr"], [typ])
        cast = self.d.get_exp(self.d.mk_exp_index(["caste"], [ptr, address]))
        result = self.d.get_lval(self.d.index_lval(self.requirement(), {1: cast}, 1))
        self.assertTrue(result.lhost.is_mem)
        self.assertTrue(result.lhost.exp.is_caste)


if __name__ == "__main__":
    unittest.main()
