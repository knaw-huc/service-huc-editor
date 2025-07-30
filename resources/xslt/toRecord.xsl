<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math"
    xmlns:clariah="http://www.clariah.eu/"
    xmlns:cue="http://www.clarin.eu/cmd/cues/1"
    xmlns:cmd="http://www.clarin.eu/cmd/1"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    exclude-result-prefixes="xs math"
    version="3.0">
    
    <xsl:variable name="prof" select="/ComponentSpec/Header/ID"/>
    
    <xsl:param name="cmd-uri" select="'http://www.clarin.eu/cmd/1'"/>
    <xsl:param name="cr-uri" select="'https://catalog.clarin.eu/ds/ComponentRegistry/rest/registry'"/>
    <xsl:variable name="cmd-profiles" select="concat($cmd-uri,'/profiles')"/>
    <xsl:variable name="cmd-profile-uri" select="concat($cmd-profiles,$prof)"/>
    
    <xsl:template match="text()"/>
    
    <xsl:template match="ComponentSpec">
        <cmd:CMD
            xsi:schemaLocation="
            {$cmd-uri} https://infra.clarin.eu/CMDI/1.x/xsd/cmd-envelop.xsd
            {$cmd-profile-uri} {$cr-uri}/1.2/profiles/{$prof}/xsd" CMDVersion="1.2">
            <cmd:Header>
                <cmd:MdCreator>test</cmd:MdCreator>
                <cmd:MdCreationDate>
                    <xsl:value-of select="format-date(current-date(),'[Y0001]-[M01]-[D01]')"/>
                </cmd:MdCreationDate>
                <cmd:MdSelfLink>http://example.com/test</cmd:MdSelfLink>
                <cmd:MdProfile>
                    <xsl:value-of select="$prof"/>
                </cmd:MdProfile>
                <cmd:MdCollectionDisplayName/>
            </cmd:Header>
            <cmd:Resources>
                <cmd:ResourceProxyList/>
                <cmd:JournalFileProxyList/>
                <cmd:ResourceRelationList/>
                <cmd:IsPartOfList><!-- zit eigenlijk fout, moet onder resources zitten ... maar dan laadt ie niet in de editor --></cmd:IsPartOfList>
            </cmd:Resources>
            <cmd:Components>
                <xsl:apply-templates></xsl:apply-templates>
            </cmd:Components>
        </cmd:CMD>
    </xsl:template>
    
    <xsl:template match="Component|Element">
        <xsl:if test="number(@CardinalityMin) lt 1">
            <xsl:comment expand-text="yes">cmdp:{@name} is optional!</xsl:comment>
        </xsl:if>
        <xsl:if test="number(@CardinalityMax) gt 1">
            <xsl:comment expand-text="yes">cmdp:{@name} can be repeated {number(@CardinalityMax)} times!</xsl:comment>
        </xsl:if>
        <xsl:element name="cmdp:{@name}" namespace="{$cmd-profile-uri}">
            <xsl:choose>
                <xsl:when test="self::Element">
                    <xsl:choose>
                        <xsl:when test="ValueScheme/Vocabulary/enumeration/item">
                            <xsl:value-of select="ValueScheme/Vocabulary/enumeration/item[1]"/>
                            <xsl:if test="count(ValueScheme/Vocabulary/enumeration/item) gt 1">
                                <xsl:comment expand-text="yes">also valid: {string-join(ValueScheme/Vocabulary/enumeration/item[position() gt 1],', ')}</xsl:comment>
                            </xsl:if>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:text expand-text="yes">test[{@name}]</xsl:text>    
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:apply-templates/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:element>
    </xsl:template>
    
</xsl:stylesheet>