#!/bin/bash

export cookies=${cookies:-~/.edl_cookies}
if test -n "${verbose}" ; then echo "cookies: ${cookies}"; fi

export w_opts="-w \n{ \"burl\": {\"status\": %{http_code} \"Connect\": %{time_connect}, \"TTFB\": %{time_starttransfer}, \"TotalTime\": %{time_total} } }\n"
if test -n "${verbose}" ; then echo "w_opts: ${w_opts}"; fi

set -x
curl -n -c "${cookies}" -b "${cookies}" -L $@
