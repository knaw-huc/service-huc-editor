<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:js="http://www.w3.org/2005/xpath-functions"
    exclude-result-prefixes="xs"
    version="3.0">
    
    <xsl:param name="js-uri" select="()"/>
    <xsl:param name="js-doc" select="
        if (js:unparsed-text-available($js-uri)) then
        (unparsed-text($js-uri))
        else
        ()"/>
    <xsl:param name="js-xml" select="json-to-xml($js-doc)"/>
    
    <xsl:template name="main">
        <xsl:apply-templates select="$js-xml"/>
    </xsl:template>
    
    <xsl:template match="node() | @*">
        <xsl:copy>
            <xsl:apply-templates select="node() | @*"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="js:*">
        <xsl:element name="js:{local-name()}">
            <xsl:apply-templates select="node() | @*"/>
        </xsl:element>
    </xsl:template>
    
</xsl:stylesheet>