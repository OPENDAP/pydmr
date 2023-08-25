import configparser
import os
import regex as re
import shutil

src_dir = ''
dst_dir = ''
log_dir = ''
recent = ''
month = ''


home_html_template_begin = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">

<html lang="en">
<head>
<title>NGAP PROD environment test results by month</title>
</head>

<body>
<h1>NGAP PROD environment test results by month</h1>
<p>Test Results:</p>
<ul>

"""


html_template_end = """</ul>

</body>
</html>
"""


month_html_template_begin = """<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
"http://www.w3.org/TR/html4/strict.dtd">

<html lang="en">
<head>
<title>NGAP PROD environment test results by date</title>
</head>

<body>
<h1>NGAP PROD environment test results by date</h1>
<p>Dates:</p>
<ul>

"""


def make_html_li(path, name):
    # <li><a href=07.28.23/PROD-07.28.2023-1.xml>Most recent</a></li>
    # <li><a href="11.30.2022/PROD-11.30.2022-1.xml">11.30.2022-1</a></li>
    element = "<li><a href="+path+">"+name+"</a></li>\n"
    return element


def load_config():
    parser = configparser.RawConfigParser()
    config_filepath = r'config.txt'
    parser.read(config_filepath)

    global src_dir
    src_dir = parser.get("urls", "src_dir")
    print("source dir: " + src_dir)

    global dst_dir
    dst_dir = parser.get("urls", "dst_dir")
    print("dest dir: " + dst_dir)

    global log_dir
    log_dir = parser.get("urls", "log_dir")
    print("log dir: " + log_dir)


def scan_dir(dir_path, pattern, file=False):
    dir_list = []
    # print("path: "+dir_path)
    for path in os.listdir(dir_path):
        # check if current path is dir
        # print("path: " + path)
        if not file:
            if os.path.isdir(os.path.join(dir_path, path)):
                if re.match(pattern, path):
                    # print("match found: " + path)
                    dir_list.append(path)
        else:
            if os.path.isfile(os.path.join(dir_path, path)):
                if re.match(pattern, path):
                    # print("match found: " + path)
                    dir_list.append(path)
    return dir_list


def move_dir(path):
    match = re.search("(\d{2})\.\d{2}\.(\d{2})", path)
    global dst_dir
    month_dir = ''
    if match:
        mon = match.group(1).strip()
        year = match.group(2).strip()
        date = decode_month(mon) + "_" + year
        global month
        month = date
        month_dir = os.path.join(dst_dir, date)
    #    print("modified dest: " + month_dir)
    dest = shutil.copytree(os.path.join(src_dir, path), os.path.join(month_dir, path))
    # print("Dest: " + dest)
    if os.path.exists(os.path.join(month_dir, path)):
        shutil.rmtree(os.path.join(src_dir, path))
    global recent
    recent = dest


def decode_month(mon):
    name = ""
    match mon:
        case "01":
            name = "January"
        case "02":
            name = "February"
        case "03":
            name = "March"
        case "04":
            name = "April"
        case "05":
            name = "May"
        case "06":
            name = "June"
        case "07":
            name = "July"
        case "08":
            name = "August"
        case "09":
            name = "September"
        case "10":
            name = "October"
        case "11":
            name = "November"
        case "12":
            name = "December"
    return name


def update_html():
    month_dir = os.path.join(dst_dir, month)
    month_list = scan_dir(month_dir, "\d{2}\.\d{2}\.\d{2}")
    month_page = month_html_template_begin
    most_recent = ""
    for m in month_list:
        ppath = scan_dir(os.path.join(month_dir, m), "PROD.*\.xml", True)
        link = os.path.join(m, ppath[0])
        most_recent = os.path.join(month, link)
        month_page += make_html_li(link, m)
    month_page += html_template_end

    with open(os.path.join(month_dir, "month.html"), "w") as f:
        f.write(month_page)
    f.close()

    home_dir = dst_dir
    home_list = scan_dir(home_dir, ".*_\d{2}")
    home_page = home_html_template_begin
    home_page += make_html_li(most_recent, "Most Recent")
    home_page += "<li><a>Months:</a></li>\n"
    for h in home_list:
        link = os.path.join(h, "month.html")
        home_page += make_html_li(link, h)
    home_page += html_template_end

    with open(os.path.join(home_dir, "home.html"), "w") as f:
        f.write(home_page)
    f.close()


def move_logs():
    shutil.copytree(log_dir, os.path.join(recent, "logs"))
    log_list = scan_dir(log_dir, ".*\.fail\.txt", True)
    for path in log_list:
        # print("\tpath: " + path)
        os.remove(os.path.join(log_dir, path))
        # os.remove(path)


def main():
    load_config()
    dir_list = scan_dir(src_dir, "\d{2}\.\d{2}\.\d{2}")
    for path in dir_list:
        move_dir(path)
        update_html()
    move_logs()


if __name__ == "__main__":
    main()
