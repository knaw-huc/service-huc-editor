<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:err="http://www.w3.org/2005/xqt-errors" 
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math" xmlns:clariah="http://www.clariah.eu/"
    xmlns:cmd="http://www.clarin.eu/cmd/" xmlns:js="http://www.w3.org/2005/xpath-functions"
    exclude-result-prefixes="xs math" version="3.0">

    <xsl:output method="text" encoding="UTF-8"/>

    <xsl:param name="cwd" select="'file:/Users/menzowi/Documents/GitHub/hi-ddb-stalling-editor'"/>
    <xsl:param name="base" select="'http://localhost:1210'"/>
    <xsl:param name="app" select="'stalling'"/>
    <xsl:param name="prof" select="'clarin.eu:cr1:p_1708423613607'"/>
    <xsl:param name="ent" select="'envelop'"/>
    <xsl:param name="query" select="'*'"/>
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
                    <xsl:variable name="exp" select="($conf/entity,'//*:Components/*')[1]"/>
                    <xsl:message expand-text="yes">?DBG: entity[{$exp}]</xsl:message>
                    <!-- title xpath -->
                    <xsl:variable name="txp" select="($conf/lookup,$conf/title,'string((.//*[empty(*)][normalize-space(text())!=''''])[1])')[1]"/>
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
                        <xsl:variable name="NS" as="element()">
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
                            <xsl:variable name="insts" as="item()*">
                                <xsl:choose>
                                    <xsl:when test="$exp">
                                        <xsl:message expand-text="yes">?DBG: use exp[{$exp}]</xsl:message>
                                        <xsl:try>
                                            <xsl:evaluate xpath="$exp" context-item="$rec" namespace-context="$NS" as="item()*">
                                                <xsl:with-param name="self" select="$rec//*:MdSelfLink"/>
                                            </xsl:evaluate>
                                            <xsl:catch select="()"/>
                                        </xsl:try>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:message expand-text="yes">?DBG: use builtin</xsl:message>
                                        <xsl:try>
                                            <xsl:evaluate xpath="'/*:CMD/*:Components/*'" context-item="$rec" namespace-context="$NS" as="item()*"/>
                                            <xsl:catch select="()"/>
                                        </xsl:try>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>
                            <xsl:message expand-text="yes">?DBG: insts[{count($insts)}]</xsl:message>
                            <xsl:for-each select="$insts">
                                <xsl:variable name="inst" select="."/>
                                <!--<xsl:copy-of select="$inst"/>-->
                                <xsl:message expand-text="yes">?DBG: inst[{$inst}][{local-name($inst)}]</xsl:message>
                                <xsl:variable name="lbl" as="item()*">
                                    <xsl:try>
                                        <xsl:evaluate xpath="$txp" context-item="$inst" namespace-context="$NS" as="item()*">
                                            <xsl:with-param name="self" select="$rec//*:MdSelfLink"/>
                                        </xsl:evaluate>
                                        <xsl:catch>
                                            <xsl:message expand-text="yes">ERR: title xpath[{$txp}] failed! [{$err:code}]: {$err:description}</xsl:message>
                                            <xsl:sequence select="concat('ERR[',$err:code,']: ',$err:description)"/>
                                        </xsl:catch>
                                    </xsl:try>
                                </xsl:variable>
                                <xsl:variable name="id" as="item()*">
                                    <xsl:try>
                                        <xsl:evaluate xpath="$ixp" context-item="$inst" namespace-context="$NS" as="item()*">
                                            <xsl:with-param name="self" select="$rec//*:MdSelfLink"/>
                                        </xsl:evaluate>
                                        <xsl:catch>
                                            <xsl:message expand-text="yes">ERR: id xpath[{$ixp}] failed! [{$err:code}]: {$err:description}</xsl:message>
                                            <xsl:sequence select="'err'"/>
                                        </xsl:catch>
                                    </xsl:try>
                                </xsl:variable>                          
                                <xsl:variable name="incl" as="xs:boolean">
                                    <xsl:choose>
                                        <xsl:when test="normalize-space($id)=''">
                                            <xsl:message>?DBG: no id</xsl:message>
                                            <xsl:sequence select="false()"/>
                                        </xsl:when>
                                        <xsl:when test="$query='*'">
                                            <xsl:message>?DBG: any</xsl:message>
                                            <xsl:sequence select="true()"/>
                                        </xsl:when>
                                        <xsl:when test="starts-with(normalize-space($query),'*') and ends-with(normalize-space($query),'*')">
                                            <!-- anywhere -->
                                            <xsl:message>?DBG: anywhere</xsl:message>
                                            <xsl:variable name="q" select="replace(normalize-space($query),'^\*(.*)\*$','$1')"/>
                                            <xsl:sequence select="contains(lower-case(normalize-space($lbl)),lower-case($q))"/>
                                        </xsl:when>
                                        <xsl:when test="ends-with(normalize-space($query),'*')">
                                            <!-- start -->
                                            <xsl:message>?DBG: start</xsl:message>
                                            <xsl:variable name="q" select="replace(normalize-space($query),'^(.*)\*$','$1')"/>
                                            <xsl:sequence select="starts-with(lower-case(normalize-space($lbl)),lower-case($q))"/>
                                        </xsl:when>
                                        <xsl:when test="starts-with(normalize-space($query),'*')">
                                            <!-- end -->
                                            <xsl:message>?DBG: end</xsl:message>
                                            <xsl:variable name="q" select="replace(normalize-space($query),'^\*(.*)$','$1')"/>
                                            <xsl:sequence select="ends-with(lower-case(normalize-space($lbl)),lower-case($q))"/>
                                        </xsl:when>
                                        <xsl:otherwise>
                                            <!-- exact match -->
                                            <xsl:message>?DBG: exact</xsl:message>
                                            <xsl:sequence select="lower-case(normalize-space($lbl))=lower-case(normalize-space($query))"/>
                                        </xsl:otherwise>
                                    </xsl:choose>
                                </xsl:variable>
                                <xsl:message expand-text="yes">?DBG: label[{lower-case(normalize-space($lbl))}] query[{lower-case(normalize-space($query))}] include[{$incl}]</xsl:message>
                                <xsl:if test="$incl">
                                    <js:map>
                                        <xsl:message expand-text="yes">?DBG: txp[{$txp}][{$lbl}]</xsl:message>
                                        <js:string key="value">
                                            <xsl:value-of select="$lbl"/>
                                        </js:string>
                                        <js:map key="data">
                                            <js:string key="label">
                                                <xsl:value-of select="$lbl"/>
                                            </js:string>
                                            <js:string key="uri">
                                                <xsl:text expand-text="yes">ref:/app/{$app}/profile/{$prof}/entity/{$ent}/{replace($id,'unl://','')}</xsl:text>
                                            </js:string>
                                        </js:map>
                                    </js:map>
                                </xsl:if> 
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
