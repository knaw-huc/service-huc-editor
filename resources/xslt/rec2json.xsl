<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math"
    xmlns:js="http://www.w3.org/2005/xpath-functions"
    exclude-result-prefixes="xs math js"
    version="3.0">
    
    <xsl:output method="text" encoding="UTF-8"/>
    
    <xsl:template match="text()"/>
    
    <xsl:template match="/*:CMD">
        <xsl:variable name="rec">
            <js:array>
                <xsl:apply-templates/>
            </js:array>
        </xsl:variable>
        <!--<xsl:copy-of select="$rec"/>-->
        <xsl:value-of select="js:xml-to-json($rec)"/>
    </xsl:template>
    
    <xsl:template match="*">
        <xsl:choose>
            <xsl:when test="exists(*)">
                <js:map>
                    <js:string key="name" xsl:expand-text="yes">{local-name()}</js:string>
                    <js:string key="type">component</js:string>
                    <xsl:if test="exists(@*)">
                        <js:map key="attributes">
                            <xsl:apply-templates select="@*"/>
                        </js:map>
                    </xsl:if>
                    <js:array key="value">
                        <xsl:apply-templates/>
                        <js:array/>
                    </js:array>
                </js:map>
            </xsl:when>
            <xsl:otherwise>
                <js:map>
                    <js:string key="name" xsl:expand-text="yes">{local-name()}</js:string>
                    <js:string key="type">element</js:string>
                    <xsl:if test="exists(@*)">
                        <js:map key="attributes">
                            <xsl:apply-templates select="@*"/>
                        </js:map>
                    </xsl:if>
                    <js:string key="value" xsl:expand-text="yes">{string(.)}</js:string>
                </js:map>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="@*">
        <js:string key="{local-name()}" xsl:expand-text="yes">{string(.)}</js:string>
    </xsl:template>
    
    <xsl:template match="*:Resources">
        <js:map>
            <js:string key="name" xsl:expand-text="yes">{local-name()}</js:string>
            <js:string key="type">component</js:string>
            <js:array key="value">
                <js:array/>
            </js:array>
        </js:map>
        
    </xsl:template>
    
</xsl:stylesheet>