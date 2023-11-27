#!/bin/sh

url_file=/home/slloyd/git/pydmr/Exports/11.27.23_dmrpp_urls.txt
output_file=/home/slloyd/git/pydmr/Exports/grep_output.txt

echo "Starting ..."
while read line; do
    dmrpp_url="$line.dmrpp"
    echo "$dmrpp_url: "
    if curl -n -c "$HOME/.edl_cookies" -b "$HOME/.edl_cookies" -L "$dmrpp_url" | grep -n "unsupp" >> $output_file
    then
        echo "$dmrpp_url

        " >> $output_file
    fi
    echo " "
done < "$url_file"
echo " ... Done"