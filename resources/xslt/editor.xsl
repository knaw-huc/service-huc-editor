<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:math="http://www.w3.org/2005/xpath-functions/math" exclude-result-prefixes="xs math" version="3.0">


    <xsl:output method="html"/>

    <xsl:param name="cwd" select="'file:/Users/menzowi/Documents/Projects/huc-cmdi-editor/service/'"/>
    <xsl:param name="base" select="'http://localhost:1210'"/>
    <xsl:param name="cdn" select="'https://cmdicdn.sd.di.huc.knaw.nl'"/>
    <xsl:param name="app" select="'adoptie'"/>
    <xsl:param name="nr" select="()"/>
    <xsl:param name="config" select="doc(concat($cwd, '/data/apps/', $app, '/config.xml'))"/>
    <xsl:param name="prof" select="$config/config/app/def_prof"/>
    <xsl:param name="prof-url" select="concat($base, '/app/', $app, '/profile/', $prof)"/>
    <xsl:param name="rec-url" select="concat($prof-url, '/record/', $nr)"/>

    <xsl:variable name="epoch" select="floor((current-dateTime() - xs:dateTime('1970-01-01T00:00:00')) div xs:dayTimeDuration('PT1S'))"/>

    <xsl:template name="main">
        <html lang="en" xsl:expand-text="yes">
            <head>
                <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
                <title>{$config/config/app/title}</title>
                <xsl:choose>
                    <xsl:when test="normalize-space($config/config/app/html/style)!=''">
                        <link rel="stylesheet" href="{$base}/app/{$app}/static/css/{$config/config/app/html/style}" type="text/css"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <link rel="stylesheet" href="{$base}/static/css/style.css" type="text/css"/>
                    </xsl:otherwise>
                </xsl:choose>
                
                <link rel="stylesheet" href="{$cdn}/css/ccfstyle.css" type="text/css"/>
                <link rel="stylesheet" href="{$cdn}/css/autocomplete.css" type="text/css"/>
                <link rel="stylesheet" href="{$cdn}/css/jquery-ui.css" type="text/css"/>
                <script type="text/javascript" src="{$cdn}/js/jquery-3.2.1.min.js"><xsl:comment>keep alive</xsl:comment></script>
                <script type="text/javascript" src="{$cdn}/js/jquery.autocomplete.js"><xsl:comment>keep alive</xsl:comment></script>
                <script type="text/javascript" src="{$cdn}/js/jquery-ui/jquery-ui.js"><xsl:comment>keep alive</xsl:comment></script>
                <script type="text/javascript" src="{$base}/static/js/ccf_config_en.js"><xsl:comment>keep alive</xsl:comment></script>
                <script type="text/javascript" src="{$cdn}/js/ccfparser.js"><xsl:comment>keep alive</xsl:comment></script>
                <script type="text/javascript" src="{$cdn}/js/plugins/skos_list/skos_list.js"><xsl:comment>keep alive</xsl:comment></script>
                <link rel="stylesheet" href="{$cdn}/js/plugins/skos_list/skos_list.css" type="text/css"/>                
                <script>
                    <xsl:text>
                        var inRec = null;
                        var outRec = null;
                        
                        function setStatus(status) {{
                            let id = document.evaluate('//select[@data-class="status"]/@id',document,null,XPathResult.STRING_TYPE,null).stringValue;
                            if (id !== undefined &amp;&amp; id !== '')
                                document.getElementById(id).value=status;

                        }}
                        
                        function setLanguages() {{
                            formBuilder.def_language = "{($config/config/app/lang/def[normalize-space(.)!=''],'en')[1]}";
                            let all = ['{string-join($config/config/app/lang/all/*,''',''')}'];
                            if (all[0]!='')
                                formBuilder.languages = all;
                        }}
                        
                        function recBrowser() {{
                            window.location.href = "{concat($base, '/app/', $app,"?refresh=",$epoch)}";
                        }}
                        
                        function submitRec() {{
                            $("#errorSpace").html("");
                            panelError = document.createElement("div");
                            inputOK = true;
                            for (var key in validationProfiles) {{
                                switch (getInputType($("#" + key))) {{
                                    case "input":
                                        validateInput(key);
                                        break;
                                    case "textarea":
                                        validateTextArea(key);
                                        break;
                                    case "select":
                                        validateSelect(key);
                                        break;
                                    default:
                                        alert("Error: unknown input type!");
                                        inputOK = false;
                                        break;
                                }}
                            }}
                            if (inputOK) {{
                                saveRec("submit");
                             }} else {{
                                $("#errorSpace").append(errorSpace);
                             }}
                        }}

                        function saveRec(action) {{
                            if (action==='submit')
                                setStatus('publish');
                            else
                                setStatus('under construction');

                            var rec = [];
                            $(".clonedComponent").each(function () {{
                                $(this).attr("class", "component");
                            }});
                            $(".hidden_element").each(function () {{
                                $(this).removeClass("hidden_element");
                            }});
                            $("#ccform").children().each(function () {{
                                if ($(this).attr("class") === "component") {{
                                    var element = {{}};
                                    element.name = $(this).attr("data-name");
                                    element.type = 'component';
                                    element.sortOrder = 0;
                                    element.content = parseComponent(this);
                                    rec.push(element);
                                }}
                            }});
                            outRec = {{prof: inRec.id, record: rec}};
                            if (inRec.when!==undefined) {{
                                outRec.when = inRec.when;
                                //alert("DBG: outRec.when["+outRec.when+"]");
                            }}
                            console.log(outRec);
                            out = JSON.stringify(outRec);
                            localStorage.setItem("{$rec-url}@{$epoch}.out",out);
                            url="{$rec-url}";
                            if (inRec.nr !==undefined) {{
                                $.ajax(
                                {{
                                    type: "PUT",
                                    url: url,
                                    contentType: 'application/json; charset=utf-8"',
                                    dataType: "json",
                                    processData: false,
                                    data: out,
                                    success: function (msg) {{
                                        //location.reload();
                                        inRec.when = msg.when
                                        //alert("DBG: inRec.when["+inRec.when+"]");
                                        $(errorSpace).append("&lt;p style='color:green'>The record has been saved!&lt;/p>");
                                    }},
                                    error: function (err) {{
                                        alert ("ERR: the "+action+" failed! ["+err.responseJSON.detail+"]");
                                        obj = {{"error": err}};
                                        console.log(obj);
                                        $(errorSpace).append("&lt;p style='color:red'>The record couldn't be saved! ["+err.responseJSON.detail+"]&lt;/p>");
                                    }}
                                }}
                                );
                           }} else {{
                                $.ajax(
                                {{
                                    type: "POST",
                                    url: url,
                                    contentType: 'application/json; charset=utf-8"',
                                    dataType: "json",
                                    processData: false,
                                    data: out,
                                    success: function (msg) {{
                                        console.log(msg);
                                        inRec.when = msg.when
                                        //alert("DBG: inRec.when["+inRec.when+"]");
                                        $(errorSpace).append("&lt;p style='color:green'>The record has been saved!&lt;/p>");
                                        window.location.replace("./"+msg.nr+"/editor");
                                    }},
                                    error: function (err) {{
                                        alert ("ERR: the "+action+" failed! ["+err.responseJSON.detail+"]");
                                        obj = {{"error": err}};
                                        console.log(obj);
                                        $(errorSpace).append("&lt;p style='color:red'>The record couldn't be saved! ["+err.responseJSON.detail+"]&lt;/p>");
                                    }}
                                }}
                                );
                            }}
                        }}

                    </xsl:text>
                    <xsl:choose>
                        <xsl:when test="normalize-space($nr)!=''">
                            <xsl:text>
                                $('document').ready(
                                    function () {{
                                        var url = "{$rec-url}";
                                        $.ajax(
                                            {{
                                                type: "GET",
                                                url: url,
                                                dataType: "json",
                                                success: function (json) {{
                                                    inRec = json;
                                                    console.log(inRec);
                                                    setLanguages();
                                                    formBuilder.start(inRec);
                                                    bind_skos_lists();
                                                }},
                                                error: function (err) {{
                                                    obj = {{"error": err}};
                                                    console.log(obj);
                                                }}
                                            }}
                                        );
                                    }}
                                )
                            </xsl:text>
                        </xsl:when>
                        <xsl:otherwise>
                            <xsl:text>
                                $('document').ready(
                                    function () {{
                                        var url = "{$prof-url}";
                                        $.ajax(
                                        {{
                                            type: "GET",
                                            url: url,
                                            dataType: "json",
                                            success: function (json) {{
                                                prof = json;
                                                inRec = {{id:"{$prof}", content: prof}}
                                                console.log(inRec);
                                                setLanguages();
                                                formBuilder.start(inRec);
                                                bind_skos_lists();
                                            }},
                                            error: function (err) {{
                                                obj = {{"error": err}};
                                                console.log(obj);
                                            }}
                                        }}
                                        );
                                    }}
                                )
                            </xsl:text>
                        </xsl:otherwise>
                    </xsl:choose>
                </script>
            </head>
            <body>
                <iframe src="{$base}/static/status.html" style="border:none;height:3em;width:100%;"/>
                <div id="wrapper">
                    <div id="header">{$config/config/app/title}</div>
                    <div id="user"/>
                    <div id="homeBtn"/>
                    <div id="content">
                        <div id="ccform"/>
                    </div>
                </div>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="/">
        <xsl:call-template name="main"/>
    </xsl:template>

</xsl:stylesheet>
