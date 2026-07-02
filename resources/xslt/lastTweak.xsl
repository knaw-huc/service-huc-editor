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

    <xsl:template match="@cue:enable">
        <xsl:variable name="pre" select="normalize-space(replace(.,'^(.*)=.*$','$1'))"/>
        <xsl:choose>
            <xsl:when test="matches($pre,'//?')">
                <xsl:variable name="co" select="replace($pre,'^(.*)//?.*$','$1')"/>
                <xsl:variable name="el" select="replace($pre,'^.*//?(.*)$','$1')"/>
                <xsl:message expand-text="yes">DBG: comp[{$co}]//elem[{$el}]</xsl:message>
                <xsl:choose>
                    <xsl:when test="exists(../ancestor::Component[@name=$co])">
                        <xsl:choose>
                            <xsl:when test="exists(../ancestor::Component[@name=$co]//Element[@name=$el])">
                                <xsl:copy>
                                    <xsl:apply-templates select="node() | @*"/>
                                </xsl:copy>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:message expand-text="yes">ERR: the descendant element[{$el}] of ancestor component[{$co}] in enable[{.}] on element[{../@name}] can't be found!</xsl:message>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:message expand-text="yes">ERR: the ancestor component[{$co}] in enable[{.}] on element[{../@name}] can't be found!</xsl:message>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:when>
            <xsl:otherwise>
                <xsl:choose>
                    <xsl:when test="not(exists(../preceding-sibling::Element[@name=$pre]))">
                        <xsl:choose>
                            <xsl:when test="exists(../preceding::Element[@name=$pre])">
                                <xsl:message expand-text="yes">WRN: the preceding element[{$pre}]  in enable[{.}] on element[{../@name}] is found, but only preceding siblings are supported!</xsl:message>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:message expand-text="yes">ERR: the preceding (sibling) element[{$pre}] in enable[{.}] on element[{../@name}] can't be found!</xsl:message>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:copy>
                            <xsl:apply-templates select="node() | @*"/>
                        </xsl:copy>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:otherwise>
        </xsl:choose>
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