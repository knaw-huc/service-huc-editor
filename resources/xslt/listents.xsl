<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math" xmlns:clariah="http://www.clariah.eu/"
    xmlns:cmd="http://www.clarin.eu/cmd/" xmlns:js="http://www.w3.org/2005/xpath-functions"
    exclude-result-prefixes="xs math" version="3.0">

    <xsl:output method="text" encoding="UTF-8"/>

    <xsl:param name="cwd" select="'file:/Users/menzowi/Documents/GitHub/service-huc-editor'"/>
    <xsl:param name="base" select="'http://localhost:1210'"/>
    <xsl:param name="app" select="'HelloWorld'"/>
    <xsl:param name="prof" select="'clarin.eu:cr1:p_1721373444008'"/>
    <xsl:param name="ent" select="'HelloWorld'"/>
    <xsl:param name="config" select="doc(concat($cwd, '/data/apps/', $app, '/config.xml'))"/>
    <xsl:param name="user" select="'anonymous'"/>

    <xsl:template name="main">
        <xsl:variable name="ents">
            <js:map>
                <js:string key="query">unit</js:string>
                <js:array key="suggestions">
                    <!-- data = {'label': res['prefLabel'],'uri': res['uri']}
                         entry = {'value': data['label'],'data': data} -->
                    <xsl:variable name="conf" select="$config//prof//*[local-name()=$ent]"/>
                    <!-- entity xpath -->
                    <xsl:variable name="exp" select="$conf/entity"/>
                    <xsl:message expand-text="yes">?DBG: entity[{$exp}]</xsl:message>
                    <!-- title xpath -->
                    <xsl:variable name="txp" select="($conf/title,'string((.//*[empty(*)][normalize-space(text())!=''''])[1])')[1]"/>
                    <xsl:message expand-text="yes">?DBG: txp[{$txp}]</xsl:message>
                    <!-- id xpath -->
                    <xsl:variable name="ixp" select="($conf/id,'/*:CMD/*:Header/*:MdSelfLink/string()')[1]"/>
                    <xsl:message expand-text="yes">?DBG: ixp[{$ixp}]</xsl:message>
                    <!-- records -->
                    <xsl:variable name="recs" select="concat($cwd, '/data/apps/', $app, '/profiles/', $prof, '/records')"/>
                    <xsl:for-each select="collection(concat($recs,'?match=record-\d+\.xml&amp;on-error=warning'))">
                        <xsl:sort select="replace(base-uri(.), '.*/record-(\d+)\.xml', '$1')" data-type="number"/>
                        <xsl:variable name="rec" select="."/>
                        <xsl:variable name="nr" select="replace(base-uri($rec), '.*/record-(\d+)\.xml', '$1')"/>
                        <xsl:variable name="url" select="concat($base, '/app/', $app, '/profile/', $prof, '/record/', $nr)"/>
                        <xsl:variable name="owner" select="string((/*:CMD/*:Header/*:MdCreator,'server')[1])"/>
                        <xsl:variable name="cmd-ns" select="
                            if ($config//app/cmdi_version = '1.2')  then
                            'http://www.clarin.eu/cmd/1'
                            else
                            'http://www.clarin.eu/cmd/'"/>
                        <xsl:variable name="cmdp-ns" select="
                            if ($config//app/cmdi_version = '1.2')  then
                            concat('http://www.clarin.eu/cmd/1/profiles/',$prof)
                            else
                            ()"/>              
                        <xsl:variable name="NS" as="element(*:ns)">
                            <xsl:element namespace="{$cmd-ns}" name="cmd:ns">
                                <xsl:if test="exists($cmdp-ns)">
                                    <xsl:namespace name="cmdp" select="$cmdp-ns"/>
                                </xsl:if>
                            </xsl:element>
                        </xsl:variable>
                        <xsl:message expand-text="yes">?DBG: r[{($config/config/app/access/read,'any')[1]}]w[{($config/config/app/access/wtite,'any')[1]}][{$user}][{base-uri($rec)}][{$url}][{$owner}]</xsl:message>
                        
                        <xsl:if test="($config/config/app/access/read,'any')[1]!='owner' or ($config/config/app/access/write,'any')[1]!='owner' or $owner=$user">
                            <!--<xsl:for-each select="//*/concat('/',string-join(ancestor-or-self::*/local-name(),'/'))[ends-with(.,$entity)]">
                                <xsl:message expand-text="yes">?DBG path[{.}]</xsl:message>
                            </xsl:for-each>-->
                            <!--<xsl:variable name="insts" select="//*[ends-with(concat('/',string-join(ancestor-or-self::*/local-name(),'/')),($entity,concat('/',//*:Components/*/local-name()))[1])]"/>-->
                            <xsl:variable name="insts">
                                <xsl:choose>
                                    <xsl:when test="$exp">
                                        <xsl:evaluate xpath="$exp" context-item="$rec" namespace-context="$NS"/>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:evaluate xpath="'/*:CMD/*:Components/*'" context-item="$rec" namespace-context="$NS" as="item()*"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>
                            <xsl:for-each select="$insts">
                                <xsl:variable name="inst" select="."/>
                                <!--<xsl:copy-of select="$inst"/>-->
                                <xsl:message expand-text="yes">?DBG: inst[{$inst}][{local-name($inst)}]</xsl:message>
                                <js:map>
                                    <xsl:variable name="lbl">
                                        <xsl:evaluate xpath="$txp" context-item="$inst" namespace-context="$NS" as="item()*"/>
                                    </xsl:variable>
                                    <xsl:message expand-text="yes">?DBG: txp[{$txp}][{$lbl}]</xsl:message>
                                    <js:string key="value">
                                        <xsl:value-of select="$lbl"/>
                                    </js:string>
                                    <js:map key="data">
                                        <js:string key="label">
                                            <xsl:value-of select="$lbl"/>
                                        </js:string>
                                        <js:string key="uri">
                                            <xsl:variable name="uri">
                                            </xsl:variable>
                                            <xsl:choose>
                                                <xsl:when test="$uri">
                                                    <xsl:value-of select="$uri"/>
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:evaluate xpath="$ixp" context-item="$rec" namespace-context="$NS" as="item()*"/>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </js:string>
                                    </js:map>
                                </js:map>
                            </xsl:for-each>
                        </xsl:if>
                    </xsl:for-each> 
                </js:array>
            </js:map>
        </xsl:variable>
        <xsl:value-of select="js:xml-to-json($ents)"/>
       <!-- <xsl:copy-of select="$ents"/>-->
    </xsl:template>

    <xsl:template match="/">
        <xsl:call-template name="main"/>
    </xsl:template>

</xsl:stylesheet>
