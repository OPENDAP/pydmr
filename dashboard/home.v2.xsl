<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0">
    <xsl:template match="Environment">
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
                    padding-left: 5px;
                    padding-right: 5px;
                    }
                </style>
            </head>
            <body>
                <h1>OPeNDAP Tested Providers for <xsl:value-of select="@name"/></h1>
                <xsl:value-of select="@date"/>
                <table>
                    <tr bgcolor="#9acd32">
                        <th colspan="5">Providers</th>
                    </tr>
                    <xsl:apply-templates/>
                </table>
            </body>
        </html>
    </xsl:template>

    <xsl:template match="Provider">
        <tr>
            <td colspan="2"><xsl:value-of select="@name"/></td>
            <td colspan="3">
                Collections: <xsl:value-of select="@run"/>
                / <xsl:value-of select="@total"/>
                in <xsl:value-of select="@time"/>s
            </td>
        </tr>
        <xsl:apply-templates/>
        <tr bgcolor="#9acd32"><td colspan="5"/></tr>
    </xsl:template>

    <xsl:template match="Error">
        <tr>
            <td>-</td>
            <td><a href="{@url}">Errors</a></td>
            <td>Total: <xsl:value-of select="@total"/></td>
            <td>Error: <xsl:value-of select="@error"/></td>
            <td>Info: <xsl:value-of select="@info"/></td>
        </tr>
    </xsl:template>

    <xsl:template match="Test">
        <tr>
            <td>-</td>
            <td><a href="{@url}"><xsl:value-of select="@name"/></a></td>
            <td>Total: <xsl:value-of select="@total"/></td>
            <td>Pass: <xsl:value-of select="@pass"/></td>
            <td>Fail: <xsl:value-of select="@fail"/></td>
        </tr>
    </xsl:template>

</xsl:stylesheet>
