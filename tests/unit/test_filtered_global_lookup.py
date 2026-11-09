"""Filtered header declarations remain readable without importing their bodies."""
import unittest
from types import SimpleNamespace
from chc.app.CFile import CFile
from chc.api.PostRequest import PostRequest
from chc.util.IndexedTable import IndexedTableValue
import chc.util.fileutil as UF


class FilteredGlobalLookupTest(unittest.TestCase):
    def setUp(self):
        self.declared = SimpleNamespace(vid=200, vglob=True, vname='header_getter')
        self.local = SimpleNamespace(vid=300, vglob=False, vname='local')
        self.existing = SimpleNamespace(vid=100, vglob=True, vname='visible')
        entries = [IndexedTableValue(7, [], [200]), IndexedTableValue(200, [], [300])]
        self.file = CFile.__new__(CFile)
        self.file._cfileglobals = SimpleNamespace(global_varinfo_vids={100:self.existing})
        self.file._dictionary = SimpleNamespace()
        self.file._declarations = SimpleNamespace(
            varinfo_table=SimpleNamespace(values=lambda:entries),
            get_varinfo=lambda index:{7:self.declared,200:self.local}[index])

    def test_filtered_global_uses_vid_and_keeps_function_filter(self):
        self.assertTrue(self.file.has_global_varinfo(200))
        self.assertIs(self.file.get_global_varinfo(200),self.declared)
        self.assertEqual(set(self.file.cfileglobals.global_varinfo_vids),{100})

    def test_visible_global_keeps_existing_lookup(self):
        self.assertIs(self.file.get_global_varinfo(100),self.existing)

    def test_local_and_missing_vid_are_rejected(self):
        for vid in [7,300,999]:
            self.assertFalse(self.file.has_global_varinfo(vid))
            with self.assertRaises(UF.CHCError):self.file.get_global_varinfo(vid)

    def test_postcondition_request_resolves_filtered_callee(self):
        req=PostRequest(SimpleNamespace(cfile=self.file),IndexedTableValue(1,[],[200,1]))
        self.assertIs(req.callee,self.declared)


if __name__=='__main__':unittest.main()
