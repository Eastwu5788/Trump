"""
Auto build xcode project and create .ipa file
"""

import os
import sys
import argparse
import configparser
import datetime
from subprocess import Popen, PIPE

py2 = sys.version_info[0] == 2
if py2:
    reload(sys)
    sys.setdefaultencoding('utf8')

config_path = "./config.ini"


def load_config(path):
    if not path or not os.path.exists(path):
        path = config_path

    config_ini = configparser.ConfigParser()
    config_ini.read(path)
    return config_ini


def check_config(config):
    """
    检查用户配置
    """
    target = config["Project"]["target"]
    if not target:
        return False, "Please input target name that you want to build"

    scheme = config["Project"]["scheme"]
    if not scheme:
        scheme = target

    return True, None


def prepare_build_path(config):
    """
    准备打包的路径
    """
    archive_path = config["archive_path"]
    ipa_path = config["ipa_path"]

    if not archive_path.endswith("/"):
        archive_path += "/"
    if not ipa_path.endswith("/"):
        ipa_path += "/"

    time_str = datetime.datetime.now().strftime("%Y-%M-%d %h:%m:%s")

    archive_path = archive_path + config["target"] + time_str
    ipa_path = ipa_path + config["target"] + time_str

    if not os.path.exists(archive_path):
        os.makedirs(archive_path, 0o777)

    if not os.path.exists(ipa_path):
        os.makedirs(ipa_path, 0o777)

    config["archive_path"] = archive_path
    config["ipa_path"] = ipa_path


def auto_build_project(path, config):

    prepare_build_path(config)

    cmd = """xcodebuild -exportArchive 
                        -archivePath '%s' 
                        -exportPath '%s' 
                        -exportOptionsPlist '%s'
          """ % (config[""])

def main():
    parser = argparse.ArgumentParser(description="Thanks for use this script!")
    parser.add_argument("-i", "--input", type=str, default=None, help="The path of the xcode project")

    args = parser.parse_args()
    if not args.input:
        print("Error: Project is not exists!")
        exit(0)

    config = load_config(path=config_path)
    success, message = check_config(config)
    if not success:
        print(message)
        exit(0)

    auto_build_project(args.input, config)
    print("Success Build!")

if __name__ == "__main__":
    main()
