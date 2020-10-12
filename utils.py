#m_k_data_to_thesaurus = f'{m_path}/manuscript-object/thesaurus'

versions = ['tc', 'tcn', 'tl']

prop_dict = {
    'animal': 'al',
    'body_part': 'bp',
    'currency': 'cn',
    'definition': 'def',
    'environment': 'env',
    'material': 'm',
    'medical': 'md',
    'measurement': 'ms',
    'music': 'mu',
    'plant': 'pa',
    'place': 'pl',
    'personal_name': 'pn',
    'profession': 'pro',
    'sensory': 'sn',
    'tool': 'tl',
    'time': 'tmp',
    'weapon': 'wp',
    'german': 'de',
    'greek': 'ge',
    'italian': 'it',
    'latin': 'la',
    'occitan': 'oc',
    'poitevin': 'po'
}

categories = [
    "lists",
    "medicine",
    "stones",
    "varnish",
    "arms and armor",
    "casting",
    "metal process",
    "practical optics",
    "decorative",
    "painting",
    "glass process",
    "household and daily life",
    "tool",
    "wood and its coloring",
    "cultivation",
    "merchants",
    "dyeing",
    "preserving",
    "tricks and sleight of hand",
    "corrosives",
    "animal husbandry",
    "wax process",
    "printing",
    "alchemy",
    "La boutique",
    "manuscript structure" 
]

stylesheet = """ 
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="1.0">
    <xsl:output method="text" encoding="UTF-8"/>
    
    <xsl:template match="/">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="corr">
        <xsl:text>[</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>]</xsl:text>
    </xsl:template>

    <xsl:template match="del">
        <xsl:text>&lt;-</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>-&gt;</xsl:text>
    </xsl:template>

    <xsl:template match="exp">
        <xsl:text>{</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>}</xsl:text>
    </xsl:template>

    <xsl:template match="ill">
        <xsl:text>[illegible]</xsl:text>
        <xsl:apply-templates/>
    </xsl:template>
    
    <xsl:template match="sup">
        <xsl:text>[</xsl:text>
        <xsl:apply-templates/>
        <xsl:text>]</xsl:text>
    </xsl:template>
</xsl:stylesheet>
"""
