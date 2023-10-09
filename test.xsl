<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math"
    exclude-result-prefixes="xs math"
    version="2.0">

    <xsl:template match="/" mode="#default">
        <hello>
            <xsl:value-of select="ComponentSpec/Header/ID"/>
        </hello>        
    </xsl:template>
</xsl:stylesheet>