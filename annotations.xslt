<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="2.0">
    <xsl:output method="text" encoding="UTF-8"/>

    <xsl:param name="corr" select="'annotate'"/>
    <xsl:param name="del"  select="'annotate'"/>
    <xsl:param name="exp"  select="'annotate'"/>
    <xsl:param name="ill"  select="'annotate'"/>
    <xsl:param name="sup"  select="'annotate'"/>
    
    <xsl:template match="/">
        <xsl:apply-templates/>
    </xsl:template>

    <xsl:template match="corr">
        <xsl:choose>
            <xsl:when test="$corr = 'annotate'">
                <xsl:text>[</xsl:text>
                <xsl:apply-templates/>
                <xsl:text>]</xsl:text>
            </xsl:when>
            <xsl:when test="$corr = 'plaintext'">
                <xsl:apply-templates/>
            </xsl:when>
            <xsl:when test="$corr = 'omit'"/>
            <xsl:otherwise>
                <xsl:message terminate="yes">
                    ERROR: Bad input for param 'corr'!
                    Value must be one of:
                      - 'annotate'
                      - 'plaintext'
                      - 'omit'
                    Instead got '<xsl:value-of select="$corr"/>'.
                </xsl:message>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="del">
        <xsl:choose>
            <xsl:when test="$del = 'annotate'">
                <xsl:text>&lt;-</xsl:text>
                <xsl:apply-templates/>
                <xsl:text>-&gt;</xsl:text>
            </xsl:when>
            <xsl:when test="$del = 'plaintext'">
                <xsl:apply-templates/>
            </xsl:when>
            <xsl:when test="$del = 'omit'"/>
            <xsl:otherwise>
                <xsl:message terminate="yes">
                    ERROR: Bad input for param 'del'!
                    Value must be one of:
                      - 'annotate'
                      - 'plaintext'
                      - 'omit'
                    Instead got '<xsl:value-of select="$del"/>'.
                </xsl:message>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="exp">
        <xsl:choose>
            <xsl:when test="$exp = 'annotate'">
                <xsl:text>{</xsl:text>
                <xsl:apply-templates/>
                <xsl:text>}</xsl:text>
            </xsl:when>
            <xsl:when test="$exp = 'plaintext'">
                <xsl:apply-templates/>
            </xsl:when>
            <xsl:when test="$exp = 'omit'"/>
            <xsl:otherwise>
                <xsl:message terminate="yes">
                    ERROR: Bad input for param 'exp'!
                    Value must be one of:
                      - 'annotate'
                      - 'plaintext'
                      - 'omit'
                    Instead got '<xsl:value-of select="$exp"/>'.
                </xsl:message>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="ill">
        <xsl:choose>
            <xsl:when test="$ill = 'annotate'">
                <xsl:text>[illegible]</xsl:text>
                <xsl:apply-templates/>
            </xsl:when>
            <xsl:when test="$ill = 'omit'"/>
            <xsl:otherwise>
                <xsl:message terminate="yes">
                    ERROR: Bad input for param 'ill'!
                    Value must be one of:
                      - 'annotate'
                      - 'omit'
                    Instead got '<xsl:value-of select="$ill"/>'.
                </xsl:message>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="sup">
        <xsl:choose>
            <xsl:when test="$sup = 'annotate'">
                <xsl:text>[</xsl:text>
                <xsl:apply-templates/>
                <xsl:text>]</xsl:text>
            </xsl:when>
            <xsl:when test="$sup = 'plaintext'">
                <xsl:apply-templates/>
            </xsl:when>
            <xsl:when test="$sup = 'omit'"/>
            <xsl:otherwise>
                <xsl:message terminate="yes">
                    ERROR: Bad input for param 'sup'!
                    Value must be one of:
                      - 'annotate'
                      - 'plaintext'
                      - 'omit'
                    Instead got '<xsl:value-of select="$sup"/>'.
                </xsl:message>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>
