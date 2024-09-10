<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math"
    xmlns:js="http://www.w3.org/2005/xpath-functions"
    exclude-result-prefixes="xs math"
    version="3.0">
    
    <xsl:param name="js-uri" select="'file:/Users/menzowi/Documents/Projects/huc-cmdi-editor/service/tests/Untitled2.json'"/>
    <xsl:param name="js-doc" select="if (js:unparsed-text-available($js-uri)) then (unparsed-text($js-uri)) else ()"/>
    <xsl:param name="js-xml" select="js:json-to-xml($js-doc)"/>
    
    <xsl:param name="prof" select="'clarin.eu:cr1:p_1721373443933'"/>
    <xsl:param name="user" select="'test'"/>
    <xsl:param name="self" select="'unl://1'"/>
    
    <xsl:variable name="cmd-ns" select="'http://www.clarin.eu/cmd/'"/>
    <xsl:variable name="cmdp-ns" select="'http://www.clarin.eu/cmd/'"/>
    
    <xsl:template name="main">
        <cmd:CMD xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:cmd="http://www.clarin.eu/cmd/" xsi:schemaLocation="http://www.clarin.eu/cmd/ http://catalog.clarin.eu/ds/ComponentRegistry/rest/registry/profiles/{$prof}/xsd" CMDVersion="1.1">
            <cmd:Header>
                <cmd:MdCreator xsl:expand-text="yes">{$user}</cmd:MdCreator>
                <cmd:MdCreationDate xsl:expand-text="yes">{format-date(current-date(),'[Y0001]-[M01]-[D01]')}</cmd:MdCreationDate>
                <cmd:MdSelfLink xsl:expand-text="yes">{$self}</cmd:MdSelfLink>
                <cmd:MdProfile xsl:expand-text="yes">{$prof}</cmd:MdProfile>
            </cmd:Header>
            <cmd:Resources>
                <cmd:ResourceProxyList/>
                <cmd:JournalFileProxyList/>
                <cmd:ResourceRelationList/>
                <cmd:IsPartOfList/>
            </cmd:Resources>
            <cmd:Components>
                <xsl:apply-templates select="$js-xml/js:array/js:map">
                    <xsl:sort select="*[@key='sortOrder']" data-type="number"></xsl:sort>
                </xsl:apply-templates>
            </cmd:Components>
        </cmd:CMD>
    </xsl:template>
    
    <xsl:template match="js:map[js:string[@key='type']='component']">
        <xsl:element name="cmd:{js:string[@key='name']}" namespace="{$cmd-ns}">
            <xsl:apply-templates select="js:array[@key='content']/js:map">
                <xsl:sort select="*[@key='sortOrder']" data-type="number"></xsl:sort>
            </xsl:apply-templates>
        </xsl:element>
    </xsl:template>
    
    <xsl:template match="js:map[js:string[@key='type']='element']">
        <xsl:element name="cmd:{js:string[@key='name']}" namespace="{$cmd-ns}">
            <xsl:value-of select="js:array[@key='content']/js:map/js:string[@key='value']"/>
        </xsl:element>
    </xsl:template>
    
</xsl:stylesheet>