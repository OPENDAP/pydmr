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
                        <th>Providers</th>
		    </tr>
                    <xsl:apply-templates/>
                </table>
            </body>
        </html>
    </xsl:template>
    
    <xsl:template match="Provider">
        <tr>
            <td><a href="{@name}.xml"><xsl:value-of select="@name"/></a></td>
        </tr>
        <xsl:apply-templates/>     
    </xsl:template>
    
</xsl:stylesheet>
