<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:cmd="http://www.clarin.eu/cmd/1"
    xmlns:clariah="http://www.clariah.eu/"
    xmlns:js="http://www.w3.org/2005/xpath-functions"
    exclude-result-prefixes="xs xsi js clariah"
    version="3.0">
    
    <xsl:param name="editor-base" select="'http://localhost:1211/app/yugo'"/>
    <xsl:param name="editor-tweak" select="()"/>
    
    <xsl:param name="cmd-toolkit" select="'https://infra.clarin.eu/CMDI/1.x'"/>
    <xsl:param name="cmd-envelop-xsd" select="concat($cmd-toolkit,'/xsd/cmd-envelop.xsd')"/>
    <xsl:param name="cmd-uri" select="'http://www.clarin.eu/cmd/1'"/>
    <xsl:param name="cmd-profile" select="()"/>
    <xsl:param name="cmd-1" select="'1.x'"/>
    <xsl:param name="cmd-1_1" select="'1.1'"/>
    <xsl:param name="cmd-1_2" select="'1.2'"/>
    <xsl:param name="cr-uri" select="'https://catalog.clarin.eu/ds/ComponentRegistry/rest/registry'"/>
    <xsl:param name="cr-extension-xsd" select="'/xsd'"/>
    <xsl:param name="cr-extension-xml" select="'/xml'"/>
    
    <xsl:param name="escape" select="'ccmmddii_'"/>

    <!-- namespaces (maybe unresolvable) -->
    <xsl:variable name="cmd-components" select="concat($cmd-uri,'/components')"/>
    <xsl:variable name="cmd-profiles" select="concat($cmd-uri,'/profiles')"/>

    <!-- CR REST API -->
    <xsl:variable name="cr-profiles" select="concat($cr-uri,'/',$cmd-1,'/profiles')"/>
    
    <xsl:variable name="base">
        <xsl:choose>
            <xsl:when test="normalize-space(base-uri(/*))!=''">
                <xsl:sequence select="normalize-space(base-uri(/*))"/>
            </xsl:when>
            <xsl:when test="normalize-space(/cmd:CMD/cmd:Header/cmd:MdSelfLink)!=''">
                <xsl:sequence select="normalize-space(/cmd:CMD/cmd:Header/cmd:MdSelfLink)"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:sequence select="'NULL'"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:variable>
    
    <!-- identity copy -->
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    
    <!-- try to determine the profile -->
    <xsl:variable name="profile">
        <xsl:variable name="header">
            <xsl:choose>
                <xsl:when test="matches(/cmd:CMD/cmd:Header/cmd:MdProfile,'.*(clarin.eu:cr1:p_[0-9]+).*')">
                    <xsl:sequence select="replace(/cmd:CMD/cmd:Header/cmd:MdProfile,'.*(clarin.eu:cr1:p_[0-9]+).*','$1')"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:sequence select="()"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
        <xsl:variable name="schema"> 
            <xsl:variable name="location">
                <xsl:choose>
                    <xsl:when test="normalize-space(/cmd:CMD/@xsi:noNamespaceSchemaLocation)!=''">
                        <xsl:message>WRN: <xsl:value-of select="$base"/>: CMDI 1.1 uses namespaces so @xsi:schemaLocation should be used instead of @xsi:schemaLocation!</xsl:message>
                        <xsl:sequence select="normalize-space(/cmd:CMD/@xsi:noNamespaceSchemaLocation)"/>
                    </xsl:when>
                    <xsl:when test="normalize-space(/cmd:CMD/@xsi:schemaLocation)!=''">
                        <xsl:variable name="pairs" select="tokenize(/cmd:CMD/@xsi:schemaLocation,'\s+')"/>
                        <xsl:choose>
                            <xsl:when test="count($pairs)=1">
                                <!-- WRN: improper use of @xsi:schemaLocation! -->
                                <xsl:message>WRN: <xsl:value-of select="$base"/>: @xsi:schemaLocation with single value[<xsl:value-of select="$pairs[1]"/>], should consist of (namespace URI, XSD URI) pairs!</xsl:message>
                                <xsl:sequence select="$pairs[1]"/>
                            </xsl:when>
                            <xsl:when test="exists(index-of($pairs,'http://www.clarin.eu/cmd/'))">
                                <xsl:variable name="pos" select="index-of($pairs,'http://www.clarin.eu/cmd/') + 1"/>
                                <xsl:if test="$pos le count($pairs)">
                                    <xsl:sequence select="$pairs[$pos]"/>
                                </xsl:if>
                            </xsl:when>
                            <xsl:otherwise>
                                <xsl:message>WRN: <xsl:value-of select="$base"/>: no XSD bound to the CMDI 1.1 namespace was found!</xsl:message>
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:when>
                </xsl:choose>
            </xsl:variable>
            <xsl:if test="not(matches($location,'http(s)?://catalog.clarin.eu/ds/ComponentRegistry/rest/'))">
                <xsl:message>WRN: <xsl:value-of select="$base"/>: non-ComponentRegistry XSD[<xsl:value-of select="$location"/>] will be replaced by a CMDI 1.2 ComponentRegistry XSD!</xsl:message>
            </xsl:if>
            <xsl:choose>
                <xsl:when test="matches($location,'.*(clarin.eu:cr1:p_[0-9]+).*')">
                    <xsl:sequence select="replace($location,'.*(clarin.eu:cr1:p_[0-9]+).*','$1')"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:sequence select="()"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>
            
        <xsl:if test="count($header) gt 1">
            <xsl:message>WRN: <xsl:value-of select="$base"/>: found more then one profile ID (<xsl:value-of select="string-join($header,',')"/>) in a cmd:MdProfile, will use the first one! </xsl:message>
        </xsl:if>
        <xsl:if test="count($schema) gt 1">
            <xsl:message>WRN: <xsl:value-of select="$base"/>: found more then one profile ID (<xsl:value-of select="string-join($schema,',')"/>) in a xsi:schemaLocation, will use the first one! </xsl:message>
        </xsl:if>
        <xsl:choose>
            <xsl:when test="normalize-space(($header)[1])!='' and normalize-space(($schema)[1])!=''">
                <xsl:if test="($header)[1] ne ($schema)[1]">
                    <xsl:message>WRN: <xsl:value-of select="$base"/>: the profile IDs found in cmd:MdProfile (<xsl:value-of select="($header)[1]"/>) and xsi:schemaLocation (<xsl:value-of select="($schema)[1]"/>), don't agree, will use the xsi:schemaLocation!</xsl:message>
                </xsl:if>
                <xsl:value-of select="normalize-space(($schema)[1])"/>
            </xsl:when>
            <xsl:when test="normalize-space(($header)[1])!='' and normalize-space(($schema)[1])=''">
                <xsl:value-of select="normalize-space(($header)[1])"/>
            </xsl:when>
            <xsl:when test="normalize-space(($header)[1])='' and normalize-space(($schema)[1])!=''">
                <xsl:value-of select="normalize-space(($schema)[1])"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:message terminate="yes">ERR: <xsl:value-of select="$base"/>: the profile ID can't be determined!</xsl:message>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:variable>
    
    <!-- the profile specific uris -->
    <xsl:variable name="cmd-profile-uri" select="concat($cmd-profiles,'/',$profile)"/>
    <xsl:variable name="cr-profile-xml" select="concat($cr-profiles,'/',$profile,$cr-extension-xml)"/>
    <xsl:variable name="cr-profile-xsd">
        <xsl:variable name="prof" select="if (exists($cmd-profile)) then ($cmd-profile) else (doc($cr-profile-xml))"/>
        <xsl:choose>
            <!-- '' means there was no @CMDOriginalVersion, so the original version is 1.2 (the default) -->
            <xsl:when test="$prof/ComponentSpec/normalize-space(@CMDOriginalVersion)=('','1.2')">
                <xsl:value-of select="concat($cr-uri,'/',$cmd-1_1,'/profiles/',$profile,'/',$cmd-1_2,$cr-extension-xsd)"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="concat($cr-profiles,'/',$profile,$cr-extension-xsd)"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:variable>
    <xsl:variable name="editor-tweak-xml" select="concat($editor-base,'/profile/',$profile)"/>
    
    <xsl:template match="/cmd:CMD/cmd:Components//*" priority="2">
        <xsl:variable name="cur" select="."/>
        <xsl:variable name="tweak" select="if (exists($editor-tweak)) then ($editor-tweak) else (doc($editor-tweak-xml))"/>
        <xsl:variable name="path" select="ancestor::*[. >> /cmd:CMD/cmd:Components]"/>
        <xsl:variable name="elem" select="$tweak//Element[@name=local-name($cur)][string-join(ancestor::Component/@name,'/')=string-join($path/local-name(),'/')]"/>
        <xsl:choose>
            <xsl:when test="$cur/@cmd:valueConceptLink">
                <xsl:element namespace="{$cmd-profile-uri}" name="cmdp:{local-name()}">
                    <xsl:apply-templates select="@* except @cmd:valueConceptLink"/>
                    <xsl:attribute name="cmd:valueConceptLink" select="@cmd:valueConceptLink"/>
                    <xsl:apply-templates select="node()"/>
                </xsl:element>
            </xsl:when>
            <xsl:when test="normalize-space($elem/clariah:autoCompleteURI)!=''">
                <xsl:variable name="q" select="concat(resolve-uri(string($elem/clariah:autoCompleteURI),$editor-base),'?q=',encode-for-uri(string($cur)))"/>
                <xsl:variable name="uris" select="json-to-xml(unparsed-text($q))//js:map[js:string[@key='label']=string($cur)]/js:string[@key='uri'](:[not(matches(.,'.*c=1\..*'))]:)"/>
                <xsl:choose>
                    <xsl:when test="count($uris) eq 0">
                        <xsl:message expand-text="yes">WRN: record[{/*:CMD/*:Header/*:MdSelfLink}#{string-join(ancestor-or-self::*[. >> /cmd:CMD/cmd:Components]/local-name(),'/')}] term[{$cur}] has [{count($uris)}] matches! [{$q}]->[{string-join($uris,', ')}]</xsl:message>
                        <xsl:copy-of select="$cur"/>
                    </xsl:when>
                    <xsl:when test="count($uris) gt 1">
                        <xsl:message expand-text="yes">WRN: record[{/*:CMD/*:Header/*:MdSelfLink}#{string-join(ancestor-or-self::*[. >> /cmd:CMD/cmd:Components]/local-name(),'/')}]] term[{$cur}] has [{count($uris)}] matches! [{$q}]->[{string-join($uris,', ')}]</xsl:message>
                    </xsl:when>
                </xsl:choose>
                <xsl:for-each select="$uris">
                    <xsl:variable name="uri" select="."/>
                    <xsl:for-each select="$cur">
                        <xsl:element namespace="{$cmd-profile-uri}" name="cmdp:{local-name()}">
                            <xsl:attribute namespace="{$cmd-uri}" name="cmd:valueConceptLink" select="$uri"/>
                            <xsl:apply-templates select="@*|node()"/>
                        </xsl:element>
                    </xsl:for-each>
                </xsl:for-each>
            </xsl:when>
            <xsl:otherwise>
                <xsl:element namespace="{$cmd-profile-uri}" name="cmdp:{local-name()}">
                    <xsl:apply-templates select="@*|node()"/>
                </xsl:element>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    

</xsl:stylesheet>
