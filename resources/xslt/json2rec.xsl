<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:functx="http://www.functx.com" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:math="http://www.w3.org/2005/xpath-functions/math" xmlns:js="http://www.w3.org/2005/xpath-functions" exclude-result-prefixes="xs math functx" version="3.0">

    <xsl:param name="js-uri" select="'file:/Users/menzowi/Documents/Projects/huc-cmdi-editor/service/tests/record-fromEditor.json'"/>
    <xsl:param name="js-doc" select="
            if (js:unparsed-text-available($js-uri)) then
                (unparsed-text($js-uri))
            else
                ()"/>
    <xsl:param name="js-xml" select="js:json-to-xml($js-doc)"/>

    <xsl:param name="prof" select="'unknown'"/>
    <xsl:param name="user" select="'test'"/>
    <xsl:param name="self" select="'unl://1'"/>
    <xsl:param name="when" select="()"/>

    <xsl:variable name="cmd-ns" select="'http://www.clarin.eu/cmd/'"/>
    <xsl:variable name="cmdp-ns" select="'http://www.clarin.eu/cmd/'"/>
    
    <xsl:function name="functx:repeat-string" as="xs:string"
        xmlns:functx="http://www.functx.com">
        <xsl:param name="stringToRepeat" as="xs:string?"/>
        <xsl:param name="count" as="xs:integer"/>
        <xsl:sequence select="
            string-join((for $i in 1 to $count return $stringToRepeat),
            '')
        "/>        
    </xsl:function>

    <xsl:function name="functx:pad-integer-to-length" as="xs:string"
        xmlns:functx="http://www.functx.com">
        <xsl:param name="integerToPad" as="xs:anyAtomicType?"/>
        <xsl:param name="length" as="xs:integer"/>
        <xsl:sequence select="
            if ($length &lt; string-length(string($integerToPad)))
            then error(xs:QName('functx:Integer_Longer_Than_Length'))
            else concat
            (functx:repeat-string(
            '0',$length - string-length(string($integerToPad))),
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
            functx:pad-integer-to-length(xs:integer($year),4),'-',
            functx:pad-integer-to-length(xs:integer($month),2),'-',
            functx:pad-integer-to-length(xs:integer($day),2)))
        "/>    
    </xsl:function>
    
    <xsl:template name="main">
        <xsl:message expand-text="yes">JSON[{$js-doc}]</xsl:message>
        <cmd:CMD xmlns:clariah="http://www.clariah.eu/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:cmd="http://www.clarin.eu/cmd/" xsi:schemaLocation="http://www.clarin.eu/cmd/ http://catalog.clarin.eu/ds/ComponentRegistry/rest/registry/profiles/{$prof}/xsd" CMDVersion="1.1">
            <cmd:Header>
                <cmd:MdCreator xsl:expand-text="yes">{$user}</cmd:MdCreator>
                <xsl:choose>
                    <xsl:when test="$when castable as xs:date">
                        <cmd:MdCreationDate xsl:expand-text="yes">{format-date(xs:date($when),'[Y0001]-[M01]-[D01]')}</cmd:MdCreationDate>
                    </xsl:when>
                    <xsl:when test="$when castable as xs:long">
                        <xsl:variable name="wdt" select="xs:dateTime('1970-01-01T00:00:00') + xs:dayTimeDuration(concat('PT', $when, 'S'))"/>
                        <xsl:variable name="wd" select="functx:date(year-from-dateTime($wdt),month-from-dateTime($wdt),day-from-dateTime($wdt))"/>
                        <cmd:MdCreationDate clariah:epoch="{$when}" xsl:expand-text="yes">{format-date($wd,'[Y0001]-[M01]-[D01]')}</cmd:MdCreationDate>
                    </xsl:when>
                    <xsl:otherwise>
                        <cmd:MdCreationDate clariah:epoch="{floor((current-dateTime() - xs:dateTime('1970-01-01T00:00:00')) div xs:dayTimeDuration('PT1S'))}" xsl:expand-text="yes">{format-date(current-date(),'[Y0001]-[M01]-[D01]')}</cmd:MdCreationDate>
                    </xsl:otherwise>
                </xsl:choose>
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
                    <xsl:sort select="*[@key = 'sortOrder']" data-type="number"/>
                </xsl:apply-templates>
            </cmd:Components>
        </cmd:CMD>
    </xsl:template>

    <xsl:template match="/">
        <xsl:call-template name="main"/>
    </xsl:template>

    <xsl:template match="js:map[js:string[@key = 'type'] = 'component']">
        <xsl:element name="cmd:{js:string[@key='name']}" namespace="{$cmd-ns}">
            <xsl:apply-templates select="js:array[@key = 'content']/js:map">
                <xsl:sort select="*[@key = 'sortOrder']" data-type="number"/>
            </xsl:apply-templates>
        </xsl:element>
    </xsl:template>

    <xsl:template match="js:map[js:string[@key = 'type'] = 'element']">
        <xsl:element name="cmd:{js:string[@key='name']}" namespace="{$cmd-ns}">
            <xsl:value-of select="js:array[@key = 'content']/js:map/js:string[@key = 'value']"/>
        </xsl:element>
    </xsl:template>

</xsl:stylesheet>
