<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:math="http://www.w3.org/2005/xpath-functions/math" xmlns:js="http://www.w3.org/2005/xpath-functions" xmlns:clariah="http://www.clariah.eu/" xmlns:cue="http://www.clarin.eu/cmd/cues/1" exclude-result-prefixes="xs math js clariah cue" version="3.0">

    <xsl:output method="text" encoding="UTF-8"/>

    <xsl:template match="text()"/>

    <xsl:template match="/ComponentSpec">
        <xsl:variable name="prof">
            <xsl:choose>
                <xsl:when test="@isProfile = 'true'">
                    <xsl:apply-templates select="Component">
                        <xsl:with-param name="level" select="1" tunnel="yes"/>
                    </xsl:apply-templates>
                </xsl:when>
                <xsl:otherwise>
                    <js:array/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <!--<xsl:copy-of select="$prof"/>-->
        <xsl:value-of select="js:xml-to-json($prof)"/>
    </xsl:template>

    <xsl:template match="Component">
        <xsl:param name="level" tunnel="yes"/>
        <js:map>
            <js:string key="type">Component</js:string>
            <js:number key="level" xsl:expand-text="yes">{$level}</js:number>
            <js:string key="ID" xsl:expand-text="yes">{generate-id()}</js:string>
            <js:map key="attributes">
                <xsl:apply-templates select="@* | clariah:*"/>
                <js:string key="initialOrder" xsl:expand-text="yes">{position()}</js:string>
            </js:map>
            <js:array key="content">
                <xsl:apply-templates select="Component | Element">
                    <xsl:sort select="@cue:displayOrder" data-type="number"/>
                    <xsl:with-param name="level" select="$level + 1" tunnel="yes"/>
                </xsl:apply-templates>
            </js:array>
        </js:map>
    </xsl:template>

    <xsl:template match="Element">
        <xsl:param name="level" tunnel="yes"/>
        <js:map>
            <js:string key="type">Element</js:string>
            <js:number key="level" xsl:expand-text="yes">{$level}</js:number>
            <js:string key="ID" xsl:expand-text="yes">{generate-id()}</js:string>
            <js:map key="attributes">
                <xsl:apply-templates select="@* | clariah:*"/>
                <js:string key="initialOrder" xsl:expand-text="yes">{position()}</js:string>
            </js:map>         
        </js:map>
    </xsl:template>
    
    <xsl:template match="@*">
        <js:string key="{local-name()}" xsl:expand-text="yes">{string(.)}</js:string>
    </xsl:template>
    
    <xsl:template match="clariah:*">
        <js:string key="{local-name()}" xsl:expand-text="yes">{string(.)}</js:string>
    </xsl:template>
    
</xsl:stylesheet>
