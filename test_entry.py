import unittest
import utils
from entry import *

class TestEntry(unittest.TestCase):
    def test_to_string(self):
        """Right now, this is just a wrapper around xslt_transform(), so there's not a whole lot of reason to test it on its own."""
        self.assertTrue(True)

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
        xml3 = generate_etree("<entry><div></div></entry>")

        self.assertEqual(find_identity(xml1), "170v_1")
        self.assertEqual(find_identity(xml2), "")
        self.assertEqual(find_identity(xml3), "")

    def test_init(self):
        xml_string = ("<entry>"
            "\n\n\n\n"
            "<div id=\"150r_1\" categories=\"arms and armor;casting\" continued=\"yes\">"
            "<head>My title <del>with deleted text</del></head>"
            "<ab><fr>Je m'appelle <pn>Grègoire</pn>; voilà des accents comme ça!</fr></ab>"
            "<ab>I have a <al>dog</al> who loves <pa>figs</pa><del>, <ill/><cn><m>gold</m> coins</cn>,</del> and <mu>jazz</mu>, especially in the <tmp>afternoon</tmp>. She loves to say \"<la>carpe diem</la>\"!</ab>"
            "<comment rid=\"12345\"/>"
            "</div>"
            "<div id=\"150r_1\" continues=\"yes\">"
            "\n\n\n\n"
            "<head>You should ignore this title.</head>"
            "<ab>This is continued from the previous div with the same ID.</ab>"
            "<ab><md>Laughter</md> is the best medicine. A <ms>spoonful</ms> of <m><pa>sugar</pa></m> helps the medicine go down.</ab>"
            "<ab>Revenge is a dish best served <sn>cold</sn>. And make sure you provide a <tl>fork</tl> and <tl>knife</tl> to eat with!</ab>"
            "</div>"
            "\n\n\n\n"
            "<div id=\"150r_2\">"
            "\n\n\n\n"
            "<head>Yet another div.</head>"
            "<ab>Nothing to <sn>see</sn> here.</ab>"
            "<ab>This div shouldn't be here, since Entry should take only one ID at a time, but the presence of this div is just to make sure it can cope with this.</ab>"
            "</div>"
            "<div/>" # to_xml_string() reformats like this.
            "</entry>")

        xml = generate_etree(xml_string)

        text = ("\n\n\n\n"
            "My title <-with deleted text->"
            "Je m'appelle Grègoire; voilà des accents comme ça!"
            "I have a dog who loves figs<-, [illegible]gold coins,-> and jazz, especially in the afternoon. She loves to say \"carpe diem\"!"
            "\n\n\n\n"
            "You should ignore this title."
            "This is continued from the previous div with the same ID."
            "Laughter is the best medicine. A spoonful of sugar helps the medicine go down."
            "Revenge is a dish best served cold. And make sure you provide a fork and knife to eat with!"
            "\n\n\n\n"
            "\n\n\n\n"
            "Yet another div."
            "Nothing to see here."
            "This div shouldn't be here, since Entry should take only one ID at a time, but the presence of this div is just to make sure it can cope with this.")
        # I had so much fun writing that.

        e = Entry(xml)
        e_id = Entry(xml, identity='075r_1')
        e_folio = Entry(xml, folio='044v')

        self.assertEqual(e.identity, '150r_1')
        self.assertEqual(e.folio, '')

        self.assertEqual(e_id.identity, '075r_1')
        self.assertEqual(e_id.folio, '')

        self.assertEqual(e_folio.identity, '150r_1')
        self.assertEqual(e_folio.folio, '044v')

        for entry in (e, e_id, e_folio):
            self.assertEqual(entry.xml, xml) # pretty sure this is just equality of reference :/
            self.assertEqual(entry.text, text)
            self.assertEqual(entry.xml_string, xml_string)
            self.assertEqual(entry.title, "My title with deleted text")
            self.assertEqual(entry.categories, ["arms and armor", "casting"])
            self.assertEqual(entry.properties, 
                    OrderedDict([
                        ("animal",["dog"]),
                        ("body_part",[]),
                        ("currency",["gold coins"]),
                        ("definition",[]),
                        ("environment",[]),
                        ("material",["gold", "sugar"]),
                        ("medical",["Laughter"]),
                        ("measurement",["spoonful"]),
                        ("music",["jazz"]),
                        ("plant",["figs","sugar"]),
                        ("place",[]),
                        ("personal_name",["Grègoire"]),
                        ("profession",[]),
                        ("sensory",["cold","see"]),
                        ("tool",["fork","knife"]),
                        ("time",["afternoon"]),
                        ("weapon",[]),
                        ("german",[]),
                        ("greek",[]),
                        ("italian",[]),
                        ("latin",["carpe diem"]),
                        ("occitan",[]),
                        ("poitevin",[])
                    ]))

    def test_from_file(self):
        # change these to be Mock objects pls
        examples_dir = "./examples/entries/"
        files = ["tc_170r_6.xml", "tcn_170r_6.xml", "tl_170r_6.xml"]

        for filename in files:
            with open(examples_dir + filename.replace("xml","txt"), "r") as fp:
                text = fp.read()
            e = Entry.from_file(examples_dir + filename)
            self.assertEqual(e.text, text)
        # Not sure what actual test to put here...

    def test_from_string(self):
        xml_string = ("<entry>"
            "\n\n\n\n"
            "<div id=\"150r_1\" categories=\"arms and armor;casting\" continued=\"yes\">"
            "<head>My title <del>with deleted text</del></head>"
            "<ab><fr>Je m'appelle <pn>Grègoire</pn>; voilà des accents comme ça!</fr></ab>"
            "<ab>I have a <al>dog</al> who loves <pa>figs</pa><del>, <ill/><cn><m>gold</m> coins</cn>,</del> and <mu>jazz</mu>, especially in the <tmp>afternoon</tmp>. She loves to say \"<la>carpe diem</la>\"!</ab>"
            "<comment rid=\"12345\"/>"
            "</div>"
            "<div id=\"150r_1\" continues=\"yes\">"
            "\n\n\n\n"
            "<head>You should ignore this title.</head>"
            "<ab>This is continued from the previous div with the same ID.</ab>"
            "<ab><md>Laughter</md> is the best medicine. A <ms>spoonful</ms> of <m><pa>sugar</pa></m> helps the medicine go down.</ab>"
            "<ab>Revenge is a dish best served <sn>cold</sn>. And make sure you provide a <tl>fork</tl> and <tl>knife</tl> to eat with!</ab>"
            "</div>"
            "\n\n\n\n"
            "<div id=\"150r_2\">"
            "\n\n\n\n"
            "<head>Yet another div.</head>"
            "<ab>Nothing to <sn>see</sn> here.</ab>"
            "<ab>This div shouldn't be here, since Entry should take only one ID at a time, but the presence of this div is just to make sure it can cope with this.</ab>"
            "</div>"
            "<div/>" # to_xml_string() reformats like this.
            "</entry>")

        text = ("\n\n\n\n"
            "My title <-with deleted text->"
            "Je m'appelle Grègoire; voilà des accents comme ça!"
            "I have a dog who loves figs<-, [illegible]gold coins,-> and jazz, especially in the afternoon. She loves to say \"carpe diem\"!"
            "\n\n\n\n"
            "You should ignore this title."
            "This is continued from the previous div with the same ID."
            "Laughter is the best medicine. A spoonful of sugar helps the medicine go down."
            "Revenge is a dish best served cold. And make sure you provide a fork and knife to eat with!"
            "\n\n\n\n"
            "\n\n\n\n"
            "Yet another div."
            "Nothing to see here."
            "This div shouldn't be here, since Entry should take only one ID at a time, but the presence of this div is just to make sure it can cope with this.")

        e = Entry.from_string(xml_string)
        e_id = Entry.from_string(xml_string, identity='075r_1')
        e_folio = Entry.from_string(xml_string, folio='044v')

        self.assertEqual(e.identity, '150r_1')
        self.assertEqual(e.folio, '')

        self.assertEqual(e_id.identity, '075r_1')
        self.assertEqual(e_id.folio, '')

        self.assertEqual(e_folio.identity, '150r_1')
        self.assertEqual(e_folio.folio, '044v')

        for entry in (e, e_id, e_folio):
            self.assertEqual(entry.text, text)
            self.assertEqual(entry.xml_string, xml_string)
            self.assertEqual(entry.title, "My title with deleted text")
            self.assertEqual(entry.categories, ["arms and armor", "casting"])
            self.assertEqual(entry.properties, 
                    OrderedDict([
                        ("animal",["dog"]),
                        ("body_part",[]),
                        ("currency",["gold coins"]),
                        ("definition",[]),
                        ("environment",[]),
                        ("material",["gold", "sugar"]),
                        ("medical",["Laughter"]),
                        ("measurement",["spoonful"]),
                        ("music",["jazz"]),
                        ("plant",["figs","sugar"]),
                        ("place",[]),
                        ("personal_name",["Grègoire"]),
                        ("profession",[]),
                        ("sensory",["cold","see"]),
                        ("tool",["fork","knife"]),
                        ("time",["afternoon"]),
                        ("weapon",[]),
                        ("german",[]),
                        ("greek",[]),
                        ("italian",[]),
                        ("latin",["carpe diem"]),
                        ("occitan",[]),
                        ("poitevin",[])
                    ]))

if __name__ == '__main__':
    unittest.main()
