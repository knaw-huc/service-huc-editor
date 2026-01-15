<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math"
    xmlns:fn="http://www.w3.org/2005/xpath-functions"
    exclude-result-prefixes="xs math"
    expand-text="yes"
    version="3.0">
    
    <xsl:template match="/">
        <html>
            <head>
                <title>history for record [{/fn:map/fn:*[@key='nr']}] </title>
            </head>
            <body>
                <div class="summary">
                    <h2>Aantal versies</h2>
                    <p>
                        <strong>Total versions: </strong>
                        {count(/fn:map/fn:array[@key='history']/fn:map)}
                    </p>
                </div>                
                <ol>
                    <xsl:apply-templates select="fn:map/fn:array/fn:map"/>
                </ol>
            </body>
        </html>
    </xsl:template>
    
    
    <xsl:template match="fn:map">
        <xsl:variable name="tijd" select="fn:string[@key='timestamp']"/>
        <xsl:variable name="epoch" select="fn:number[@key='epoch']"/>   
        <li> <a href="{$epoch}">{$tijd}</a>  </li>
    </xsl:template>    
    
    
</xsl:stylesheet>