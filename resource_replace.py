# -*- coding: utf-8 -*-
# Copyright (c) 2018, Wu Dong
# All rights reserved.
"""
This script is designed to copy resources from one file to another.
If there are same resource in the same path, the document in the destination file path will be replaced by the document
in source file path
If file path is not exists in the destination path, it will create a new file path for it

Usage:
python resource_replace.py -i ./iOSImages -o ./Images
OR:
python resource_replace.py -input ./iOSImages -output ./Images

Help:
python resource_replace.py -h
"""

__version__ = "0.0.1"

import argparse
import os
import shutil


def replace_resource(origin_path, base_dst_path):

    for (base_path, sub_path_list, file_name_list) in os.walk(origin_path):

        for file_name in file_name_list:
            ori_file = os.path.join(base_path, file_name)
            dst_path = base_path.replace(origin_path, base_dst_path)

            if not os.path.exists(dst_path):
                os.makedirs(dst_path, 0o777)

            dst_file = os.path.join(dst_path, file_name)
            shutil.copyfile(ori_file, dst_file)


if __name__ == "__main__":
    des = """This script is designed to copy resources from one file to another."""
    parser = argparse.ArgumentParser(description=des)
    parser.add_argument("-i", "--input", type=str, default=None, help="The New Resource Document")
    parser.add_argument("-o", "--output", type=str, default=None, help="The Replaced Resource Document")
    args = parser.parse_args()

    from_path = args.input
    if not from_path or not os.path.exists(from_path):
        print("Input file path is not exists!")
        exit(0)

    to_path = args.output
    if not to_path or not os.path.exists(to_path):
        print("Output file path is not exists!")
        exit(0)

    print("Start replace resource...")
    replace_resource(from_path, to_path)
    print("Replace resource Completed!!")
