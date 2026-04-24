<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math"
    xmlns:cue="http://www.clarin.eu/cmd/cues/1"
    xmlns:clariah="http://www.clariah.eu/"
    xmlns:js="http://www.w3.org/2005/xpath-functions" exclude-result-prefixes="xs math js"
    version="3.0">

    <xsl:output method="text" encoding="UTF-8"/>

    <xsl:param name="rec-nr" select="replace(base-uri(),'.*record-(\d+).xml','$1')"/>
    <xsl:param name="prof-doc" select="'file:/Users/menzowi/Documents/GitHub/ecodices-editor/data/apps/ecodices/profiles/clarin.eu:cr1:p_1744616237097/clarin.eu:cr1:p_1744616237097.xml'"/>
    <xsl:param name="prof-xml" select="doc($prof-doc)"/>

    <xsl:template match="text()"/>

    <xsl:template match="node() | @*" mode="prof">
        <xsl:copy>
            <xsl:apply-templates select="node() | @*" mode="#current"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="/js:map" mode="prof">
        <xsl:copy>
            <xsl:attribute name="key" select="'content'"/>
            <xsl:apply-templates select="@* | node()" mode="#current"/>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="/*:CMD">
        <xsl:variable name="rec">
            <js:map>
                <xsl:if test="js:normalize-space($rec-nr) != ''">
                    <js:string key="nr" xsl:expand-text="yes"
                        >{js:normalize-space($rec-nr)}</js:string>
                </xsl:if>
                <js:string key="id" xsl:expand-text="yes">{*:Header/*:MdProfile}</js:string>
                <js:string key="when" xsl:expand-text="yes"
                    >{(*:Header/*:MdCreationDate/@*:epoch,*:Header/*:MdCreationDate)[1]}</js:string>
                <js:map key="record">
                    <xsl:apply-templates select="//*:Components/*">
                        <xsl:with-param name="tweak" select="$prof-xml/ComponentSpec"/>
                    </xsl:apply-templates>
                </js:map>
            </js:map>
        </xsl:variable>
        <!--<xsl:copy-of select="$rec"/>-->
        <xsl:value-of select="js:xml-to-json($rec)"/>
    </xsl:template>
    
    <xsl:template match="@*">
        <js:string key="@{local-name()}">
            <xsl:value-of select="."/>
        </js:string>
    </xsl:template>
    
    <xsl:function name="clariah:toMax" as="xs:double">
        <xsl:param name="max"/>
        <xsl:choose>
            <xsl:when test="normalize-space($max)=''">
                <xsl:sequence select="1"/>
            </xsl:when>
            <xsl:when test="normalize-space($max)='unbounded'">
                <xsl:sequence select="2147483647"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:sequence select="number(normalize-space($max))"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:function>

    <xsl:template match="*">
        <xsl:param name="tweak"/>
        <xsl:variable name="t" select="$tweak/*[@name=local-name(current())]"/>
        <xsl:variable name="name" select="local-name()"/>
        <xsl:choose>
            <xsl:when test="exists(*)">
                <js:map>
                    <xsl:if test="clariah:toMax($t/@CardinalityMax) eq 1">
                        <xsl:attribute name="key" select="$name"/>
                    </xsl:if>
                    <xsl:if test="exists(@*)">
                        <xsl:apply-templates select="@*"/>
                    </xsl:if>
                    <xsl:for-each-group select="*" group-by="local-name()">
                        <xsl:variable name="tt" select="$t/*[@name=current-grouping-key()]"/>
                        <xsl:choose>
                            <xsl:when test="clariah:toMax($tt/@CardinalityMax) eq 1">
                                <xsl:apply-templates select="current-group()">
                                    <xsl:with-param name="tweak" select="$t"/>
                                </xsl:apply-templates>
                            </xsl:when>
                            <xsl:otherwise>
                                <js:array key="{current-grouping-key()}">
                                    <xsl:apply-templates select="current-group()">
                                        <xsl:with-param name="tweak" select="$t"/>
                                    </xsl:apply-templates>
                                </js:array>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:for-each-group>
                </js:map>
            </xsl:when>
            <xsl:otherwise>
                <js:map>
                    <xsl:if test="clariah:toMax($t/@CardinalityMax) eq 1">
                        <xsl:attribute name="key" select="$name"/>
                    </xsl:if>
                    <xsl:apply-templates select="@*"/>
                    <js:string key="@value">
                        <xsl:value-of select="."/>
                    </js:string>
                </js:map>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="@*:valueConceptLink">
        <js:string key="@valueConceptLink" xsl:expand-text="yes">{string(.)}</js:string>
    </xsl:template>

    <xsl:template match="@xml:lang">
        <js:string key="@language" xsl:expand-text="yes">{string(.)}</js:string>
    </xsl:template>

</xsl:stylesheet>
