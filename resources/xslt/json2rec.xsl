<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:functx="http://www.functx.com" xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math"
    xmlns:js="http://www.w3.org/2005/xpath-functions" exclude-result-prefixes="xs math functx"
    version="3.0">

    <xsl:param name="js-uri" select="'file:/Users/menzowi/Documents/GitHub/hi-ddb-stalling-editor/scripts/bete-record-30.json'"/>
    <xsl:param name="js-doc" select="
            if (js:unparsed-text-available($js-uri)) then
                (unparsed-text($js-uri))
            else
                ()"/>
    <xsl:param name="js-xml" select="js:json-to-xml($js-doc)"/>
    <xsl:param name="vers" select="'1.2'"/>
    <xsl:param name="prof" select="'unknown'"/>
    <xsl:param name="user" select="'test'"/>
    <xsl:param name="self" select="'unl://1'"/>
    <xsl:param name="when" select="()"/>

    <xsl:variable name="cmd-envelop-xsd" select="'https://infra.clarin.eu/CMDI/1.x/xsd/cmd-envelop.xsd'"/>
    <xsl:variable name="cmd-profile-xsd" select="concat('http://catalog.clarin.eu/ds/ComponentRegistry/rest/registry/', $vers, '/profiles/', $prof, '/xsd')"/>
    

    <xsl:variable name="cmd-ns" select="
            if ($vers = '1.1') then
                'http://www.clarin.eu/cmd/'
            else
                'http://www.clarin.eu/cmd/1'"/>
    <xsl:variable name="cmdp-ns" select="
            if ($vers = '1.1') then
                'http://www.clarin.eu/cmd/'
            else
                concat('http://www.clarin.eu/cmd/1/profiles/', $prof)"/>

    <xsl:function name="functx:repeat-string" as="xs:string" xmlns:functx="http://www.functx.com">
        <xsl:param name="stringToRepeat" as="xs:string?"/>
        <xsl:param name="count" as="xs:integer"/>
        <xsl:sequence select="
                string-join((for $i in 1 to $count
                return
                    $stringToRepeat),
                '')
                "/>
    </xsl:function>

    <xsl:function name="functx:pad-integer-to-length" as="xs:string"
        xmlns:functx="http://www.functx.com">
        <xsl:param name="integerToPad" as="xs:anyAtomicType?"/>
        <xsl:param name="length" as="xs:integer"/>
        <xsl:sequence select="
                if ($length &lt; string-length(string($integerToPad)))
                then
                    error(xs:QName('functx:Integer_Longer_Than_Length'))
                else
                    concat
                    (functx:repeat-string(
                    '0', $length - string-length(string($integerToPad))),
                    string($integerToPad))
                "/>
    </xsl:function>

    <xsl:function name="functx:date" as="xs:date">
        <xsl:param name="year" as="xs:anyAtomicType"/>
        <xsl:param name="month" as="xs:anyAtomicType"/>
        <xsl:param name="day" as="xs:anyAtomicType"/>
        <xsl:sequence select="
                xs:date(
                concat(
                functx:pad-integer-to-length(xs:integer($year), 4), '-',
                functx:pad-integer-to-length(xs:integer($month), 2), '-',
                functx:pad-integer-to-length(xs:integer($day), 2)))
                "/>
    </xsl:function>

    <xsl:template name="main">
        <xsl:message expand-text="yes">JSON[{$js-doc}]</xsl:message>
        <xsl:element namespace="{$cmd-ns}" name="cmd:CMD">
            <xsl:attribute namespace="http://www.w3.org/2001/XMLSchema-instance"
                name="xsi:schemaLocation">
                <xsl:choose>
                    <xsl:when test="$vers = '1.1'">
                        <xsl:value-of select="$cmd-ns"/>
                        <xsl:text> </xsl:text>
                        <xsl:value-of select="$cmd-profile-xsd"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="$cmd-ns"/>
                        <xsl:text> </xsl:text>
                        <xsl:value-of select="$cmd-envelop-xsd"/>
                        <xsl:text> </xsl:text>
                        <xsl:value-of select="$cmdp-ns"/>
                        <xsl:text> </xsl:text>
                        <xsl:value-of select="$cmd-profile-xsd"/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:attribute>
            <xsl:attribute name="CMDVersion" select="$vers"/>
            <xsl:element namespace="{$cmd-ns}" name="cmd:Header">
                <xsl:element namespace="{$cmd-ns}" name="cmd:MdCreator">
                    <xsl:value-of select="$user"/>
                </xsl:element>
                <xsl:choose>
                    <xsl:when test="$when castable as xs:date">
                        <xsl:element namespace="{$cmd-ns}" name="cmd:MdCreationDate">
                            <xsl:value-of
                                select="format-date(xs:date($when), '[Y0001]-[M01]-[D01]')"/>
                        </xsl:element>
                    </xsl:when>
                    <xsl:when test="$when castable as xs:long">
                        <xsl:variable name="wdt" select="xs:dateTime('1970-01-01T00:00:00') + xs:dayTimeDuration(concat('PT', $when, 'S'))"/>
                        <xsl:variable name="wd" select="functx:date(year-from-dateTime($wdt),month-from-dateTime($wdt),day-from-dateTime($wdt))"/>
                        <xsl:element namespace="{$cmd-ns}" name="cmd:MdCreationDate">
                            <xsl:attribute namespace="http://www.clariah.eu/" name="clariah:epoch"
                                select="$when"/>
                            <xsl:value-of
                                select="format-date(xs:date($wd), '[Y0001]-[M01]-[D01]')"/>
                        </xsl:element>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:element namespace="{$cmd-ns}" name="cmd:MdCreationDate">
                            <xsl:attribute namespace="http://www.clariah.eu/" name="clariah:epoch"
                                select="floor((current-dateTime() - xs:dateTime('1970-01-01T00:00:00')) div xs:dayTimeDuration('PT1S'))"/>
                            <xsl:value-of
                                select="format-date(current-date(),'[Y0001]-[M01]-[D01]')"/>
                        </xsl:element>
                    </xsl:otherwise>
                </xsl:choose>
                <xsl:element namespace="{$cmd-ns}" name="cmd:MdSelfLink">
                    <xsl:value-of select="$self"/>
                </xsl:element>
                <xsl:element namespace="{$cmd-ns}" name="cmd:MdProfile">
                    <xsl:value-of select="$prof"/>
                </xsl:element>
                <xsl:element namespace="{$cmd-ns}" name="cmd:MdCollectionDisplayName"></xsl:element>
            </xsl:element>
            <xsl:element namespace="{$cmd-ns}" name="cmd:Resources">
                <xsl:element namespace="{$cmd-ns}" name="cmd:ResourceProxyList"/>
                <xsl:element namespace="{$cmd-ns}" name="cmd:JournalFileProxyList"/>
                <xsl:element namespace="{$cmd-ns}" name="cmd:ResourceRelationList"/>
                <xsl:element namespace="{$cmd-ns}" name="cmd:IsPartOfList"/>
            </xsl:element>
            <xsl:element namespace="{$cmd-ns}" name="cmd:Components">
                <xsl:variable name="payload">
                    <xsl:choose>
                        <xsl:when test="exists($js-xml/js:map/js:array[@key='record']/js:map)">
                            <xsl:message expand-text="yes">DBG: found record</xsl:message>
                            <xsl:sequence select="$js-xml/js:map/js:array[@key='record']/js:map"/>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:sequence select="$js-xml/js:array/js:map"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </xsl:variable>
                <xsl:message expand-text="yes">DBG: found records[{count($payload)}]</xsl:message>
                <xsl:apply-templates select="$payload">
                    <xsl:sort select="*[@key = 'sortOrder']" data-type="number"/>
                </xsl:apply-templates>
            </xsl:element>
        </xsl:element>
    </xsl:template>

    <xsl:template match="js:map[js:string[@key = 'type'] = 'component']">
        <xsl:element namespace="{$cmdp-ns}"
            name="{if($vers='1.1') then 'cmd' else 'cmdp'}:{js:string[@key='name']}">
            <xsl:for-each select="js:map[@key = 'attributes']/*">
                <xsl:choose>
                    <xsl:when test="@key = 'lang'">
                        <xsl:attribute name="xml:lang" select="."/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:comment>
                                <xsl:attribute name="{@key}" select="."/>
                            </xsl:comment>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:for-each>
            <xsl:apply-templates select="js:array[@key = ('content','value')]/js:map">
                <xsl:sort select="*[@key = 'sortOrder']" data-type="number"/>
            </xsl:apply-templates>
        </xsl:element>
    </xsl:template>

    <xsl:template match="js:map[js:string[@key = 'type'] = 'element']">
        <xsl:variable name="e" select="."/>
        <xsl:choose>
            <xsl:when test="exists(js:string[@key='value'])">
                <xsl:element namespace="{$cmdp-ns}"
                    name="{if($vers='1.1') then 'cmd' else 'cmdp'}:{$e/js:string[@key='name']}">
                    <xsl:for-each select="js:map[@key = 'attributes']/*">
                        <xsl:choose>
                            <xsl:when test="@key = ('lang','xml:lang')">
                                <xsl:attribute name="xml:lang" select="."/>
                            </xsl:when>
                            <xsl:when test="@key = 'uri'">
                                <xsl:attribute namespace="{$cmd-ns}" name="cmd:valueConceptLink" select="."/>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:comment>
                                <xsl:attribute name="{@key}" select="."/>
                            </xsl:comment>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:for-each>
                    <xsl:value-of select="js:string[@key = 'value']"/>
                </xsl:element>
            </xsl:when>
            <xsl:otherwise>
                <xsl:for-each select="$e/js:array[@key = 'content']/js:map">
                    <xsl:element namespace="{$cmdp-ns}"
                        name="{if($vers='1.1') then 'cmd' else 'cmdp'}:{$e/js:string[@key='name']}">
                        <xsl:for-each select="js:map[@key = 'attributes']/*">
                            <xsl:choose>
                                <xsl:when test="@key = 'lang'">
                                    <xsl:attribute name="xml:lang" select="."/>
                                </xsl:when>
                                <xsl:when test="@key = 'uri'">
                                    <xsl:attribute namespace="{$cmd-ns}" name="cmd:valueConceptLink" select="."/>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:comment>
                                <xsl:attribute name="{@key}" select="."/>
                            </xsl:comment>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:for-each>
                        <xsl:value-of select="js:string[@key = 'value']"/>
                    </xsl:element>
                </xsl:for-each>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>
