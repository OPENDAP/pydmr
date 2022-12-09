<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0">
  <xsl:template match="Provider">
    <xsl:variable name="collections" select="count(Collection)"/>
    <xsl:variable name="pass_count" select="count(Collection/Test[@result='pass'])"/>
    <xsl:variable name="fail_count" select="count(Collection/Test[@result!='pass'])"/>
    <xsl:variable name="error_count" select="count(Collection/Error)"/>
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
            </style>
            </head>
            <body>
                <h1>OPeNDAP Test Results for <xsl:value-of select="@name"/></h1>
                <xsl:value-of select="@date"/>
		<p>
		  Tested <xsl:value-of select="$collections"/> Collections <br />
		  Passed: <xsl:value-of select="$pass_count"/> <br />
		  Failed: <xsl:value-of select="$fail_count"/> <br />
		  Errors: <xsl:value-of select="$error_count"/> <br />
		</p>
                <table>
                    <tr bgcolor="#9acd32">
                        <th colspan="3" >Collection ID</th>
                    </tr>
		    <tr bgcolor="9acd32">
		        <th>Result</th>
                        <th>Test</th>
                        <th>URL</th>
		    </tr>
                    <xsl:apply-templates/>
                </table>
            </body>
        </html>
    </xsl:template>
    
    <xsl:template match="Collection">
        <tr title="{@long_name}">
            <td id="ccid" colspan="3" ><xsl:value-of select="@ccid"/></td>
        </tr>
        <xsl:apply-templates/>     
    </xsl:template>
    
    
    <xsl:template match="Test">
        <tr title="{../@long_name}" class="result-{@result}">
            <td><xsl:value-of select="@result"/></td>
            <td><xsl:value-of select="@name"/></td>
            <td><a href="{@url}"><xsl:value-of select="@url"/></a></td>
        </tr>
    </xsl:template>

    <xsl:template match="Error">
      <tr title="{../@long_name}" class="result-error">
	    <td>Error</td>
	    <td>...</td>
            <td><xsl:value-of select="@message"/></td>
      </tr>
    </xsl:template>
    
</xsl:stylesheet>
