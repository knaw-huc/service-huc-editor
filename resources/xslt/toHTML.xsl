<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:cmd="http://www.clarin.eu/cmd/"
    xmlns:clariah="http://www.clariah.eu/"
    exclude-result-prefixes="cmd"
    version="3.0">
    
    <xsl:param name="cwd" select="'file:/Users/menzowi/Documents/Projects/huc-cmdi-editor/service/'"/>
    <xsl:param name="base" select="'http://localhost:1210'"/>
    <xsl:param name="app" select="'adoptie'"/>
    <xsl:param name="nr" select="'1'"/>
    <xsl:param name="config" select="doc(concat($cwd, '/data/apps/', $app, '/config.xml'))"/>
    
    <xsl:param name="style" select="'style.css'"/>
    <xsl:param name="tweak-uri" select="''"/>
    <xsl:param name="tweak-doc" select="document($tweak-uri)"/>
    
    <xsl:output method="html"/>
    
    <xsl:template match="text()"/>
    
    <xsl:template name="title">
        <xsl:variable name="xpath" select="$config/config/app/html/title"/>
        <xsl:evaluate xpath="$xpath" context-item="."/>
    </xsl:template>
    
    <xsl:template match="/">
        <html>
            <head>
                <title>
                    <xsl:call-template name="title"/>
                </title>
                <link href="{$style}" rel="stylesheet"/>
            </head>
            <body>
                <h1>
                    <xsl:call-template name="title"/>
                </h1>
                <dl>
                    <xsl:apply-templates select="/cmd:CMD/cmd:Components/*">
                        <xsl:with-param name="tweak" select="$tweak-doc/ComponentSpec"/>
                    </xsl:apply-templates>
                </dl>
            </body>
        </html>
    </xsl:template>
    
    <xsl:template match="*">
        <xsl:param name="tweak"/>
        <xsl:variable name="t" select="$tweak/*[@name=local-name(current())]"/>
        <dt class="{local-name()} level-{count(ancestor::*) - 1} {local-name($t)}">
            <xsl:choose>
                <xsl:when test="normalize-space($t/clariah:label)!=''">
                    <xsl:value-of select="normalize-space($t/clariah:label)"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="local-name()"/>
                </xsl:otherwise>
            </xsl:choose>
        </dt>
        <dd class="{local-name()} level-{count(ancestor::*) - 1} {local-name($t)}">
            <xsl:choose>
                <xsl:when test="*">
                    <dl>
                        <xsl:apply-templates>
                            <xsl:with-param name="tweak" select="$t"/>
                        </xsl:apply-templates>
                    </dl>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="."/>
                </xsl:otherwise>
            </xsl:choose>
        </dd>
    </xsl:template>        
    
</xsl:stylesheet>