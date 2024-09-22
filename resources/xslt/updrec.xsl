<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:math="http://www.w3.org/2005/xpath-functions/math" xmlns:clariah="http://www.clariah.eu/" xmlns:cmd="http://www.clarin.eu/cmd/" exclude-result-prefixes="xs math" version="3.0">

    <xsl:param name="user" select="'updrec.xsl'"/>

    <xsl:template match="node() | @*">
        <xsl:copy>
            <xsl:apply-templates select="node() | @*"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="cmd:MdCreator">
        <xsl:copy>
            <xsl:value-of select="$user"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="cmd:MdCreationDate">
        <cmd:MdCreationDate clariah:epoch="{floor((current-dateTime() - xs:dateTime('1970-01-01T00:00:00')) div xs:dayTimeDuration('PT1S'))}" xsl:expand-text="yes">{format-date(current-date(),'[Y0001]-[M01]-[D01]')}</cmd:MdCreationDate>
    </xsl:template>

</xsl:stylesheet>
