# Get tag messages from git depository.
# How to use ?  Command : python git_tag_msg.py <parameter>.
# Parameter is the name of git depository folder. for example: lz4,log4j,etc. [ note : Do not + '/ '].

import subprocess
import os
import sys
import re
import csv

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

def get_git_tags():
    stdout, stderr = git(['tag', '-l'])
    tags = stdout.decode('utf-8').split()
    return tags


if __name__ == '__main__':

    git_name = sys.argv[1]
    base_path=os.getcwd()
    git_path=os.getcwd()+'/'+git_name

    # Switch path to git_path
    os.chdir(git_path)
    # Get all tags
    print('Retrieve all release tags :')
    tags = get_git_tags()
    print(tags)

    # Get time of all tags
    stdout, stderr = git(['log', '--tags','--simplify-by-decoration','--pretty="format:%ci'])
    s = str(stdout, encoding='utf8')
    a = re.findall(r'\d{4}-\d{2}-\d{2}', s)
    a.reverse()
    print("tag time:\n",a)

    code1 = []
    code2 = []
    # Count CodeSize of all tags
    for tag in tags:
        git(['checkout',tag])
        code_count = cloc(['.'])
        # Remove tests and count CodeSize of tag
        code_count_no_tests = cloc(['--exclude-dir=tests','.'])

        code_count = str(code_count[0], encoding="utf-8")
        code_count_no_tests = str(code_count_no_tests[0],encoding="utf-8")

        code_count = code_count.split(' ')
        code_count_no_tests=code_count_no_tests.split(' ')

        CodeSize = (code_count[len(code_count) - 1].split('\n'))[0]
        CodeSize_no_tests = (code_count_no_tests[len(code_count_no_tests)-1].split('\n'))[0]

        code1.append(CodeSize)
        code2.append(CodeSize_no_tests)
    print("Tags Version CodeSize:\n",code1)
    print("Tags Version CodeSize Removed tests:\n", code2)

    # write data to csv file
    os.chdir(base_path)
    with open(git_name+".csv","w") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["tags","tags_time","codesize","codesize_no_tests"])
        rw = [tags,a,code1,code2]
        new = []
        for i in range(len(rw[0])):
            row = []
            for j in range(len(rw)):
                row.append(rw[j][i])
            new.append(row)
        writer.writerows(new)
