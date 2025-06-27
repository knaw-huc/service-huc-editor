<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xs="http://www.w3.org/2001/XMLSchema"
                xmlns:math="http://www.w3.org/2005/xpath-functions/math"
                xmlns:cue="http://www.clarin.eu/cmd/cues/1"
                exclude-result-prefixes="xs math"
                version="3.0">
  
  <xsl:param name="tweak-uri" select="''"/>
  <xsl:param name="tweak-doc" select="document($tweak-uri)"/>
  
  <xsl:param name="cwd" select="'file:/Users/menzowi/Documents/Projects/huc-cmdi-editor/service/'"/>
  <xsl:param name="app" select="'yugo'"/>
  <xsl:param name="config" select="doc(concat($cwd, '/data/apps/', $app, '/config.xml'))"/>
  <xsl:param name="prof" select="$config/config/app/def_prof"/>
  
  
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
  
  
  <xsl:template name="handleAttribute">
    <xsl:param name="tweak"/>
  </xsl:template>
  
  <xsl:template name="handleElement">
    <xsl:param name="context"/>
    <xsl:param name="tweak"/>
    <xsl:message expand-text="yes">?DBG: handleElement([{$tweak/@name}][{string-join($tweak/@cue:*/local-name(),',')}])</xsl:message>
    <xsl:choose>
      <xsl:when test="normalize-space($tweak/@cue:post-xpath-value)!=''">
        <xsl:message expand-text="yes">?DBG: handleElement([{$tweak/@cue:post-xpath-value}])</xsl:message>
        <xsl:variable name="val">
          <xsl:evaluate xpath="$tweak/@cue:post-xpath-value" namespace-context="$NS" context-item="$context"/>
        </xsl:variable>
        <xsl:message expand-text="yes">?DBG: handleElement([{$tweak/@cue:post-xpath-value}]=[{$val}])</xsl:message>
        <xsl:if test="normalize-space($val)!=''">
          <xsl:element namespace="{namespace-uri($context)}" name="{$tweak/@name}">
            <xsl:value-of select="normalize-space($val)"/>
          </xsl:element>
        </xsl:if>
      </xsl:when>
      <xsl:otherwise>
        <xsl:message expand-text="yes">?DBG: handleElement(NO @cue:post-xpath-value[{$tweak/@cue:post-xpath-value}])</xsl:message>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>
  
  <xsl:template name="handleComponent">
    <xsl:param name="tweak"/>
  </xsl:template>
  
  <xsl:template match="node() | @*">
    <xsl:copy>
      <xsl:apply-templates select="@* | node()"/>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="*:Components">
    <xsl:copy>
      <xsl:apply-templates select="@*"/>
      <xsl:apply-templates select="node()">
        <xsl:with-param name="tweak" select="$tweak-doc/ComponentSpec" tunnel="yes"/>
      </xsl:apply-templates>
    </xsl:copy>
  </xsl:template>
  
  <xsl:template match="*:Components//*">
    <xsl:param name="tweak" select="()" tunnel="yes"/>
    <xsl:variable name="this" select="."/>
    <xsl:message expand-text="yes">?DBG: tweak[{local-name($tweak)}]</xsl:message>
    <xsl:variable name="t" select="$tweak/*[@name=local-name(current())]"/>
    <xsl:copy>
      <xsl:for-each select="$t/AttributeList/Attribute">
        <xsl:variable name="a" select="."/>
        <xsl:choose>
          <xsl:when test="exists($this/@*[local-name()=$a/@name])">
            <xsl:apply-templates select="$this/@*[local-name()=$a/@name]">
              <xsl:with-param name="tweak" select="$t" tunnel="yes"/> 
            </xsl:apply-templates>
          </xsl:when>
          <xsl:otherwise>
            <xsl:call-template name="handleAttribute">
              <xsl:with-param name="tweak" select="$a"/> 
            </xsl:call-template>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:for-each>
      <xsl:apply-templates select="$this/@* except @*[local-name()=$t/AttributeList/Attribute/@name]"/>
      <xsl:apply-templates select="$this/text()"/>
      <xsl:for-each select="$t/Element">
        <xsl:variable name="e" select="."/>
        <xsl:message expand-text="yes">?DBG: {local-name($this)}/{$e/@name}[{count($this/*[local-name()=$e/@name])}]</xsl:message>
        <xsl:choose>
          <xsl:when test="exists($this/*[local-name()=$e/@name])">
            <xsl:apply-templates select="$this/*[local-name()=$e/@name]">
              <xsl:with-param name="tweak" select="$t" tunnel="yes"/> 
            </xsl:apply-templates>
          </xsl:when>
          <xsl:otherwise>
            <xsl:call-template name="handleElement">
              <xsl:with-param name="context" select="$this"/>
              <xsl:with-param name="tweak" select="$e"/> 
            </xsl:call-template>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:for-each>
      <xsl:for-each select="$t/Component">
        <xsl:variable name="c" select="."/>
        <xsl:choose>
          <xsl:when test="exists($this/*[local-name()=$c/@name])">
            <xsl:apply-templates select="$this/*[local-name()=$c/@name]">
              <xsl:with-param name="tweak" select="$t" tunnel="yes"/> 
            </xsl:apply-templates>
          </xsl:when>
          <xsl:otherwise>
            <xsl:call-template name="handleComponent">
              <xsl:with-param name="tweak" select="$c"/> 
            </xsl:call-template>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:for-each>
    </xsl:copy>
  </xsl:template>        
</xsl:stylesheet>