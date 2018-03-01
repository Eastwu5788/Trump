# -*- coding: utf-8 -*-
# Copyright (c) 2018, Wu Dong
# All rights reserved.

"""
This script is designed to methods in xcode project.
Specially this script can only replace file which name is end with .h or .m

Usage:
python2 obfuscator.py -i ./Quokka -p TL

OR
python obfuscator.py --input ./Quokka --prefix TL

Otherwise you can use args below to get help
python proj_rename.py -h
"""
__version__ = "0.0.2"

import os
import argparse
import sys
import re
import json
import random

py2 = sys.version_info[0] == 2

if py2:
    reload(sys)
    sys.setdefaultencoding('utf8')

file_name_prefix = None
# deal with: /User/libs
ignore_dirs = []
# deal with path name: libs
ignore_dir_names = ["Venders", "libs", "ThirdPartLibs"]
# ignore special file names
ignore_file_name = []
# the script only replace file name and content with ext below
replace_file_ext = [".h", ".m", ".mm"]

analyzed_property_list = list()
analyzed_method_list = list()
define_rand_list = list()

replace_dict = dict()

ignore_property_list = [
    "width",
    "height",
    "size"
]

ignore_method_list = []

random_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
               'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']


# 自定义过滤 init 开头的方法名
def filter_start_with_init(content):
    """
    过滤init开头的方法名
    """
    if content.startswith("init"):
        return False
    return True


# 自定义过滤器列表
filter_func_list = [
    filter_start_with_init,
]


def replace_file(source_path, func=None, analyze_func=None):
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
            sub_path_list[:] = []
            continue

        for file_name in file_name_list:
            # ignore file name
            if file_name in ignore_file_name:
                continue

            if file_name_prefix and not file_name.startswith(file_name_prefix):
                continue

            if func:
                if not check_file_replace_needed_with_ext(file_name):
                    continue
                replace_file_content(os.path.join(base_path, file_name), func)
            else:
                analyze_file_content(base_path, file_name, analyze_func)


def analyze_file_content(file_path, file_name, analyze_func=None):
    """
    解析文本内容，读取出需要混淆的关键字
    """
    if not analyze_func:
        return

    if not check_file_replace_needed_with_ext(file_name):
        return

    if analyze_func == analyze_oc_method and not file_name.endswith(".h"):
        return

    file_path = os.path.join(file_path, file_name)

    with open(file_path, "r") as file:
        lines = file.readlines()

        for line in lines:
            analyze_func(line)


def analyze_oc_property(content):
    """
    解析 @property 属性
    """
    property_list = re.search("^@property\s*\(.+?\)\s*\w+\s*\*?\s*(\w+?);", content)

    if not property_list:
        return

    prop = property_list.group(1)

    if not prop:
        return

    if prop in ignore_property_list:
        return

    if prop not in analyzed_property_list:
        analyzed_property_list.append(prop)


def analyze_oc_method(content):
    method_list = re.search("^\s*-|\+\s*\(.+?\)\s*(\w+)", content)

    if method_list and valid_method_name(method_list.group(1)):
        analyzed_method_list.append(method_list.group(1))

    method_list = re.search("^\s*-|\+\s*\(.+?\)\s*\w+?\s*:\s*\(\w+?\)\s*\w+?\s+?(\w+?):\(.*?\)\s*\w+?\s*[;{]$", content)

    if method_list and valid_method_name(method_list.group(1)):
        analyzed_method_list.append(method_list.group(1))

    method_list = re.search("^\s*(\w+?)\s*:\s*\(.+?\)\s*\w+\s*;?$", content)

    if method_list and valid_method_name(method_list.group(1)):
        analyzed_method_list.append(method_list.group(1))


def valid_method_name(method):
    if not method:
        return False

    if method in ignore_method_list:
        return False

    if method in analyzed_method_list:
        return False

    if method in analyzed_property_list:
        return False

    for func in filter_func_list:
        if not func(method):
            return False

    return True


def generate_random_replace_string():
    for ori_str in analyzed_method_list:
        rand_str = rand_string()
        replace_dict[ori_str] = rand_str


def rand_string():
    length = random.randint(10, 17)
    ran_str = ''.join(random.sample(random_list, length))
    ran_str += str(random.randint(100, 999))

    while ran_str in define_rand_list:
        ran_str = ''.join(random.sample(random_list, length))
        ran_str += str(random.randint(100, 999))

    define_rand_list.append(ran_str)

    return ran_str


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


def load_ignore_key_words():
    with open("./ignore_key_words", "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.replace(" ", "")
            line = line.replace("\n", "")
            if len(line):
                if line not in ignore_method_list:
                    ignore_method_list.append(line)


def load_extra_method_kew_words():
    with open("./extra_method_key_words", "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.replace(" ", "")
            line = line.replace("\n", "")
            if len(line):
                analyzed_method_list.append(line)


if __name__ == "__main__":
    des = """This script is designed to replace special characters in documents. \n
    Specially this script can only replace file which name is end with .h or .m
    """
    parser = argparse.ArgumentParser(description=des)
    parser.add_argument("-i", "--input", type=str, default=None, help="The Document you want to replace")
    parser.add_argument("-p", "--prefix", type=str, default=None, help="The Prefix of file name")

    args = parser.parse_args()
    input_file = args.input
    if not input_file:
        print("Error: Please input file path that you want to replace")
        exit(0)

    file_name_prefix = args.prefix

    print("Load ignore key words")
    load_ignore_key_words()

    print("Load extra key words")
    load_extra_method_kew_words()

    print("Analyze properties")
    replace_file(input_file, analyze_func=analyze_oc_property)

    print("Analyze methods")
    replace_file(input_file, analyze_func=analyze_oc_method)

    print("Cache analyze result")
    # cache replace result
    with open(os.path.join(input_file, "analyze_property.txt"), "w") as file:
        file.write(str(analyzed_property_list))

    with open(os.path.join(input_file, "analyze_method.txt"), "w") as file:
        file.write(str(analyzed_method_list))

    print("Generate random replace string")
    generate_random_replace_string()

    print("Cache random replace dict")
    with open(os.path.join(input_file, "replace_dict.txt"), "w") as file:
        file.write(str(replace_dict))

    # replace file content
    if replace_dict:
        print("Replace file content ...")
        func = make_replace_func(replace_dict)
        replace_file(input_file, func)
        print("Replace file content Completed!")

    print("------ statistics 000")

    print("Success ...")
