<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:math="http://www.w3.org/2005/xpath-functions/math" xmlns:clariah="http://www.clariah.eu/" xmlns:cmd="http://www.clarin.eu/cmd/" exclude-result-prefixes="xs math" version="3.0">

    <xsl:output method="html"/>

    <xsl:param name="cwd" select="'file:/Users/menzowi/Documents/Projects/huc-cmdi-editor/service/'"/>
    <xsl:param name="base" select="'http://localhost:1210'"/>
    <xsl:param name="app" select="'adoptie'"/>
    <xsl:param name="config" select="doc(concat($cwd, '/data/apps/', $app, '/config.xml'))"/>
    <xsl:param name="user" select="'anonymous'"/>
    
    <xsl:template name="main">
        <html lang="en" xsl:expand-text="yes">
            <head>
                <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
                <title>{$config/config/app/title}</title>
                <link rel="stylesheet" href="{$base}/static/css/style.css" type="text/css"/>
                <link rel="stylesheet" href="{$base}/static/css/datatable.min.css" type="text/css"/>
                <link rel="stylesheet" href="{$base}/static/js/lib/jquery-ui/jquery-ui.css"/>
                <script type="text/javascript" src="{$base}/static/js/lib/jquery-3.2.1.min.js"><xsl:comment>keep alive</xsl:comment></script>
                <script type="text/javascript" src="{$base}/static/js/lib/jquery-3.2.1.min.js"><xsl:comment>keep alive</xsl:comment></script>
                <script type="text/javascript" src="{$base}/static/js/lib/jquery-ui/jquery-ui.js"><xsl:comment>keep alive</xsl:comment></script>
                <script type="text/javascript" src="{$base}/static/js/lib/jquery-ui/jquery-ui.js"><xsl:comment>keep alive</xsl:comment></script>
                <script type="text/javascript" src="{$base}/static/js/lib/datatable.min.js"><xsl:comment>keep alive</xsl:comment></script>
                <script>
                        //$('document').ready(function(){{
                        //    setEvents();
                        //}});
                        
                        function deleteRecord(rec) {{
                            var answer = confirm('Dit record wordt verwijderd! This record will be removed! OK?');
                            if (answer){{
                                console.log("delete record["+rec+"]");
                                $.ajax(
                                    {{
                                        type: "DELETE",
                                        url: rec,
                                        dataType: "json",
                                        success: function (json) {{
                                            obj = json;
                                            console.log(obj);
                                            location.reload();
                                        }},
                                        error: function (err) {{
                                            obj = {{"error": err}};
                                            console.log(obj);
                                        }}
                                    }}
                                );
                            }}
                        }}                                                    
                 </script>
            </head>
            <body>
                <div id="wrapper">
                    <div id="header">{$config/config/app/title}</div>
                    <div id="user"/>
                    <div id="homeBtn"/>
                    <div id="content">
                        <xsl:for-each select="$config/config/app/prof/*">
                            <xsl:variable name="p" select="."/>
                            <xsl:variable name="prof" select="prof"/>
                            <xsl:variable name="recs" select="concat($cwd, '/data/apps/', $app, '/profiles/', $prof, '/records')"/>
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
                            <xsl:comment expand-text="yes">
                                # cmdi version[{$config//app/cmdi_version}]
                                # cmd ns [{$cmd-ns}]
                                # cmdp ns [{$cmdp-ns}]
                                <xsl:copy-of select="$NS"/>
                            </xsl:comment>
                            <h2 xsl:expand-text="yes">list of {(./label_en,local-name())[1]} records</h2>
                            <table id="records-{local-name()}" class="table table-bordered resultTable">
                                <thead>
                                    <tr>
                                        <xsl:for-each select="list/(* except ns)">
                                            <th>{(label,label_en,local-name())[1]}</th>
                                        </xsl:for-each>
                                        <th>Creation date</th>
                                        <th>
                                            <xsl:choose>
                                                <xsl:when test="$config/config/app/access/write='owner' and $user='anonymous'">
                                                    <xsl:text>&#160;</xsl:text>
                                                </xsl:when>
                                                <xsl:when test="$config/config/app/access/write='user' and $user='anonymous'">
                                                    <xsl:text>&#160;</xsl:text>
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <a href="{concat($base, '/app/', $app, '/profile/', $prof, '/record/editor')}" id="addRec">
                                                        <img src="{$base}/static/img/add.ico" height="16px" width="16px"/>
                                                    </a>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                        </th>
                                        <th/>
                                        <!--<th/>-->
                                        <th/>
                                        <th/>
                                        <th/>
                                    </tr>
                                </thead>
                                <tbody>
                                    <xsl:for-each select="collection(concat($recs,'?match=record-\d+\.xml&amp;on-error=warning'))">
                                        <xsl:sort select="replace(base-uri(.), '.*/record-(\d+)\.xml', '$1')" data-type="number"/>
                                        <xsl:variable name="rec" select="."/>
                                        <xsl:variable name="nr" select="replace(base-uri($rec), '.*/record-(\d+)\.xml', '$1')"/>
                                        <xsl:variable name="url" select="concat($base, '/app/', $app, '/profile/', $prof, '/record/', $nr)"/>
                                        <xsl:variable name="owner" select="string((/*:CMD/*:Header/*:MdCreator,'server')[1])"/>
                                        <xsl:comment>r[{$config/config/app/access/read}]w[{$config/config/app/access/write}][{$user}][{base-uri($rec)}][{$url}][{$owner}]</xsl:comment>
    
                                        <xsl:if test="$config/config/app/access/read!='owner' or $config/config/app/access/write!='owner' or $owner=$user">
                                            <tr>
                                                <xsl:for-each select="$p/list/(* except ns)">
                                                    <td>
                                                        <xsl:variable name="xpath" select="xpath"/>
                                                        <xsl:evaluate xpath="$xpath" context-item="$rec" namespace-context="$NS"/>
                                                    </td>
                                                </xsl:for-each>
                                                <td>{/cmd:CMD/cmd:Header/cmd:MdCreationDate}</td>
                                                <td>
                                                    <xsl:choose>
                                                        <xsl:when test="$config/config/app/access/write='owner' and $user!=$owner">
                                                            <xsl:text>&#160;</xsl:text>
                                                        </xsl:when>
                                                        <xsl:when test="$config/config/app/access/write='user' and $user='anonymous'">
                                                            <xsl:text>&#160;</xsl:text>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                            <a href="{$url}/editor" title="Edit metadata">
                                                                <img src="{$base}/static/img/edit.png" height="16px" width="16px"/>
                                                            </a>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                                <!--<td>
                                                <a href="dwnldRec('{$nr}')" title="Download">
                                                    <img src="{$base}/static/img/download.png" height="16px" width="16px"/>
                                                </a>
                                            </td>-->
                                                <td>
                                                    <xsl:choose>
                                                        <xsl:when test="$config/config/app/access/write='owner' and $user!=$owner">
                                                            <xsl:text>&#160;</xsl:text>
                                                        </xsl:when>
                                                        <xsl:when test="$config/config/app/access/write='user' and $user='anonymous'">
                                                            <xsl:text>&#160;</xsl:text>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                            <a title="Delete" class="myBtn delete" id="myBtn1" onclick="deleteRecord('{$url}');">
                                                                <img src="{$base}/static/img/bin.png" height="16px" width="16px"/>
                                                            </a>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                                <td>
                                                    <xsl:choose>
                                                        <xsl:when test="$config/config/app/access/read='owner' and $user!=$owner">
                                                            <xsl:text>&#160;</xsl:text>
                                                        </xsl:when>
                                                        <xsl:when test="$config/config/app/access/read='user' and $user='anonymous'">
                                                            <xsl:text>&#160;</xsl:text>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                            <a href="{$url}.xml" title="Show CMDI" target="_blank">CMDI</a>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                                <td>
                                                    <xsl:choose>
                                                        <xsl:when test="$config/config/app/access/read='owner' and $user!=$owner">
                                                            <xsl:text>&#160;</xsl:text>
                                                        </xsl:when>
                                                        <xsl:when test="$config/config/app/access/read='user' and $user='anonymous'">
                                                            <xsl:text>&#160;</xsl:text>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                            <a href="{$url}.html" title="Show HTML" target="_blank">HTML</a>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                                <td>
                                                    <xsl:choose>
                                                        <xsl:when test="$config/config/app/access/read='owner' and $user!=$owner">
                                                            <xsl:text>&#160;</xsl:text>
                                                        </xsl:when>
                                                        <xsl:when test="$config/config/app/access/read='user' and $user='anonymous'">
                                                            <xsl:text>&#160;</xsl:text>
                                                        </xsl:when>
                                                        <xsl:otherwise>
                                                            <a href="{$url}.pdf" title="Show PDF" target="_blank">PDF</a>
                                                        </xsl:otherwise>
                                                    </xsl:choose>
                                                </td>
                                            </tr>
                                        </xsl:if>    
                                    </xsl:for-each>
                                </tbody>
                            </table>
                            <div id="paging-records-{local-name()}"/>
                            <br/>
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
                    </div>
                </div>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="/">
        <xsl:call-template name="main"/>
    </xsl:template>

</xsl:stylesheet>
