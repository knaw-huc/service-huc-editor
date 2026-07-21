<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:err="http://www.w3.org/2005/xqt-errors" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:math="http://www.w3.org/2005/xpath-functions/math" xmlns:clariah="http://www.clariah.eu/" xmlns:cmd="http://www.clarin.eu/cmd/" exclude-result-prefixes="xs math" version="3.0">

    <xsl:output method="html"/>

    <xsl:param name="cwd" select="'file:/Users/menzowi/Documents/Projects/huc-cmdi-editor/service/'"/>
    <xsl:param name="base" select="'http://localhost:1210'"/>
    <xsl:param name="app" select="'adoptie'"/>
    <xsl:param name="config" select="doc(concat($cwd, '/data/apps/', $app, '/config.xml'))"/>

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
                <xsl:if test="normalize-space($config/config/app/js/script)!=''">
                    <script type="text/javascript" src="{$base}/app/{$app}/static/js/{$config/config/app/js/script}"/>           
                </xsl:if>
                <script>

                    async function setUser() {{
                        const writePermissions = "{$config/config/app/access/write}"
                        const baseUrlApp = "{concat($base, '/app/', $app)}";
                        const response = await fetch(baseUrlApp + "/auth/me")
                        const userData = await response.json()
                        const userDiv = document.getElementById("user")
                        userDiv.setHTML(userData.name)

                        if ((writePermissions == "users" || writePermissions == "owner") &amp;&amp; userData.name == "anonymous") {{
                            const buttons = document.getElementsByClassName("addButton")
                            for (const button of buttons) {{
                                button.removeAttribute("href")
                                button.setAttribute("disabled", true)
                                button.setHTML("&#160;")
                            }}
                        }}
                    }}

                    $('document').ready(function(){{
                        ccfInit('list');
                        setUser()
                    }});

                    function ccfInit(page) {{
                    <xsl:if test="normalize-space($config/config/app/js/init)!=''">
                        <xsl:text expand-text="yes">{normalize-space($config/config/app/js/init)};</xsl:text>
                    </xsl:if>
                    }}

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
                <iframe src="{$base}/static/status.html" style="border:none;height:3em;width:100%;"/>
                <div id="wrapper">
                    <div id="header">{$config/config/app/title}</div>
                    <div id="user"></div>
                    <div id="homeBtn"/>
                    <div class="action_menu">
                        <xsl:for-each select="$config/config/app/hooks/action/*[tokenize(level)='app']">
                            <xsl:if test="position()=1">
                                <xsl:text>[ </xsl:text>
                            </xsl:if>
                            <xsl:variable name="action" select="."/>
                            <xsl:comment expand-text="yes">
                                action: {local-name($action)}
                                endpoint: {endpoint}
                            </xsl:comment>
                            <a xsl:expand-text="yes" class="app action {local-name($action)}" id="action_{local-name($action)}" target="action_{local-name($action)}">
                                <xsl:choose>
                                    <xsl:when test="starts-with(endpoint,'javascript:')">
                                        <xsl:attribute name="onclick" select="endpoint"/>
                                    </xsl:when>
                                    <xsl:otherwise>
                                        <xsl:attribute name="href" select="concat($base,'/app/',$app,'/action/',(normalize-space(endpoint),local-name($action))[1])"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                                <xsl:value-of select="$action/label"/>
                            </a>
                            <xsl:choose>
                                <xsl:when test="position() = last()">
                                    <xsl:text> ]</xsl:text>
                                </xsl:when>
                                <xsl:otherwise>
                                    <xsl:text> | </xsl:text>
                                </xsl:otherwise>
                            </xsl:choose>
                        </xsl:for-each>
                    </div>
                    
                    <div id="content">
                        <xsl:for-each select="$config/config/app/prof/*">
                            <xsl:variable name="p" select="."/>
                            <xsl:variable name="prof" select="prof"/>
                            <xsl:variable name="hooks" select="hooks"/>
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
                            <xsl:variable name="NS" as="element()">
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
                            <div class="action_menu">
                                <xsl:for-each select="$config/config/app/hooks/action/*">
                                    <xsl:variable name="action" select="."/>
                                    <xsl:comment expand-text="yes">
                                        action: {local-name($action)}
                                        level: {level} [{normalize-space(level) => tokenize()=('','prof')}]
                                        profile: {prof} [={$prof}? { normalize-space(prof)=('',$prof)}]
                                        endpoint: {endpoint}
                                    </xsl:comment>
                                    <xsl:if test="normalize-space(level)=>tokenize()=('','prof') and normalize-space(prof)=('',$prof)">
                                        <xsl:if test="position()=1">
                                            <xsl:text>[ </xsl:text>
                                        </xsl:if>
                                        <a xsl:expand-text="yes" class="prof action {local-name($action)}" id="action_{local-name($action)}" target="action_{local-name($action)}">
                                            <xsl:choose>
                                                <xsl:when test="starts-with(endpoint,'javascript:')">
                                                    <xsl:attribute name="onclick" select="endpoint"/>
                                                </xsl:when>
                                                <xsl:otherwise>
                                                    <xsl:attribute name="href" select="concat($base,'/app/',$app,'/profile/',$prof,'/action/',(normalize-space(endpoint),local-name($action))[1])"/>
                                                </xsl:otherwise>
                                            </xsl:choose>
                                            <xsl:value-of select="$action/label"/>
                                        </a>
                                        <xsl:choose>
                                            <xsl:when test="position() = last()">
                                                <xsl:text> ]</xsl:text>
                                            </xsl:when>
                                            <xsl:otherwise>
                                                <xsl:text> | </xsl:text>
                                            </xsl:otherwise>
                                        </xsl:choose>
                                    </xsl:if>
                                </xsl:for-each>
                            </div>
                            <table id="records-{local-name()}" class="table table-bordered resultTable">
                                <thead>
                                    <tr>
                                        <xsl:for-each select="list/(* except ns)">
                                            <th data-sort="{local-name()}">{(label,label_en,local-name())[1]}</th>
                                        </xsl:for-each>
                                        <th data-sort="creationDate">Creation date</th>
                                        <th>
                                            <a class="addButton" href="{concat($base, '/app/', $app, '/profile/', $prof, '/record/editor')}" id="addRec">
                                                <img src="{$base}/static/img/add.ico" height="16px" width="16px"/>
                                            </a>
                                        </th>
                                        <th/>
                                        <th/>
                                        <th/>
                                        <th/>
                                        <th/>
                                        <xsl:for-each select="$config/config/app/hooks/action/*[tokenize(level)='rec'][normalize-space(prof)=('',$prof)]">
                                            <th/>
                                        </xsl:for-each>
                                    </tr>
                                </thead>
                                <tbody>
                                </tbody>
                            </table>
                            <div id="paging-records-{local-name()}"/>
                            <br/>
                            <script xsl:expand-text="yes">

                                (async () => {{
                                    const baseUrl = "{concat($base, '/app/', $app, '/profile/', $prof)}";
                                    const response = await fetch(baseUrl + "/records?limit=10000");
                                    const data = await response.json();
                                    const header = data.header;
                                    const actions = data.actions;

                                    let filterOptions = {{}}

                                    for (prop of header) {{
                                        if (prop.filter) {{
                                            filterOptions[prop.prop] = prop.filter
                                        }} else {{
                                            filterOptions[prop.prop] = false
                                        }}
                                    }}

                                    filterOptions["creationDate"] = "select"

                                    var datatable = new DataTable(document.querySelector('#records-{local-name()}'), {{
                                        pageSize: 25,
                                        sort: [{string-join(list/(* except ns)/sort,', ')}, true],
<!--                                        filters: [{string-join(list/(* except ns)/filter,', ')}, 'select'],-->
                                        filters: filterOptions,
                                        filterText: 'Type to filter... ',
                                        data: data.data,
                                        lineFormat: function (id, data) {{
                                            var res = document.createElement("tr");
                                            // Custom properties
                                            for (var item of header) {{
                                                const cell = document.createElement("td")
                                                const value = document.createTextNode(data[item.prop])
                                                cell.appendChild(value)
                                                res.appendChild(cell)
                                            }}
                                            // Default props: creation date
                                            var creationDate = document.createElement("td")
                                            creationDate.appendChild(document.createTextNode(data.creationDate))
                                            res.appendChild(creationDate)

                                            const editCell = document.createElement("td")
                                            const deleteCell = document.createElement("td")
                                            // Edit button
                                            if (data.write) {{
                                                const editButton = document.createElement("a")
                                                editButton.setAttribute("href", baseUrl + "/record/" + data._id + "/editor")
                                                editButton.setAttribute("title", "Edit record")
                                                const editImg = document.createElement("img")
                                                editImg.setAttribute("src", "{$base}/static/img/edit.png")
                                                editImg.setAttribute("width", "16px")
                                                editImg.setAttribute("height", "16px")
                                                editButton.appendChild(editImg)
                                                editCell.appendChild(editButton)

                                                // Delete button
                                                const deleteButton = document.createElement("a")
                                                deleteButton.setAttribute("class", "myBtn delete")
                                                deleteButton.setAttribute("onclick", "deleteRecord('" + baseUrl + "/record/" + data._id +"')")
                                                const deleteImg = document.createElement("img")
                                                deleteImg.setAttribute("src", "{$base}/static/img/bin.png")
                                                deleteImg.setAttribute("width", "16px")
                                                deleteImg.setAttribute("height", "16px")
                                                deleteButton.appendChild(deleteImg)
                                                deleteCell.appendChild(deleteButton)
                                            }} else {{
                                                // Add empty cells
                                                editCell.appendChild(document.createTextNode("&#160;"))
                                                deleteCell.appendChild(document.createTextNode("&#160;"))
                                            }}
                                            res.appendChild(editCell)
                                            res.appendChild(deleteCell)


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
                                            const historyCell = document.createElement("td")
                                            if (data.read) {{
                                                // History button
                                                const historyButton = document.createElement("a")
                                                historyButton.setAttribute("href", baseUrl + "/record/" + data._id + "/history")
                                                historyButton.setAttribute("class", "byBtn history")
                                                historyButton.setAttribute("target", "_blank")
                                                const historyImg = document.createElement("img")
                                                historyImg.setAttribute("src", "{$base}/static/img/history.png")
                                                historyImg.setAttribute("width", "16px")
                                                historyImg.setAttribute("height", "16px")
                                                historyButton.appendChild(historyImg)
                                                historyCell.appendChild(historyButton)
                                                res.appendChild(historyCell)

                                                // Exports
                                                for (exp of exports) {{
                                                    const cell = document.createElement("td")
                                                    const link = document.createElement("a")
                                                    link.setAttribute("href", baseUrl + "/record/" + data._id + "." + exp.format)
                                                    link.setAttribute("title", "Show " + exp.name)
                                                    link.setAttribute("target", "_blank")
                                                    link.appendChild(document.createTextNode(exp.name))
                                                    cell.appendChild(link)
                                                    res.appendChild(cell)
                                                }}
                                            }} else {{
                                                historyCell.appendChild(document.createTextNode("&#160;"))
                                                res.appendChild(historyCell)
                                            }}

                                            // Actions
                                            for (action in actions) {{
                                                const details = actions[action]

                                                const cell = document.createElement("td")
                                                const link = document.createElement("a")

                                                if (data.actionsEnabled[action]) {{
                                                    if (details.endpoint.startsWith("javascript:")) {{
                                                        link.setAttribute("onclick", details.endpoint)
                                                    }} else {{
                                                        link.setAttribute("href", baseUrl + "/record/" + data._id + "/action/" + details.endpoint)
                                                    }}
                                                    link.setAttribute("class", "rec action")
                                                }} else {{
                                                    link.setAttribute("class", "rec action disabled")
                                                }}

                                                link.setAttribute("title", "Action " + details.label)
                                                link.appendChild(document.createTextNode(details.label))
                                                cell.appendChild(link)
                                                res.appendChild(cell)
                                            }}

                                            return res;
                                        }},
                                        pagingDivSelector: "#paging-records-{local-name()}"}}
                                    );
                                }})()
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
