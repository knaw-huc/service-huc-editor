<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:math="http://www.w3.org/2005/xpath-functions/math" xmlns:clariah="http://www.clariah.eu/" xmlns:cmd="http://www.clarin.eu/cmd/" exclude-result-prefixes="xs math" version="3.0">

    <xsl:output method="html"/>

    <xsl:param name="cwd" select="'file:/Users/menzowi/Documents/Projects/huc-cmdi-editor/service/'"/>
    <xsl:param name="base" select="'http://localhost:1210'"/>
    <xsl:param name="app" select="'adoptie'"/>
    <xsl:param name="config" select="doc(concat($cwd,'/data/apps/',$app,'/config.xml'))"/>
    <xsl:param name="recs" select="concat($cwd,'/data/apps/',$app,'/records')"/>
    

    <xsl:template name="main">
        <html lang="en" xsl:expand-text="yes">
            <head>
                <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
                <title>{$config/app/title}</title>
                <link rel="stylesheet" href="{$base}/static/css/style.css" type="text/css"/>
                <link rel="stylesheet" href="{$base}/static/css/datatable.min.css" type="text/css"/>
                <link rel="stylesheet" href="{$base}/static/js/lib/jquery-ui/jquery-ui.css"/>
                <script type="text/javascript" src="{$base}/static/js/lib/jquery-3.2.1.min.js"><xsl:comment>keep alive</xsl:comment></script>
                <script type="text/javascript" src="{$base}/static/js/lib/jquery-3.2.1.min.js"><xsl:comment>keep alive</xsl:comment></script>
                <script type="text/javascript" src="{$base}/static/js/lib/jquery-ui/jquery-ui.js"><xsl:comment>keep alive</xsl:comment></script>
                <script type="text/javascript" src="{$base}/static/js/lib/jquery-ui/jquery-ui.js"><xsl:comment>keep alive</xsl:comment></script>
                <script type="text/javascript" src="{$base}/static/js/lib/datatable.min.js"><xsl:comment>keep alive</xsl:comment></script>
                <script>
                        $('document').ready(function(){{
                        setEvents();}});
                    </script>
            </head>
            <body>
                <div id="wrapper">
                    <div id="header">{$config/app/title}</div>
                    <div id="user"/>
                    <div id="homeBtn"/>
                    <div id="content">
                        <h2>list of records</h2>
                        <table id="resultTable" class="table table-bordered">
                            <thead>
                                <tr>
                                    <xsl:for-each select="$config//app/list/(* except ns)">
                                        <th>{label}</th>
                                    </xsl:for-each>
                                    <th>Creation date</th>
                                    <th>
                                        <a href="addRec('{$config/app/prof}')" id="addRec">
                                            <img src="{$base}/static/img/add.ico" height="16px" width="16px"/>
                                        </a>
                                    </th>
                                    <th/>
                                    <th/>
                                    <th/>
                                    <th/>
                                </tr>
                            </thead>
                            <tbody>
                                <xsl:for-each select="collection(concat($recs,'?match=record-\d+\.xml&amp;on-error=warning'))">
                                    <xsl:sort select="replace(base-uri(.),'.*/record-(\d+)\.xml','$1')" data-type="number"></xsl:sort>
                                    <xsl:variable name="rec" select="."/>
                                    <xsl:variable name="nr" select="replace(base-uri($rec),'.*/record-(\d+)\.xml','$1')"/>
                                    <xsl:comment>{base-uri($rec)}</xsl:comment>
                                    <tr>
                                        <xsl:for-each select="$config//app/list/(* except ns)">
                                            <td>
                                                <xsl:variable name="xpath" select="xpath"/>
                                                <xsl:evaluate xpath="$xpath" context-item="$rec"/>
                                            </td>
                                        </xsl:for-each>
                                        <td>{/cmd:CMD/cmd:Header/cmd:MdCreationDate}</td>
                                        <td>
                                            <a href="editRec('{$nr}')" title="Edit metadata">
                                                <img src="{$base}/static/img/edit.png" height="16px" width="16px"/>
                                            </a>
                                        </td>
                                        <td>
                                            <a href="dwnldRec('{$nr}')" title="Download">
                                                <img src="{$base}/static/img/download.png" height="16px" width="16px"/>
                                            </a>
                                        </td>
                                        <td>
                                            <a href="delRec('{$nr}')" title="Delete" class="myBtn delete" id="myBtn1" onclick="deleteRecord(1, 1);">
                                                <img src="{$base}/static/img/bin.png" height="16px" width="16px"/>
                                            </a>
                                        </td>
                                        <td>
                                            <a href="dwnldRec('{$nr}','cmdi')" title="Show CMDI">CMDI</a>
                                        </td>
                                        <td>
                                            <a href="dwnldRec('{$nr}','html')" title="Show HTML" target="_blank">HTML</a>
                                        </td>
                                    </tr>
                                </xsl:for-each>
                            </tbody>
                        </table>
                        <div id="paging-resultTable"/>
                        <script>
                            
                            
                            var datatable = new DataTable(document.querySelector('#resultTable'), {{
                            pageSize: 25,
                            sort: [{string-join($config/app/list/(* except ns)/sort,', ')}, true],
                            filters: [{string-join($config/app/list/(* except ns)/filter,', ')}, 'select'],
                            filterText: 'Type to filter... ',
                            pagingDivSelector: "#paging-resultTable"
                            }});
                        </script>


                        <div id="dialog-confirm" title="Record Deletion Confirmation" style="display: none;">
                            <p><span class="ui-icon ui-icon-alert" style="float:left; margin:12px 12px 20px 0;"/>This record will be permanently deleted and cannot be recovered. Are you sure?</p>
                        </div>


                        <script>
                            
                            $(document).ready(function ()
                            {{
                            $('.delete').click(function () {{
                            var answer = confirm('Dit record wordt verwijderd! This record will be removed! OK?');
                            return answer; // answer is a boolean
                            }});
                            }});
                        </script>


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
