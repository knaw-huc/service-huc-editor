<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math"
    xmlns:clariah="http://www.clariah.eu/"
    xmlns:cue="http://www.clarin.eu/cmd/cues/1"
    exclude-result-prefixes="xs math"
    version="3.0">
    
    <xsl:param name="cues" select="()"/>
    
    <xsl:template match="node() | @*">
        <xsl:copy>
            <xsl:apply-templates select="node() | @*"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="ComponentSpec">
        <xsl:copy>
            <xsl:namespace name="cue" select="'http://www.clarin.eu/cmd/cues/1'"/>
            <xsl:namespace name="clariah" select="'http://www.clariah.eu/'"/>
            <xsl:apply-templates select="node() | @*"/>
        </xsl:copy>
    </xsl:template>
    
    <xsl:template match="Component|Element">
        <xsl:message>?DBG:<xsl:value-of select="local-name()"/>[<xsl:value-of select="@name"/>]</xsl:message>
        <xsl:copy copy-namespaces="no">
            <xsl:apply-templates select="@name"/>
            <xsl:variable name="a" select="ancestor-or-self::Component[2]/@name"/>
            <xsl:variable name="c" select="ancestor-or-self::Component[1]/@name"/>
            <xsl:variable name="e" select="self::Element/@name"/>
            <xsl:variable name="r" as="node()?">
                <xsl:choose>
                    <xsl:when test="normalize-space($c)=''">
                        <xsl:message>DBG: no c</xsl:message>
                        <xsl:sequence select="()"/>
                    </xsl:when>
                    <xsl:when test="normalize-space($e)!=''">
                        <xsl:message>DBG: match c[<xsl:value-of select="$c"/>] and e[<xsl:value-of select="$e"/>]</xsl:message>
                        <xsl:sequence select="$cues//r[normalize-space(c[@n='SKIP'])=''][normalize-space(c[@n='component'])=$c][normalize-space(c[@n='element'])=$e][normalize-space(c[@n='ancestor'])=$a or normalize-space(c[@n='ancestor'])='']"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:message>DBG: match only c[<xsl:value-of select="$c"/>]</xsl:message>
                        <xsl:sequence select="$cues//r[normalize-space(c[@n='SKIP'])=''][normalize-space(c[@n='component'])=$c][normalize-space(c[@n='element'])=''][normalize-space(c[@n='ancestor'])=$a or normalize-space(c[@n='ancestor'])='']"/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:variable>
            <xsl:message>DBG: r[<xsl:value-of select="$r"/>]</xsl:message>
            <xsl:message>DBG: c[<xsl:value-of select="$c"/>] e[<xsl:value-of select="$e"/>] r[<xsl:value-of select="$r/@l"/>]</xsl:message>
            <xsl:if test="normalize-space($r/c[@n='order'])!=''">
                <xsl:attribute name="cue:displayOrder" select="$r/c[@n='order']"/>
            </xsl:if>
            <xsl:if test="normalize-space($r/c[@n='textWidth (characters)'])!=''">
                <xsl:attribute name="cue:inputWidth" select="$r/c[@n='textWidth (characters)']"/>
            </xsl:if>
            <xsl:if test="normalize-space($r/c[@n='textHeight (lines)'])!=''">
                <xsl:attribute name="cue:inputHeight" select="$r/c[@n='textHeight (lines)']"/>
            </xsl:if>
            <xsl:if test="normalize-space($r/c[@n='label'])!=''">
                <clariah:label xml:lang="en">
                    <xsl:value-of select="$r/c[@n='label']"/>
                </clariah:label>
            </xsl:if>
            <xsl:if test="normalize-space($r/c[@n='explanation'])!=''">
                <clariah:explanation>
                    <xsl:value-of select="$r/c[@n='explanation']"/>
                </clariah:explanation>
            </xsl:if>
            <xsl:if test="normalize-space($r/c[@n='vocabulary (https://skosmos.sd.di.huc.knaw.nl/en/)'])!=''">
                <clariah:autoCompleteURI>skos_proxy.php?vocabulary=<xsl:value-of select="replace($r/c[@n='vocabulary (https://skosmos.sd.di.huc.knaw.nl/en/)'],'https://skosmos.sd.di.huc.knaw.nl/(.*)/en/','$1')"/></clariah:autoCompleteURI>
            </xsl:if>
            
            <xsl:choose>
                <xsl:when test="empty(*)">
                    <xsl:comment>cues</xsl:comment>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:apply-templates select="node() except ValueScheme"/>        
                </xsl:otherwise>
            </xsl:choose>
        </xsl:copy>
    </xsl:template>
    
</xsl:stylesheet>