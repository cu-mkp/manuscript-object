import unittest
import utils
import lxml.etree as et
from io import StringIO
from manuscript import *

class ManuscriptEntry(unittest.TestCase):
    def test_ignore_data_path(self):
        # This function is actually poorly implemented and needs to be rewritten and some other code refactored.
        # Reason: data path shouldn't be hard-coded.
        # At the moment this function is only used for printing, so it's not a critical issue.
        # However, it is Not Good and it should be changed.
        # As such, we are leaving this test unwritten until a proper spec is mocked up.
        # Idea: simply have a function "ignore common path" which takes two paths and essentially returns the latest path at which they diverge (which might be empty). This function should then be in utils.
        pass

    def test_extract_folio(self):
        self.assertEqual(extract_folio("tl_p162v_preTEI.xml"), "162v")
        self.assertEqual(extract_folio("/mnt/c/usr/foo/bar/tl_p162v_preTEI.xml"), "162v")
        self.assertEqual(extract_folio("foo_q162z_bar"), "162z")
        self.assertEqual(extract_folio("tc_p001r_preTEI.xml"), "001r")
        # Add `assertRaises` tests for bad inputs.

    def test_filename_from_folio(self):
        self.assertEqual(filename_from_folio("162v", "tl", "xml"), "tl_p162v_preTEI.xml")
        # Spec for this?
        self.assertEqual(filename_from_folio("", "", ""), "_p0000_preTEI.")
        self.assertEqual(filename_from_folio("1v", "foo", "barbuzz"), "foo_p001v_preTEI.barbuzz")
        pass

    def test_clean_folio(self):
        self.assertEqual(clean_folio("000000000001"), "1")
        self.assertEqual(clean_folio("100000000000"), "100000000000")
        self.assertEqual(clean_folio("005r"), "5r")
        self.assertEqual(clean_folio(""), "")
        self.assertEqual(clean_folio("foo"), "foo")
        self.assertEqual(clean_folio("162v"), "162v")
        pass

    def test_clean_id(self):
        # need better specs on what exactly this is supposed to do;
        # it's not clear in manuscript.py due to lack of documentation which step this is used for
        self.assertEqual(clean_id("p162v"), "162v")
        self.assertEqual(clean_id("p005r"), "5r")
        self.assertEqual(clean_id(""), "")
        self.assertEqual(clean_id("foop162vbar"), "foop162vbar")

    def test_separate_by_id(self):
        # Need a neat way to handle checking equality of lxml etree objects...
        input_1 = StringIO('<root><div id="p162v_1" categories="foo;bar" continued="yes">Content 1</div><div id="p162v_1" continues="yes">Content 2</div></root>')
        expected_result_1 = {'p162v_1' : et.XML('<entry><div id="p162v_1" categories="foo;bar" continued="yes">Content 1</div><div id="p162v_1" continues="yes">Content 2</div></entry>')}

        input_2 = StringIO('<root><div id="p162v_1" categories="foo;bar" continued="yes">Content 1</div><div id="p162v_2">Content 2</div><div id="p162v_1" continues="yes">Content 3</div></root>')
        expected_result_2 = {'p162v_1' : et.XML('<entry><div id="p162v_1" categories="foo;bar" continued="yes">Content 1</div><div id="p162v_1" continues="yes">Content 3</div></entry>'),
            'p162v_2' : et.XML('<entry><div id="p162v_2">Content 2</div></entry>')}
        self.assertEqual([et.tostring(x) for x in separate_by_id(input_1).values()], [et.tostring(x) for x in expected_result_1.values()])
        self.assertEqual([et.tostring(x) for x in separate_by_id(input_2).values()], [et.tostring(x) for x in expected_result_2.values()])
        pass

    def test_generate_entries(self):
        # effective testing requires the ability to accept mock files
        pass

    def test_generate_folios(self):
        # effective testing requires the ability to accept mock files
        pass

    def test_init(self):
        # effective testing requires the ability to accept mock files
        m = Manuscript()
        self.assertEqual(m.entries, {})
        self.assertEqual(m.folios, {})
        self.assertEqual(m.versions, [])

    def test_get_entry(self):
        m = Manuscript()
        # self.assertEqual(m.get_entry("162v"), Entry())
        pass

    def test_get_folio(self):
        pass

    def test_add_entry(self):
        pass

    def test_add_entries(self):
        pass

    def test_add_folio(self):
        pass

    def test_add_dir(self):
        pass

    def test_add_dirs(self):
        pass

    def test_from_dir(self):
        pass

    def test_from_dirs(self):
        pass

    def test_update(self):
        # effective testing requires the ability to accept mock files
        pass

    def test_update_ms_txt(self):
        # effective testing requires the ability to accept mock files
        pass

    def test_update_entries(self):
        # effective testing requires the ability to accept mock files
        pass

    def test_update_all_folios(self):
        # effective testing requires the ability to accept mock files
        pass

    def test_generate_all_folios(self):
        # effective testing requires the ability to accept mock files
        pass

    def test_update_metadata(self):
        # effective testing requires the ability to accept mock files
        pass

    def test_generate_metadata(self):
        # effective testing requires the ability to accept mock files
        pass

if __name__ == '__main__':
    unittest.main()
