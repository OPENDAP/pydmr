<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0">
    <xsl:template match="Provider">
        <html>
            <head>
                <style>
                    table, th, td {
                    border: 1px solid black;
                    border-collapse: collapse;
                    }
                    th, td {
                    padding-top: 2px;
                    padding-bottom: 2px;
                    padding-left: 10px;
                    padding-right: 10px;
                    }
                    th, #ccid {
                    text-align: left;
                    }
                    td {
                    text-align: center;
                    }
                    .result-pass {
                    background-color: #ccffcc
                    }
                    .result-fail {
                    background-color: #ffcccc
                    }
                    .result-error {
                    background-color: #ffdab3
                    }
                    .result-timeout {
                    background-color: #ffccbb
                    }
                    .result-info {
                    background-color: #b3daff
                    }
                </style>
            </head>
            <body>
                <h1>OPeNDAP Test Results for <xsl:value-of select="@name"/></h1>
                <xsl:value-of select="@date"/>
                <p>
                    Total: <xsl:value-of select="@total"/><br/>
                    <xsl:choose>
                        <xsl:when test="@err_count">
                            Error: <xsl:value-of select="@err_count"/><br/>
                            Info: <xsl:value-of select="@info_count"/><br/>
                            Timeout: <xsl:value-of select="@time_count"/>
                        </xsl:when>
                        <xsl:otherwise>
                            Pass: <xsl:value-of select="@pass_count"/><br/>
                            Fail: <xsl:value-of select="@fail_count"/>
                        </xsl:otherwise>
                    </xsl:choose>
                </p>
                <table>
                    <tr bgcolor="9acd32">
                        <xsl:choose>
                            <xsl:when test="@err_count">
                                <th>CCID</th>
                                <th>Status : Code</th>
                                <th>Message</th>
                            </xsl:when>
                            <xsl:otherwise>
                                <th>CCID (Request Form Link)</th>
                                <th>GID (Data URL Link)</th>
                                <th>Test Type</th>
                                <th>Status : Code</th>
                            </xsl:otherwise>
                        </xsl:choose>
                    </tr>
                    <xsl:apply-templates/>
                </table>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="Test">
        <tr title="{@title}" class="result-{@status}">
            <td><a href="{@url}"><xsl:value-of select="@ccid"/></a></td>
            <td><a href="{@murl}"><xsl:value-of select="@gid"/></a></td>
            <td><xsl:value-of select="@type"/></td>
            <td><xsl:value-of select="@status"/> : <xsl:value-of select="@code"/></td>
        </tr>
    </xsl:template>

    <xsl:template match="Error">
        <tr title="{@title}" class="result-{@status}">
            <td><xsl:value-of select="@ccid"/></td>
            <td><xsl:value-of select="@type"/> : <xsl:value-of select="@code"/></td>
            <td><xsl:value-of select="@payload"/></td>
        </tr>
    </xsl:template>

    <xsl:template match="Info">
        <tr title="{@title}" class="result-info">
            <td><xsl:value-of select="@ccid"/></td>
            <td><xsl:value-of select="@type"/> : <xsl:value-of select="@code"/></td>
            <td><xsl:value-of select="@payload"/></td>
        </tr>
    </xsl:template>

</xsl:stylesheet>
