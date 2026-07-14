<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                xmlns:xs="http://www.w3.org/2001/XMLSchema"
                xmlns:math="http://www.w3.org/2005/xpath-functions/math"
                xmlns:fn="http://www.w3.org/2005/xpath-functions" 
                exclude-result-prefixes="xs math fn"
                expand-text="yes" version="3.0">
    
    
    <xsl:output method="html"/>
    
    <xsl:param name="base" select="'http://localhost:1210'"/>

    <xsl:param name="cwd" select="'file:/Users/menzowi/Documents/Projects/huc-cmdi-editor/service/'"/>
    <xsl:param name="app" select="'blabla'"/>
    <xsl:param name="prof" select="'blabla'"/>
    <xsl:param name="config" select="doc(concat($cwd, '/data/apps/', $app, '/config.xml'))"/>
    <xsl:param name="user" select="'anonymous'"/>
    <xsl:param name="nr" />

    <xsl:template name="main">
            <html xsl:expand-text="yes">
                <head>                
                    <title>history for record [{$nr}] </title>
                    <link rel="stylesheet" href="{$base}/static/css/style.css" type="text/css"/>
                    <link rel="stylesheet" href="{$base}/static/css/datatable.min.css" type="text/css"/>
                    <link rel="stylesheet" href="{$base}/static/js/lib/jquery-ui/jquery-ui.css"/>
                    <script type="text/javascript" src="{$base}/static/js/lib/jquery-3.2.1.min.js"><xsl:comment>keep alive</xsl:comment></script>
                    <script type="text/javascript" src="{$base}/static/js/lib/jquery-ui/jquery-ui.js"><xsl:comment>keep alive</xsl:comment></script>
                    <script type="text/javascript" src="{$base}/static/js/lib/datatable.min.js"><xsl:comment>keep alive</xsl:comment></script>
                    
                    
                </head>
                <body>
                    <div id="wrapper">
                        <div id="header">{$config/config/app/title}</div>
                        <div id="user"/>
                        <div id="homeBtn" titel="back" onclick="window.history.back()" onkeydown="if(event.key==='Enter'||event.key===' '){{event.preventDefault(); window.history.back();}}" role="button" tabindex="0" />
                        
                        <div id="content">
                            <div class="summary">
                                <h2>Previous versions for record: {$nr}</h2>
                                <p>
                                    <strong>Total versions: </strong>
                                    <span id="versionCount" />
                                </p>
                            </div>
                            <table id="records-{$nr}" class="table table-bordered resultTable">
                                <thead>                          
                                    <tr>
                                        <th data-sort="epoch">epoch</th>
                                        <th data-sort="timestamp">dateTime</th>
                                        <th data-sort="user">user</th>
                                        <th />
                                        <th />
                                        <th />
                                    </tr>
                                </thead>
                                <tbody>
                                </tbody>

                            </table>
                            <div id="paging-records"/>
                        </div>
                    </div>
                    <script xsl:expand-text="yes">
                        (async () => {{
                            const recordNumber = {$nr}
                            const url = "{concat($base, '/app/', $app, '/profile/', $prof, '/record/')}"

                            const result = await fetch(url + recordNumber + "/history")
                            const data = await result.json()
                            console.log(data)
                            document.getElementById("versionCount").setHTML(data.history.length)


                            const datatable = new DataTable(document.querySelector('#records-{$nr}'), {{
                                pageSize: 25,
                                sort: [true, true, true, false,false,false],
                                filters: {{
                                    epoch: false,
                                    dateTime: true,
                                    user: "select"
                                }},
                                data: data.history,
                                lineFormat: function (id, data) {{
                                    var res = document.createElement("tr");
                                    // Custom properties
                                    // Default props: epoch, dateTime, user
                                    for (const prop of ["epoch", "timestamp", "user"]) {{
                                        const cell = document.createElement("td")
                                        cell.appendChild(document.createTextNode(data[prop]))
                                        res.appendChild(cell)
                                    }}

                                    const exports = [
                                        {{
                                            name: "CMDI",
                                            format: "xml"
                                        }},
                                        {{
                                            name: "HTML",
                                            format: "html"
                                        }},
                                        {{
                                            name: "PDF",
                                            format: "pdf"
                                        }},
                                    ]

                                    // Exports
                                    for (exp of exports) {{
                                        const cell = document.createElement("td")
                                        const link = document.createElement("a")
                                        link.setAttribute("href", url + recordNumber + "/history/" + data.epoch + "." + exp.format)
                                        link.setAttribute("title", "Show " + exp.name)
                                        link.setAttribute("target", "_blank")
                                        link.appendChild(document.createTextNode(exp.name))
                                        cell.appendChild(link)
                                        res.appendChild(cell)
                                    }}

                                    return res;
                                }},
                                filterText: 'Type to filter... ',
                                pagingDivSelector: "#paging-records"
                            }});
                        }})()
                    </script>
                    <script type="text/javascript" src="{$base}/static/js/src/sorttable.js"/>
                </body>
            </html>
    </xsl:template>
</xsl:stylesheet>
