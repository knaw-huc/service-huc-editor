<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    exclude-result-prefixes="xs"
    version="3.0">
    
    <xsl:param name="JS"/>
    
    <xsl:template name="main">
        <xsl:choose>
            <xsl:when test="unparsed-text-available($JS)">
                <xsl:copy-of select="json-to-xml(unparsed-text($JS))"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:message terminate="yes">!ERR: JS[<xsl:value-of select="$JS"/>] can't be loaded</xsl:message>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    
    
</xsl:stylesheet>