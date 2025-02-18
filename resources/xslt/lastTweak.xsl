<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xs="http://www.w3.org/2001/XMLSchema"
                xmlns:math="http://www.w3.org/2005/xpath-functions/math"
                exclude-result-prefixes="xs math"
                xmlns:clariah="http://www.clariah.eu/"
                xmlns:cue="http://www.clarin.eu/cmd/cues/1"
                version="3.0">

    <xsl:template match="node() | @*">
        <xsl:copy>
            <xsl:apply-templates select="node() | @*"/>
        </xsl:copy>
    </xsl:template>


    <xsl:template match="clariah:explanation[normalize-space(@src) != '']">
        <xsl:choose>
            <xsl:when test="@src= 'documentation' and normalize-space(../Documentation) != ''">
                <clariah:explanation>
                    <xsl:value-of select="../Documentation"/>
                </clariah:explanation>
            </xsl:when>
        </xsl:choose>
    </xsl:template>

    <!-- add clariah:value wrapper to items from the profile -->
    <xsl:template match="item">
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <clariah:value>
                <xsl:value-of select="."/>
            </clariah:value>
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>