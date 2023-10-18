import os
import shutil
import subprocess

files_dir = '/home/slloyd/git/pydmr/Imports'
xml_dir = '/home/slloyd/git/pydmr/Exports'
log_dir = '/home/slloyd/git/pydmr/logs'
mover = '/home/slloyd/git/pydmr/file_mover.py'


def scan():
    files = []
    for path in os.listdir(files_dir):
        if os.path.isdir(os.path.join(files_dir, path)):
            files.append(path)
    return files


def move_logs(path):
    src_logs = os.path.join(os.path.join(files_dir, path),"logs")
    if os.path.exists(src_logs):
        for logs in os.listdir(src_logs):
            source = os.path.join(src_logs, logs)
            dest = os.path.join(log_dir, logs)
            if os.path.isfile(source):
                shutil.copy(source, dest)
        shutil.rmtree(src_logs)


def move_xml(path):
    src_xml = os.path.join(files_dir, path)
    dest_xml = os.path.join(xml_dir, path)
    shutil.copytree(src_xml, dest_xml)
    if os.path.exists(dest_xml):
        shutil.rmtree(src_xml)


def call_mover():
    subprocess.run(["python3", mover])


def main():
    dirs = scan()
    for path in dirs:
        print("path: " + path)
        move_logs(path)
        move_xml(path)
        call_mover()
        

if __name__ == "__main__":
    main()
    
        
