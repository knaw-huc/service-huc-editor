<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:math="http://www.w3.org/2005/xpath-functions/math" xmlns:clariah="http://www.clariah.eu/" exclude-result-prefixes="xs math" version="3.0">

    <xsl:param name="user" select="'server'"/>

    <xsl:template match="node() | @*">
        <xsl:copy>
            <xsl:apply-templates select="node() | @*"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="*:MdCreator">
        <xsl:copy>
            <xsl:value-of select="$user"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="*:MdCreationDate">
        <xsl:copy>
            <xsl:attribute name="clariah:epoch" select="floor((current-dateTime() - xs:dateTime('1970-01-01T00:00:00')) div xs:dayTimeDuration('PT1S'))"/>
            <xsl:value-of select="format-date(current-date(),'[Y0001]-[M01]-[D01]')"/>
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>
