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
                <title>Login [{$app}] </title>
                <link rel="stylesheet" href="{$base}/static/css/style.css" type="text/css"/>
<!--                <link rel="stylesheet" href="{$base}/static/css/datatable.min.css" type="text/css"/>-->
<!--                <script type="text/javascript" src="{$base}/static/js/lib/datatable.min.js"><xsl:comment>keep alive</xsl:comment></script>-->

            </head>
            <body>
                <main id="wrapper">
                    <form class="login-form" onsubmit="return login(event, '{$app}')">
                        <h2>Log in</h2>
                        <p id="login_message"></p>
                        <div class="form-group">
                            <label for="username">Username</label>
                            <input id="username" class="form-input" type="text" name="username" />
                        </div>
                        <div class="form-group">
                            <label for="password">Password</label>
                            <input id="password" class="form-input" type="password" name="password" />
                        </div>
                        <div id="response"></div>
                        <button type="submit">Log in</button>
                    </form>
                </main>
                <script src="{$base}/static/js/auth.js"></script>
                <script>
                    const loginMessage = localStorage.getItem("login_message_{$app}")
                    if (loginMessage) {{
                        document.getElementById("login_message").setHTML(loginMessage)
                    }}
                </script>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>
