<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:math="http://www.w3.org/2005/xpath-functions/math" xmlns:functx="http://www.functx.com" xmlns:js="http://www.w3.org/2005/xpath-functions" xmlns:clariah="http://www.clariah.eu/" xmlns:cue="http://www.clarin.eu/cmd/cues/1" exclude-result-prefixes="xs math functx js clariah cue" version="3.0">

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
                <xsl:variable name="attrs" as="node()*">
                    <xsl:apply-templates select="@* | * except Component except Element"/>
                    <js:string key="initialOrder" xsl:expand-text="yes">{position()}</js:string>
                </xsl:variable>
                <xsl:for-each-group select="$attrs except $attrs/self::js:array except $attrs/self::map" group-by="@key">
                    <xsl:variable name="vals" select="js:distinct-values(js:current-group())"/>
                    <xsl:if test="js:count($vals) gt 1">
                        <xsl:message expand-text="yes">component attr[{current-grouping-key()}] multiple values[{string-join($vals,',')}]</xsl:message>
                    </xsl:if>
                    <js:string key="{current-grouping-key()}" xsl:expand-text="yes">{$vals[1]}</js:string>
                </xsl:for-each-group>
                <xsl:copy-of select="($attrs/self::js:array,$attrs/self::js:map)"/>
            </js:map>
            <js:array key="content">
                <xsl:variable name="maxOrder" select="max((Component | Element)/@cue:displayOrder) + 1"/>
                <xsl:apply-templates select="Component | Element">
                    <xsl:sort select="(@cue:displayOrder, $maxOrder)[1]" data-type="number"/>
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
                <xsl:variable name="attrs" as="node()*">
                    <xsl:apply-templates select="@* | * except Component except Element"/>
                    <js:string key="initialOrder" xsl:expand-text="yes">{position()}</js:string>
                </xsl:variable>
                <xsl:for-each-group select="$attrs except $attrs/self::js:array except $attrs/self::map" group-by="@key">
                    <xsl:variable name="vals" select="js:distinct-values(js:current-group())"/>
                    <xsl:if test="js:count($vals) gt 1">
                        <xsl:message expand-text="yes">element attr[{current-grouping-key()}] multiple values[{string-join($vals,',')}]</xsl:message>
                    </xsl:if>
                    <js:string key="{current-grouping-key()}" xsl:expand-text="yes">{$vals[1]}</js:string>
                </xsl:for-each-group>
                <xsl:copy-of select="($attrs/self::js:array,$attrs/self::js:map)"/>
            </js:map>
        </js:map>
    </xsl:template>

    <xsl:template match="@*">
        <js:string key="{local-name()}" xsl:expand-text="yes">{string(.)}</js:string>
    </xsl:template>

    <xsl:template match="@CardinalityMax">
        <xsl:next-match/>
        <xsl:if test="string(.) = 'unbounded' and ../normalize-space(@Multilingual) != 'true'">
            <js:string key="duplicate">yes</js:string>
        </xsl:if>
    </xsl:template>

    <xsl:template match="@Multilingual">
        <xsl:next-match/>
        <xsl:if test="string(.) = 'true'">
            <js:string key="duplicate">yes</js:string>
        </xsl:if>
    </xsl:template>

    <xsl:function name="functx:capitalize-first" as="xs:string?">
        <xsl:param name="arg" as="xs:string?"/>

        <xsl:sequence select="
                concat(upper-case(substring($arg, 1, 1)),
                substring($arg, 2))
                "/>

    </xsl:function>

    <xsl:function name="functx:camel-case-to-words" as="xs:string">
        <xsl:param name="arg" as="xs:string?"/>
        <xsl:param name="delim" as="xs:string"/>

        <xsl:sequence select="
                concat(substring($arg, 1, 1),
                replace(substring($arg, 2), '(\p{Lu})',
                concat($delim, '$1')))
                "/>

    </xsl:function>

    <xsl:template match="@name">
        <xsl:next-match/>
        <xsl:if test="empty(parent::*/clariah:label)">
            <xsl:variable name="label" select="functx:capitalize-first(functx:camel-case-to-words(string(.), ' '))"/>
            <xsl:if test="normalize-space($label) != ''">
                <js:string key="label" xsl:expand-text="yes">{$label}</js:string>
            </xsl:if>
        </xsl:if>
    </xsl:template>

    <xsl:template match="@cue:inputHeight">
        <js:string key="height" xsl:expand-text="yes">{string(.)}</js:string>
        <js:string key="inputField">multiple</js:string>
    </xsl:template>

    <xsl:template match="@cue:inputWidth">
        <js:string key="width" xsl:expand-text="yes">{string(.)}</js:string>
        <xsl:if test="normalize-space(parent::*/@cue:inputHeight) = ''">
            <js:string key="inputField">single</js:string>
        </xsl:if>
    </xsl:template>

    <xsl:template match="clariah:*">
        <js:string key="{local-name()}" xsl:expand-text="yes">{string(.)}</js:string>
    </xsl:template>

    <xsl:template match="clariah:value"/>

    <xsl:template match="AutoValue">
        <xsl:choose>
            <xsl:when test="string(.) = 'now'">
                <js:string key="autoValue" xsl:expand-text="yes">{format-date(current-date(),'[Y]-[M01]-[D01]')}</js:string>
            </xsl:when>
            <xsl:otherwise>
                <js:string key="autoValue" xsl:expand-text="yes">{string(.)}</js:string>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

    <xsl:template match="AttributeList">
        <js:array key="attributeList">
            <!-- TODO -->
        </js:array>
    </xsl:template>

    <xsl:template match="ValueScheme">
        <xsl:choose>
            <xsl:when test="normalize-space(pattern) != ''">
                <js:string key="pattern" xsl:expand-text="yes">{normalize-space(pattern)}</js:string>
                <js:string key="ValueScheme">string</js:string>
            </xsl:when>
            <xsl:when test="Vocabulary">
                <js:array key="ValueScheme">
                    <js:array>
                        <xsl:for-each select=".//item">
                            <js:map>
                                <xsl:if test="normalize-space(clariah:label) != ''">
                                    <js:string key="label" xsl:expand-text="yes">{normalize-space(clariah:label)}</js:string>
                                </xsl:if>
                                <xsl:if test="normalize-space(clariah:value) != ''">
                                    <js:string key="value" xsl:expand-text="yes">{normalize-space(clariah:value)}</js:string>
                                </xsl:if>
                            </js:map>
                        </xsl:for-each>
                    </js:array>
                </js:array>
            </xsl:when>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>
