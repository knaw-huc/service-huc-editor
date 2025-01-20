<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:math="http://www.w3.org/2005/xpath-functions/math" xmlns:functx="http://www.functx.com"
    exclude-result-prefixes="xs math" version="3.0">

    <xsl:output method="text" encoding="UTF-8"/>

    <xsl:param name="app" select="'app'"/>
    <xsl:param name="descr" select="functx:capitalize-first(functx:camel-case-to-words(string($app), ' '))"/>
    <xsl:param name="prof" select="$template_prof"/>
    <xsl:param name="template_prof" select="()"/>

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

    <xsl:template match="/">
        <xsl:text expand-text="yes">
[app]
name="{$app}"
title="{functx:capitalize-first(functx:camel-case-to-words(string($app),' '))} Editor"
def_prof="{$prof}"
cmdi_version="1.2"

[app.access]
#users="./htp.test" # location of the htpassword file, i.e. the "users" and "owner"
read="any" # or "users" or "owner"
write="any" # or "users" or "owner"

[app.prof.{$app}]
prof="{$prof}"
title="string((/cmd:CMD/cmd:Components//cmdp:*[empty(cmdp:*)][normalize-space(text())!=''])[1])"

[app.prof.{$app}.list]
        </xsl:text>
        <xsl:choose>
            <xsl:when test="$prof = $template_prof">
                <xsl:text expand-text="yes">
[app.prof.{$app}.list.who]
xpath="string(/cmd:CMD/cmd:Components/cmdp:ShowcaseForm/cmdp:Hello)"
label="Hello"
sort="true"
filter="true"
                </xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:text expand-text="yes">
[app.prof.{$app}.list.first]
xpath="string((/cmd:CMD/cmd:Components//cmdp:*[empty(cmdp:*)][normalize-space(text())!=''])[1])"
label="First"
sort="true"# or "false"
filter="true"# or "'select'"
                </xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        
    </xsl:template>
</xsl:stylesheet>
