<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:math="http://www.w3.org/2005/xpath-functions/math" exclude-result-prefixes="xs math" version="3.0">


    <xsl:output method="html"/>

    <xsl:param name="cwd" select="'file:/Users/menzowi/Documents/Projects/huc-cmdi-editor/service/'"/>
    <xsl:param name="base" select="'http://localhost:1210'"/>
    <xsl:param name="app" select="'adoptie'"/>
    <xsl:param name="nr" select="'1'"/>
    <xsl:param name="config" select="doc(concat($cwd, '/data/apps/', $app, '/config.xml'))"/>
    <xsl:param name="rec" select="concat($base, '/app/', $app, '/record/', $nr)"/>

    <xsl:template name="main">
        <html lang="en" xsl:expand-text="yes">
            <head>
                <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
                <title>{$config/app/title}</title>
                <link rel="stylesheet" href="css/style.css" type="text/css"/>
                <link rel="stylesheet" href="https://cmdicdn.sd.di.huc.knaw.nl/css/ccfstyle.css" type="text/css"/>
                <link rel="stylesheet" href="https://cmdicdn.sd.di.huc.knaw.nl/css/autocomplete.css" type="text/css"/>
                <link rel="stylesheet" href="https://cmdicdn.sd.di.huc.knaw.nl/css/jquery-ui.css" type="text/css"/>
                <script type="text/javascript" src="https://cmdicdn.sd.di.huc.knaw.nl/js/jquery-3.2.1.min.js"><xsl:comment>keep alive</xsl:comment></script>
                <script type="text/javascript" src="https://cmdicdn.sd.di.huc.knaw.nl/js/jquery.autocomplete.js"><xsl:comment>keep alive</xsl:comment></script>
                <script type="text/javascript" src="https://cmdicdn.sd.di.huc.knaw.nl/js/jquery-ui/jquery-ui.js"><xsl:comment>keep alive</xsl:comment></script>
                <script type="text/javascript" src="/js/ccf_config_en.js"><xsl:comment>keep alive</xsl:comment></script>
                <script type="text/javascript" src="/js/ccfparser.js"><xsl:comment>keep alive</xsl:comment></script>

                <script>
                    $('document').ready(
                        function () {{
                            var rec = "{$rec}";
                            $.ajax(
                            {{
                                type: "GET",
                                url: rec,
                                dataType: "json",
                                success: function (json) {{
                                    obj = json;
                                    console.log(obj);
                                    //formBuilder.start(obj);
                                }},
                                error: function (err) {{
                                    obj = {{"error": err}};
                                    console.log(obj);
                                }}
                            }}
                            );
                        }}
                    )
                </script>
            </head>
            <body>
                <div id="wrapper">
                    <div id="header">{$config/app/title}</div>
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
