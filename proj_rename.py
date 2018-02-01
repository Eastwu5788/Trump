# -*- coding: utf-8 -*-
# Copyright (c) 2018, Wu Dong
# All rights reserved.

"""
This script is designed to replace special characters in documents.
Specially this script can only replace file which name is end with .h or .m

Usage:
python2 proj_rename.py -i ./Quokka -p ./project.pbxproj -s TL -r Quka  -c True

OR
python proj_rename.py --input ./Quokka -project ./project.pbxproj --start TL --replace LD --content True

Otherwise you can use args below to get help
python proj_rename.py -h
"""
__version__ = "0.0.3"

import os
import argparse
import sys
import re
import json

py2 = sys.version_info[0] == 2

if py2:
    reload(sys)
    sys.setdefaultencoding('utf8')

ori_start = "TL"
dst_start = "LD"
replace_content = False
input_file = ""

replace_dict = dict()

# deal with path name: libs
ignore_dir_names = []
# deal with: /User/libs
ignore_dirs = []
# ignore special file names
ignore_file_name = []
# the script only replace file name and content with ext below
replace_file_ext = [".h", ".m", ".mm", ".xib", ".storyboard"]
# deal with UIImage+TLExt.h
left_start = ["+"]


def replace_file(source_path, func=None):
    if not os.path.exists(source_path):
        return

    # ignore path
    if source_path in ignore_dirs:
        return

    for (base_path, sub_path_list, file_name_list) in os.walk(source_path):

        if base_path in ignore_dirs:
            continue

        document_name = base_path.split("/")[-1]
        if document_name in ignore_dir_names:
            continue

        for file_name in file_name_list:
            # ignore file name
            if file_name in ignore_file_name:
                continue

            if func:
                if not check_file_replace_needed_with_ext(file_name):
                    continue
                replace_file_content(os.path.join(base_path, file_name), func)
            else:
                rename_file(base_path, file_name)


def rename_file(file_path, file_name):
    if not check_file_replace_needed_with_ext(file_name):
        return

    ori_file_path = os.path.join(file_path, file_name)
    replaced_file_name = generate_new_file_name(file_name)
    dst_file_path = os.path.join(file_path, replaced_file_name)

    if ori_file_path == dst_file_path:
        return

    replace_dict[file_name] = replaced_file_name
    os.rename(ori_file_path, dst_file_path)


def make_replace_func(rep_dict, ext=True):

    ext_dict = dict()
    if not ext:
        for key, value in replace_dict.items():
            ext_dict[key.split(".")[0]] = value.split(".")[0]
    else:
        ext_dict = rep_dict

    replace_pattern = re.compile("|".join(map(re.escape, ext_dict)))

    def match_func(match):
        rep_str = ext_dict.get(match.group(0), None)
        if not rep_str:
            rep_str = match.group(0)
        return rep_str

    def replace_func(text):
        return replace_pattern.sub(match_func, text)

    return replace_func


def check_file_replace_needed_with_ext(file_name):
    """
    check file ext in replace_file_ext list
    """
    if not file_name:
        return False

    for ext in replace_file_ext:
        if file_name.endswith(ext):
            return True

    return False


def generate_new_file_name_needed(file_name):
    # deal with TLImage.h
    if file_name.startswith(ori_start):
        return True

    # deal with UIImage+TLExt.h
    for left in left_start:
        left += ori_start
        if left in file_name:
            return True


def generate_new_file_name(file_name):
    """
    Generate a new file name
    :param file_name: origin file name
    """
    if not generate_new_file_name_needed(file_name):
        return file_name

    return file_name.replace(ori_start, dst_start)


def replace_file_content(file_path, func):
    """
    replace content of file
    """
    # read file content and replace it
    with open(file_path, "r") as file:
        file_data = func(file.read())

    # write data to origin file
    with open(file_path, "w") as file:
        file.write(file_data)


if __name__ == "__main__":
    des = """This script is designed to replace special characters in documents. \n
    Specially this script can only replace file which name is end with .h or .m
    """
    parser = argparse.ArgumentParser(description=des)
    parser.add_argument("-i", "--input", type=str, default=None, help="The Document you want to replace")
    parser.add_argument("-p", "--project", type=str, default=None, help="The document path of project")
    parser.add_argument("-s", "--start", type=str, default=None, help="The characters you want to replace")
    parser.add_argument("-r", "--replace", type=str, default=None, help="Replace characters")
    parser.add_argument("-c", "--content", type=bool, default=False, help="Replace Content")

    args = parser.parse_args()
    input_file = args.input
    if not input_file:
        print("Error: Please input file path that you want to replace")
        exit(0)

    if args.start:
        ori_start = args.start

    if args.replace:
        dst_start = args.replace

    if args.content:
        replace_content = args.content

    print("Replace Start ...")

    print("Replace file name ...")
    # replace file name
    replace_file(input_file)
    print("Replace file name Completed!")

    print("Save replace cache ...")
    # cache replace result
    with open(os.path.join(input_file, "replace_cache.json"), "w") as file:
        file.write(json.dumps(replace_dict))
    print("Save replace cache Completed!")

    # replace file content
    if args.content and replace_dict:
        print("Replace file content ...")
        func = make_replace_func(replace_dict, ext=False)
        replace_file(input_file, func)
        print("Replace file content Completed!")

    if args.project and replace_dict:
        print("Replace project content ...")
        func = make_replace_func(replace_dict)
        if os.path.exists(args.project):
            replace_file_content(args.project, func)
            print("Replace project content Completed!")
        else:
            print("Project file is not exit!")

    print("Replace Completed!!")


