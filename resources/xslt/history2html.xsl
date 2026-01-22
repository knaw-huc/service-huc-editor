<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xs="http://www.w3.org/2001/XMLSchema"
                xmlns:math="http://www.w3.org/2005/xpath-functions/math"
                xmlns:fn="http://www.w3.org/2005/xpath-functions" 
                exclude-result-prefixes="xs math fn"
                expand-text="yes" version="3.0">
    
    
    <xsl:output method="html"/>
    
    <xsl:param name="base" select="'http://localhost:1210'"/>

    
    <xsl:param name="js-uri" select="'file:/Users/menzowi/Documents/GitHub/hi-ddb-stalling-editor/scripts/bete-record-30.json'"/>
    <xsl:param name="js-doc" select="
        if (unparsed-text-available($js-uri)) then
            (unparsed-text($js-uri))
        else
            ()"/>
    <xsl:param name="js-xml" select="json-to-xml($js-doc)"/> 
    
    <xsl:variable name="recordnumber" select="$js-xml/fn:map/fn:string[@key = 'nr']"/>
    
    <xsl:template name="main">
        <xsl:for-each select="$js-xml">
            <html>
                <head>
                    <title>history for record [{$recordnumber}] </title>
                    <link rel="stylesheet" href="{$base}/static/css/style.css" type="text/css"/>
                    <link rel="stylesheet" href="{$base}/static/css/datatable.min.css" type="text/css"/>
                    <link rel="stylesheet" href="{$base}/static/js/lib/jquery-ui/jquery-ui.css"/>
                    <script type="text/javascript" src="{$base}/static/js/lib/jquery-3.2.1.min.js"><xsl:comment>keep alive</xsl:comment></script>
                    <script type="text/javascript" src="{$base}/static/js/lib/jquery-3.2.1.min.js"><xsl:comment>keep alive</xsl:comment></script>
                    <script type="text/javascript" src="{$base}/static/js/lib/jquery-ui/jquery-ui.js"><xsl:comment>keep alive</xsl:comment></script>
                    <script type="text/javascript" src="{$base}/static/js/lib/jquery-ui/jquery-ui.js"><xsl:comment>keep alive</xsl:comment></script>
                    <script type="text/javascript" src="{$base}/static/js/lib/datatable.min.js"><xsl:comment>keep alive</xsl:comment></script>
                    
                    
                </head>
                <body>
                    <div class="summary">
                        <h2>Number of versions for record: {$recordnumber}</h2>
                        <p>
                            <strong>Total versions: </strong>
                            {count(/fn:map/fn:array[@key='history']/fn:map)} </p>
                    </div>
                    <table class="table table-bordered resultTable">
                        <thead>
                            <tr><th>epoch</th><th>dateTime</th><th>user</th><th>detail</th></tr>
                        </thead>
                        <tbody>
                            <xsl:apply-templates select="fn:map/fn:array/fn:map"/>
                        </tbody>    
                            
                    </table>
                </body>
            </html>
            <script xsl:expand-text="yes">
                var datatable = new DataTable(document.querySelector('#records-{local-name()}'), {{
                pageSize: 25,
                sort: [{string-join(list/(* except ns)/sort,', ')}, true],
                filters: [{string-join(list/(* except ns)/filter,', ')}, 'select'],
                filterText: 'Type to filter... ',
                pagingDivSelector: "#paging-records-{local-name()}"}}
                );
            </script>
        </xsl:for-each>
        <script type="text/javascript" src="{$base}/static/js/src/sorttable.js"/>

    </xsl:template>
    
    
    <xsl:template match="fn:map">
        <xsl:variable name="tijd" select="fn:string[@key = 'timestamp']"/>
        <xsl:variable name="user" select="fn:string[@key = 'user']"/>        
        <xsl:variable name="formattedTijd" select="format-dateTime(xs:dateTime(translate($tijd, ' ', 'T')), 
                '[Y0001]-[M01]-[D01] [H01]:[m01]')"/>   
        <xsl:variable name="epoch" select="fn:number[@key = 'epoch']"/>
        <tr>
            <td>{$epoch}</td>
            <td>
                {$formattedTijd} 
            </td>
            <td>
                {$user}
            </td>    
            <td>
                <a href="history/{$epoch}">LINK</a>
            </td>
        </tr>
    </xsl:template>
    
    
</xsl:stylesheet>
