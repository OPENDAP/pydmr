<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0">
  <xsl:template match="Provider">
    <xsl:variable name="collections" select="count(Collection)"/>
    <xsl:variable name="pass_count" select="count(Collection/Test[@result='pass'])"/>
    <xsl:variable name="fail_count" select="count(Collection/Test[@result!='pass'])"/>
    <xsl:variable name="error_count" select="count(Collection/Error)"/>
    <xsl:variable name="info_count" select="count(Collection/Info)"/>
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
                .result-info {
                background-color: #b3daff
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
          Info: <xsl:value-of select="$info_count"/> <br />  
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
            <xsl:variable name="pass_fail" select="@result"/>
            <xsl:variable name="name" select="@name"/>
            <xsl:choose> <!-- unit_tests passed -->
                <xsl:when test="$pass_fail='pass'">
                    <td><xsl:value-of select="concat(@result, ' : ', @status)"/></td>
                </xsl:when>
                <xsl:otherwise> <!-- unit_tests failed, link to fail.txt -->
                    <td><a href="logs/{substring-after(@url,'/granules/')}.{@name}.fail.txt"><xsl:value-of select="concat(@result, ' : ', @status)"/></a></td>
                </xsl:otherwise>
            </xsl:choose>
            <td><xsl:value-of select="@name"/></td>
            <xsl:choose>
                <xsl:when test="$name='dap_vars'">
                    <xsl:variable name="var_url" select="substring-after(@url,'?dap4.ce=/')"/>
                    <td><a href="{@url}"><xsl:value-of select="$var_url"/></a></td>
                </xsl:when>
                <xsl:otherwise>
                    <td><a href="{@url}"><xsl:value-of select="@url"/></a></td>
                </xsl:otherwise>
            </xsl:choose>
        </tr>
    </xsl:template>

    <xsl:template match="Error">
      <tr title="{../@long_name}" class="result-error">
	    <td>Error</td>
	    <td>...</td>
            <td><xsl:value-of select="@message"/></td>
      </tr>
    </xsl:template>

    <!--
    <?xml version="1.0" ?>
    <?xml-stylesheet type='text/xsl' href='/NGAP-PROD-tests/details.xsl'?>
    <Provider name="GES_DISC" date="Wed Jan 25 17:37:58 2023">
    <Collection ccid="C1238517289-GES_DISC" long_name="AIRS/Aqua L3 Daily Standard Physical Retrieval (AIRS-only) 1 degree x 1 degree V006 (AIRS3STD) at GES DISC">
        <Info message="Expected one or more URLs to data in the cloud, but got https://acdisc.gesdisc.eosdis.nasa.gov/opendap/Aqua_AIRS_Level3/AIRS3STD.006/2002/AIRS.2002.08.31.L3.RetStd_IR001.v6.0.9.0.G13214161357.hdf, https://acdisc.gesdisc.eosdis.nasa.gov/opendap/Aqua_AIRS_Level3/AIRS3STD.006/2023/AIRS.2023.01.24.L3.RetStd_IR001.v6.0.33.0.G23025130618.hdf instead"/>
    </Collection>
    -->

    <xsl:template match="Info">
        <tr title="{../@long_name}" class="result-info">
            <td>Info</td>
            <td>...</td>
            <td><xsl:value-of select="@message"/></td>
        </tr>
    </xsl:template>
    
</xsl:stylesheet>
