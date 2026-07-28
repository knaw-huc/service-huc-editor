<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:math="http://www.w3.org/2005/xpath-functions/math" xmlns:functx="http://www.functx.com" xmlns:js="http://www.w3.org/2005/xpath-functions" xmlns:clariah="http://www.clariah.eu/" xmlns:cue="http://www.clarin.eu/cmd/cues/1" exclude-result-prefixes="xs math functx js clariah cue" version="3.0">

    <xsl:output method="text" encoding="UTF-8"/>
    
    <xsl:template match="text()"/>

    <xsl:template match="/ComponentSpec">
        <xsl:variable name="prof">
            <js:map>
                <js:string key="type">profile</js:string>
                <js:number key="level" xsl:expand-text="yes">0</js:number>
                <js:string key="id" xsl:expand-text="yes">{Header/ID}</js:string>
                <js:string key="name" xsl:expand-text="yes">{Header/Name}</js:string>
                <js:array key="description">
                    <xsl:for-each select="Header/Description[normalize-space(.)!='']">
                        <js:map>
                            <xsl:apply-templates select="@*"/>
                            <js:string key="@value" xsl:expand-text="yes">{normalize-space(.)}</js:string>
                        </js:map>
                    </xsl:for-each>
                </js:array>
                <js:array key="content">
                    <xsl:if test="@isProfile = 'true'">
                        <xsl:apply-templates select="Component">
                            <xsl:with-param name="level" select="1" tunnel="yes"/>
                        </xsl:apply-templates>
                    </xsl:if>
                </js:array>
            </js:map>
        </xsl:variable>
        <!--<xsl:copy-of select="$prof"/>-->
        <xsl:value-of select="js:xml-to-json($prof)"/>
    </xsl:template>

    <xsl:template match="Component">
        <xsl:param name="level" tunnel="yes"/>
        <xsl:variable name="c" select="."/>
        <js:map>
            <js:string key="type">component</js:string>
            <js:number key="level" xsl:expand-text="yes">{$level}</js:number>
            <js:string key="id" xsl:expand-text="yes">{generate-id()}</js:string>
            <js:string key="name" xsl:expand-text="yes">{@name}</js:string>
            <xsl:apply-templates select="@conceptlink"/>
            <js:array key="documentation">
                <xsl:for-each select="Documentation[normalize-space(.)!='']">
                    <js:map>
                        <xsl:apply-templates select="@*"/>
                        <js:string key="@value" xsl:expand-text="yes">{normalize-space(.)}</js:string>
                    </js:map>
                </xsl:for-each>
            </js:array>
            <js:map key="cardinality" xsl:expand-text="yes">
                <js:string key="min">{(@CardinalityMin,'1')[1]}</js:string>
                <js:string key="max">{(@CardinalityMax,'1')[1]}</js:string>
            </js:map>
            <js:map key="cues">
                <xsl:variable name="cues" as="node()*">
                    <xsl:apply-templates select="@cue:* | (* except Component except Element)"/>
                    <js:string key="initialOrder" xsl:expand-text="yes">{position()}</js:string>
                </xsl:variable>
                <xsl:for-each-group select="$cues except $cues/self::js:array except $cues/self::map" group-by="@key">
                    <xsl:variable name="vals" select="js:distinct-values(js:current-group())"/>
                    <xsl:if test="js:count($vals) gt 1">
                        <xsl:message expand-text="yes">!WARNING: component[{string-join(reverse($c/ancestor-or-self::Component/@name),'/')}] cue[{current-grouping-key()}] has multiple values[{string-join($vals,',')}] taking the last one!</xsl:message>
                    </xsl:if>
                    <js:string key="{current-grouping-key()}" xsl:expand-text="yes">{$vals[last()]}</js:string>
                </xsl:for-each-group>
                <xsl:copy-of select="($cues/self::js:array,$cues/self::js:map)"/>
                <xsl:if test="empty(clariah:label)">
                    <xsl:variable name="label" select="functx:capitalize-first(functx:camel-case-to-words(string(@name), ' '))"/>
                    <xsl:if test="normalize-space($label) != ''">
                        <js:string key="label" xsl:expand-text="yes">{$label}</js:string>
                    </xsl:if>
                </xsl:if>
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
        <xsl:variable name="e" select="."/>
        <js:map>
            <js:string key="type">element</js:string>
            <js:number key="level" xsl:expand-text="yes">{$level}</js:number>
            <js:string key="id" xsl:expand-text="yes">{generate-id()}</js:string>
            <js:string key="name" xsl:expand-text="yes">{@name}</js:string>
            <xsl:apply-templates select="@conceptlink"/>
            <js:map key="cardinality" xsl:expand-text="yes">
                <js:string key="min">{(@CardinalityMin,'1')[1]}</js:string>
                <js:string key="max">{(@CardinalityMax,'1')[1]}</js:string>
                <js:string key="multilingual">{(if (@Multilingual='true') then ('true') else ('false'),'false')[1]}</js:string>
            </js:map>
            <js:map key="values" xsl:expand-text="yes">
                <js:string key="scheme">{(@ValueScheme,'string')[1]}</js:string>
                <xsl:apply-templates select="ValueScheme"/>
            </js:map>
            <js:map key="cues">
                <xsl:variable name="cues" as="node()*">
                    <xsl:apply-templates select="@cue:* | (* except Component except Element except ValueScheme)"/>
                    <js:string key="initialOrder" xsl:expand-text="yes">{position()}</js:string>
                </xsl:variable>
                <xsl:for-each-group select="$cues except $cues/self::js:array except $cues/self::map" group-by="@key">
                    <xsl:variable name="vals" select="js:distinct-values(js:current-group())"/>
                    <xsl:if test="js:count($vals) gt 1">
                        <xsl:message expand-text="yes">!WARNING: element[{string-join(reverse($e/ancestor::Component/@name),'/')}/{$e/@name}] cue[{current-grouping-key()}] hasmultiple values[{string-join($vals,',')}] taking the last one!</xsl:message>
                    </xsl:if>
                    <js:string key="{current-grouping-key()}" xsl:expand-text="yes">{$vals[1]}</js:string>
                </xsl:for-each-group>
                <xsl:copy-of select="($cues/self::js:array,$cues/self::js:map)"/>
                <xsl:if test="empty(clariah:label)">
                    <xsl:variable name="label" select="functx:capitalize-first(functx:camel-case-to-words(string(@name), ' '))"/>
                    <xsl:if test="normalize-space($label) != ''">
                        <js:string key="label" xsl:expand-text="yes">{$label}</js:string>
                    </xsl:if>
                </xsl:if>
            </js:map>
        </js:map>
    </xsl:template>

    <xsl:template match="@*">
        <js:string key="{local-name()}" xsl:expand-text="yes">{string(.)}</js:string>
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
    
    <xsl:template match="clariah:explanation[empty(preceding-sibling::clariah:explanation)]">
        <js:array key="explanation">
            <xsl:for-each select="../clariah:explanation">
                <js:map>
                    <xsl:apply-templates select="@*"/>
                    <js:string key="@value" xsl:expand-text="yes">{normalize-space(.)}</js:string>
                </js:map>
            </xsl:for-each>
        </js:array>
    </xsl:template>
    
    <xsl:template match="clariah:explanation[exists(preceding-sibling::clariah:explanation)]"/>

    <xsl:template match="clariah:label[empty(preceding-sibling::clariah:label)]">
        <js:array key="label">
            <xsl:for-each select="../clariah:label[normalize-space(.)!='']">
                <js:map>
                    <xsl:apply-templates select="@*"/>
                    <js:string key="@value" xsl:expand-text="yes">{normalize-space(.)}</js:string>
                </js:map>
            </xsl:for-each>
        </js:array>
    </xsl:template>
    
    <xsl:template match="clariah:label[exists(preceding-sibling::clariah:label)]"/>

    <xsl:template match="item">
        <js:map>
            <xsl:choose>
                <xsl:when test="exists(clariah:value)">
                    <xsl:for-each select="clariah:value">
                        <js:string key="@value" xsl:expand-text="yes">{normalize-space(string-join(text()))}</js:string>
                        <js:map key="cues">
                            <js:array key="label">
                                <xsl:for-each select="clariah:label[normalize-space(.)!='']">
                                    <js:map>
                                        <xsl:apply-templates select="@*"/>
                                        <js:string key="@value" xsl:expand-text="yes">{normalize-space(.)}</js:string>
                                    </js:map>
                                </xsl:for-each>
                            </js:array>
                        </js:map>
                    </xsl:for-each>
                </xsl:when>
                <xsl:otherwise>
                    <js:string key="@value" xsl:expand-text="yes">{normalize-space(string-join(text()))}</js:string>
                </xsl:otherwise>
            </xsl:choose>
        </js:map>
    </xsl:template>

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

    <xsl:template match="AttributeList[exists(*)]">
        <xsl:message expand-text="yes">!WARNING: attributes[{string-join(reverse(ancestor::Component/@name),'/')}/@*] are not supported, so skipped!</xsl:message>
    </xsl:template>

    <xsl:template match="ValueScheme">
        <xsl:choose>
            <xsl:when test="normalize-space(pattern) != ''">
                <js:string key="pattern" xsl:expand-text="yes">{normalize-space(pattern)}</js:string>
            </xsl:when>
            <xsl:when test="Vocabulary">
                <js:array key="vocabulary">
                    <xsl:apply-templates select=".//item"/>
                </js:array>
            </xsl:when>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template match="@xml:lang">
        <js:string key="@language" xsl:expand-text="yes">{string(.)}</js:string>
    </xsl:template>
    

</xsl:stylesheet>
