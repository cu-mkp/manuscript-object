import unittest
import utils
from entry import *

class TestEntry(unittest.TestCase):
    def test_xslt_transform(self):
        xml = generate_etree(("<entry>"
                              "<div>"
                              "<ab>"
                              "<add>foo bar</add>"
                              "<corr>foo bar</corr>"
                              "<del>foo bar</del>"
                              "<emph>foo bar</emph>"
                              "<exp>foo bar</exp>"
                              "<gap/>"
                              "<ill/>"
                              "<superscript>foo bar</superscript>"
                              "<sup>foo bar</sup>"
                              "<underline>foo bar</underline>"
                              "</ab>"
                              "</div>"
                              "</entry>"))

        expected_result1 = ("foo bar"
                           "[foo bar]"
                           "<-foo bar->"
                           "foo bar"
                           "{foo bar}"
                           ""
                           "[illegible]"
                           "foo bar"
                           "[foo bar]"
                           "foo bar")

        expected_result2 = ("foo bar"
                           "foo bar"
                           "foo bar"
                           "foo bar"
                           "foo bar"
                           ""
                           ""
                           "foo bar"
                           "foo bar"
                           "foo bar")

        self.assertEqual(xslt_transform(xml, transform), expected_result1)
        self.assertEqual(xslt_transform(xml, transform, params={
            "corr":False,
            "del":False,
            "exp":False,
            "ill":False,
            "sup":False}), expected_result2)

    def test_parse_categories(self):
        xml = generate_etree(("<entry>"
            "<div id='015v_1' categories='arms and armor;casting;painting'>"
            "<ab>Some content in a div.</ab>"
            "</div>"
            "<div id='015v_2' categories='varnish;cultivation'>"
            "<ab>Second div content. This div's categories should be ignored.</ab>"
            "</div>"
            "</entry>"))
        expected_result = ["arms and armor", "casting", "painting"]

        self.assertEqual(parse_categories(xml), expected_result)

    def test_find_terms(self):
        xml = generate_etree("<entry>" +
            "<div><ab>" +
            " ".join([f'<{tag}>foo</{tag}>' for tag in utils.prop_dict.values()]) +
            "</ab></div>" +
            "<div><ab>" +
            " ".join([f'<{tag}>bar</{tag}>' for tag in utils.prop_dict.values()]) +
            "</ab></div>" +
            "</entry>")
        for tag in utils.prop_dict.values():
            self.assertEqual(find_terms(xml, tag), ["foo", "bar"])

    def test_parse_properties(self):
        xml = generate_etree("<entry>" +
            "<div><ab>" +
            " ".join([f'<{tag}>foo</{tag}>' for tag in utils.prop_dict.values()]) +
            "</ab></div>" +
            "<div><ab>" +
            " ".join([f'<{tag}>bar</{tag}>' for tag in utils.prop_dict.values()]) +
            "</ab></div>" +
            "</entry>")
        self.assertEqual(parse_properties(xml), {tag:["foo","bar"] for tag in utils.prop_dict.keys()})

    def test_find_title(self):
        xml1 = generate_etree(("<entry>"
            "<div>"
            "<head>Title 1 <del>deleted text</del></head>"
            "</div>"
            "<div>"
            "<head>Title 2 <del>deleted text</del></head>"
            "</div>"
            "</entry>"))
        xml2 = generate_etree(("<entry>"
            "<div>"
            "<ab>Body 1</ab>"
            "</div>"
            "<div>"
            "<ab>Title 2</ab>"
            "</div>"
            "</entry>"))
        self.assertEqual(find_title(xml1), "Title 1 deleted text")
        self.assertEqual(find_title(xml2), "")

    def test_find_identity(self):
        xml1 = generate_etree(("<entry>"
            "<comment/>"
            "<div id='170v_1' categories='casting'>"
            "<ab>Some content</ab>"
            "</div>"
            "<div id='170v_2'>"
            "<ab>Content 2</ab>"
            "</div>"
            "</entry>"))
        xml2 = generate_etree(("<entry>"
            "<comment/>"
            "<div categories='casting'>"
            "<ab>Some content</ab>"
            "</div>"
            "<div>"
            "<ab>Content 2</ab>"
            "</div>"
            "</entry>"))
        xml3 = generate_etree("<entry></entry>")

        self.assertEqual(find_identity(xml1), "170v_1")
        self.assertEqual(find_identity(xml2), "")
        self.assertEqual(find_identity(xml3), "")

if __name__ == '__main__':
    unittest.main()
