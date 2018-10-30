# Get tag messages from git depository.
# How to use ?  Command :python git_tag_msg.py <parameter>.
# Parameter is the name of git depository folder. for example: lz4,log4j,etc. [ note : Do not + '/ '].
from __future__ import print_function
import subprocess
import os
import sys
import re
import csv
import datetime

make_cmd = 'make'
git_cmd = 'git'
cloc_cmd = 'cloc'

def proc(cmd_args, pipe=True, dummy=False):
    if dummy:
        return
    if pipe:
        subproc = subprocess.Popen(cmd_args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
    else:
        subproc = subprocess.Popen(cmd_args)
    return subproc.communicate()

def make(args, pipe=True):
    return proc([make_cmd] + args, pipe)

def git(args, pipe=True):
    return proc([git_cmd] + args, pipe)

def cloc(args, pipe=True):
    return proc([cloc_cmd] + args, pipe)

if __name__ == '__main__':
    start = datetime.datetime.now()

    git_name = sys.argv[1]
    csv_name = git_name
    base_path=os.getcwd()
    git_path=os.getcwd()+'/'+git_name
    if len(sys.argv)>2:
        csv_name=sys.argv[2]
    # Switch path to git_path
    os.chdir(git_path)

    # Get time of all tags and tags_time
    stdout, stderr = git(['log', '--tags','--simplify-by-decoration','--pretty=format:"%ci,%d"'])
    stdout = str(stdout).split('\\n')
    tags =[]
    tags_time = []
    if len(stdout) <= 1:
        stdout = stdout[0].split('\n')
    for st in stdout:
        sn = st.split("tag: ")
        tag_time = sn[0].split(' ')[0]
        tag_time = re.findall(r'\d{4}-\d{2}-\d{2}',tag_time)[0]
        for i in range(len(sn) - 1):
            snn = sn[i + 1].split(',')
            snn = snn[0].split(')')
            tags.append(snn[0])
            tags_time.append(tag_time)
    print("Retrieve all release tags:\n",tags)
    print("The Time of all release tags:\n",tags_time)

    tt = tags
    tm = tags_time
    if len(tags) > 20:
        tagss = []
        tagt = []
        m = round(len(tags)/20)
        m= int(m)
        tagss.append(tags[0])
        tagt.append(tags_time[0])
        j=0
        for i in range(20):
            if j+m < len(tags):
                tagss.append(tags[j+m])
                tagt.append(tags_time[j+m])
            j = j +m
        if j + m < len(tags):
            tagss.append(tags[len(tags)-1])
            tagt.append(tags_time[len(tags)-1])
        tt = tagss
        tm = tagt
    print(tt)

    code1 = []
    code2 = []
    # Count CodeSize of all tags
    for tag in tt:
        git(['checkout',tag])
        # Count the CodeSize of tag
        code_count = cloc(['.'])
        #print(tag,code_count)
        code_count = str(code_count[0])
        code_count = code_count.split(' ')
        CodeSize = (code_count[len(code_count) - 1].split('\\n'))[0].split('\n')[0]
        code1.append(CodeSize)
        print(tag,CodeSize)
        # Remove tests and count CodeSize of tag
        code_count_no_tests = cloc(['--exclude-dir=tests,test', '.'])
        code_count_no_tests = str(code_count_no_tests[0])
        code_count_no_tests = code_count_no_tests.split(' ')
        CodeSize_no_tests = (code_count_no_tests[len(code_count_no_tests) - 1].split('\\n'))[0].split('\n')[0]
        code2.append(CodeSize_no_tests)
    print("The CodeSize of all release tags :\n",code1)
    print("The CodeSize of all release tags (removed test):\n", code2)

    # write data to git_name.csv file
    os.chdir(base_path)
    with open(csv_name + ".csv","w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["tags","tags_time","codesize","codesize_no_tests"])
        rw=[tt,tm,code1,code2]
        # rw = [tags,tags_time,code1,code2]
        new = []
        for i in range(len(rw[0])):
            row = []
            for j in range(len(rw)):
                row.append(rw[j][i])
            new.append(row)
        writer.writerows(new)
    end = datetime.datetime.now()
    st = end - start
    print("Time is :",st)
