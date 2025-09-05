#!/usr/bin/env python3
# Copyright (c) 2021-2023 Asustor Systems, Inc. All Rights Reserved.

import argparse
import csv
import glob
import json
import os
import re
import shutil
import sys
import tarfile
import tempfile
import zipfile

__author__ = "Walker Lee <walkerlee@asustor.com>"
__copyright__ = "Copyright (C) 2021-2023  ASUSTOR Systems, Inc.  All Rights Reserved."
__version__ = "0.1.0.post1"


class Chdir:
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


class Apkg:
    mask = 18
    os.umask(mask)

    tmp_dir = "/tmp"

    tmp_prefix = "APKG-"

    apk_format = {
        "version": "2.0",
        "format": "zip",
        "suffix": "apk",
    }

    apk_file_contents = {
        "version": "apkg-version",
        "data": "data.tar.gz",
        "control": "control.tar.gz",
    }

    apk_special_folders = {
        "control": "CONTROL",
        "webman": "webman",
        "web": "www",
    }

    apk_control_files = {
        "pkg-config": "config.json",
        "changlog": "changelog.txt",
        "description": "description.txt",
        "icon": "icon.png",
        "script-pre-install": "pre-install.sh",
        "script-pre-uninstall": "pre-uninstall.sh",
        "script-post-install": "post-install.sh",
        "script-post-uninstall": "post-uninstall.sh",
        "script-start-stop": "start-stop.sh",
    }

    apk_web_settings = {
        "user": "admin",
        "group": "administrators",
        "uid": 999,
        "gid": 999,
        "perms": 770,
    }

    def __init__(self):
        self.pid = os.getpid()
        self.cwd = os.getcwd()
        self.pkg_tmp_dir = self.tmp_dir + "/APKG." + str(self.pid)

    def __del__(self):
        pass

    def pkg_misc_check(self):
        pass

    def compress_pkg(self):
        pass

    def __check_apk_format(self, apk_file):
        file_list = []

        # check apk file format
        try:
            with zipfile.ZipFile(apk_file, "r") as apk_zip:
                file_list = apk_zip.namelist()
        except zipfile.BadZipfile:
            print(f"error: file is not an apk file: {apk_file}", file=sys.stderr)
            return False

        # check apk file contents
        if not file_list:
            print(f"error: file is empty: {apk_file}", file=sys.stderr)
            return False

        result = True
        for key, value in self.apk_file_contents.items():
            if value not in file_list:
                print(f"error: can't find file in apk file: {value}", file=sys.stderr)
                result = False

        return result

    # return True for files we want to exclude
    def __filter_files(self, file: tarfile.TarInfo):
        if "CONTROL" in file.name:
            return None
        return file

    def __zip_archive(self, apk_file, file_list):
        with zipfile.ZipFile(apk_file, "w") as apk_zip:
            for one_file in file_list:
                apk_zip.write(one_file)

    def __tar_archive(self, tar_file, path):
        # create a tar archive of directory
        with tarfile.open(tar_file, "w:gz") as tar:
            if os.path.basename(tar_file) == self.apk_file_contents["data"]:
                tar.add(path, filter=self.__filter_files)
            else:
                tar.add(path)

    def __get_app_info_v1(self, control_dir):
        with open(control_dir + "/" + self.apk_control_files["pkg-config"]) as data_file:
            data = json.load(data_file)
        return data

    def __get_app_info_v2(self, control_dir):
        with open(control_dir + "/" + self.apk_control_files["pkg-config"]) as data_file:
            data = json.load(data_file)
        return data

    def __get_app_info(self, control_dir, apkg_version):
        if apkg_version == "1.0":
            # TODO:
            return self.__get_app_info_v1(control_dir)
        elif apkg_version == "2.0" or apkg_version == "2.1":
            return self.__get_app_info_v2(control_dir)
        else:
            return None

    def __check_app_layout(self, app_dir):
        control_dir = app_dir + "/" + self.apk_special_folders["control"]

        if not os.path.isdir(control_dir):
            print("[Not found] CONTROL folder: %s" % (control_dir))
            return False

        config_file = control_dir + "/" + self.apk_control_files["pkg-config"]

        if not os.path.isfile(config_file):
            print("[Not found] config file: %s" % (config_file))
            return False

        # TODO: check icon exist?
        control_dir + "/" + self.apk_control_files["icon"]

        return True

    def __check_app_info_fields(self, app_info):
        require_fields = ["package", "version", "architecture", "firmware"]

        for field in require_fields:
            try:
                if app_info["general"][field].strip() == "":
                    print("Empty field: %s" % (field))
                    return False
            except KeyError:
                print("Missing field: %s" % (field))
                return False

        return True

    def __filter_special_chars(self, string, pattern):
        filter_string = re.sub(pattern, "", string)
        return filter_string

    def __check_app_package_name(self, package):
        return True if self.__filter_special_chars(package, "[a-zA-Z0-9.+-]") == "" else False

    def create(self, folder, dest_dir=None):
        # check folder does exist
        app_dir = os.path.abspath(folder)
        if not os.path.isdir(app_dir):
            print("Directory doesn't exist: %s" % (app_dir))
            return -1

        control_dir = app_dir + "/" + self.apk_special_folders["control"]
        config_file = control_dir + "/" + self.apk_control_files["pkg-config"]

        # check package layout is correct
        if not self.__check_app_layout(app_dir):
            print("Invalid App layout: %s" % (app_dir))
            return -1

        # change file mode and owner
        os.chmod(control_dir, 0o755)
        os.chown(control_dir, 0, 0)

        all_files = glob.glob(control_dir + "/*")
        sh_files = glob.glob(control_dir + "/*.sh")
        py_files = glob.glob(control_dir + "/*.py")

        for one_file in all_files:
            os.chmod(one_file, 0o644)
            os.chown(one_file, 0, 0)

        for one_file in sh_files:
            os.chmod(one_file, 0o755)
            os.system("dos2unix %s > /dev/null 2>&1" % (one_file))

        for one_file in py_files:
            os.chmod(one_file, 0o755)

        app_info = self.__get_app_info(control_dir, self.apk_format["version"])

        # check config.json fields
        if not self.__check_app_info_fields(app_info):
            print("Invalid App config: %s" % (config_file))
            return -1

        # check package field value
        if not self.__check_app_package_name(app_info["general"]["package"]):
            print("Invalid App package field: %s (valid characters [a-zA-Z0-9.+-])" % ("package"))
            return -1

        # prepare tmp dir
        tmp_dir = tempfile.mkdtemp(prefix=self.tmp_prefix)

        version_file = tmp_dir + "/" + self.apk_file_contents["version"]
        control_tar_gz = tmp_dir + "/" + self.apk_file_contents["control"]
        data_tar_gz = tmp_dir + "/" + self.apk_file_contents["data"]

        if dest_dir == None:
            dest_dir = os.getcwd()
        else:
            dest_dir = os.path.abspath(dest_dir)

        apk_file = (
            dest_dir
            + "/"
            + app_info["general"]["package"]
            + "_"
            + app_info["general"]["version"]
            + "_"
            + app_info["general"]["architecture"]
            + "."
            + self.apk_format["suffix"]
        )

        # write apkg version
        with open(version_file, "w") as apkg_version:
            apkg_version.write(self.apk_format["version"] + "\n")

        # archive data files
        with Chdir(app_dir):
            self.__tar_archive(data_tar_gz, ".")

        # archive control files
        with Chdir(control_dir):
            self.__tar_archive(control_tar_gz, ".")

        # archive apk file
        with Chdir(tmp_dir):
            self.__zip_archive(
                apk_file,
                [self.apk_file_contents["version"], self.apk_file_contents["control"], self.apk_file_contents["data"]],
            )

        # cleanup temp folder
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return apk_file

    def convert(self, package):
        app_dir = self.extract(package, dest_dir="/tmp")

        if app_dir == -1:
            print("Convert error")
            return -1

        control_dir = app_dir + "/" + self.apk_special_folders["control"]
        config_file = control_dir + "/" + self.apk_control_files["pkg-config"]
        changelog_file = control_dir + "/" + self.apk_control_files["changlog"]
        description_file = control_dir + "/" + self.apk_control_files["description"]

        app_new_info = {}

        app_new_info["general"] = {}
        app_new_info["general"]["package"] = app_old_info["app"]["package"]
        app_new_info["general"]["name"] = app_old_info["app"]["name"]
        app_new_info["general"]["version"] = app_old_info["app"]["version"]
        app_new_info["general"]["depends"] = app_old_info["app"]["depends"]
        app_new_info["general"]["conflicts"] = app_old_info["app"]["conflicts"]
        app_new_info["general"]["developer"] = app_old_info["app"]["website"]
        app_new_info["general"]["maintainer"] = app_old_info["app"]["maintainer"]
        app_new_info["general"]["email"] = app_old_info["app"]["email"]
        app_new_info["general"]["website"] = app_old_info["app"]["website"]
        app_new_info["general"]["architecture"] = app_old_info["app"]["architecture"]
        app_new_info["general"]["firmware"] = "2.0"

        try:
            app_old_info["desktop"]
        except KeyError:
            app_old_info["desktop"] = {}

        try:
            app_old_info["desktop"]["icon"]
        except KeyError:
            app_old_info["desktop"]["icon"] = {}

        # remove unused field
        app_old_info["desktop"]["icon"].pop("title", None)

        try:
            app_old_info["desktop"]["privilege"]
        except KeyError:
            app_old_info["desktop"]["privilege"] = {}

        app_new_info["adm-desktop"] = {}
        app_new_info["adm-desktop"]["app"] = app_old_info["desktop"]["icon"]
        app_new_info["adm-desktop"]["privilege"] = app_old_info["desktop"]["privilege"]

        try:
            app_old_info["install"]["link"]
        except KeyError:
            app_old_info["install"]["link"] = {}

        try:
            app_old_info["install"]["share"]
        except KeyError:
            app_old_info["install"]["share"] = []

        try:
            app_old_info["install"]["service-reg"]
        except KeyError:
            app_old_info["install"]["service-reg"] = {}

        try:
            app_old_info["install"]["service-reg"]["priority"]
        except KeyError:
            app_old_info["install"]["service-reg"]["priority"] = {}

        try:
            app_old_info["install"]["service-reg"]["port"]
        except KeyError:
            app_old_info["install"]["service-reg"]["port"] = []

        try:
            app_old_info["install"]["dep-service"]
        except KeyError:
            app_old_info["install"]["dep-service"] = {}

        try:
            app_old_info["install"]["dep-service"]["start"]
        except KeyError:
            app_old_info["install"]["dep-service"]["start"] = []

        try:
            app_old_info["install"]["dep-service"]["restart"]
        except KeyError:
            app_old_info["install"]["dep-service"]["restart"] = []

        app_new_info["register"] = {}
        app_new_info["register"]["symbolic-link"] = app_old_info["install"]["link"]
        app_new_info["register"]["share-folder"] = app_old_info["install"]["share"]
        app_new_info["register"]["port"] = app_old_info["install"]["service-reg"]["port"]
        app_new_info["register"]["boot-priority"] = {}

        try:
            app_new_info["register"]["boot-priority"]["start-order"] = app_old_info["install"]["service-reg"][
                "priority"
            ]["start"]
        except KeyError:
            pass

        try:
            app_new_info["register"]["boot-priority"]["stop-order"] = app_old_info["install"]["service-reg"][
                "priority"
            ]["stop"]
        except KeyError:
            pass

        app_new_info["register"]["prerequisites"] = {}
        app_new_info["register"]["prerequisites"]["enable-service"] = app_old_info["install"]["dep-service"]["start"]
        app_new_info["register"]["prerequisites"]["restart-service"] = app_old_info["install"]["dep-service"]["restart"]

        # get changelog and description
        changelog = app_old_info["app"].pop("changes", None).strip()
        description = app_old_info["app"].pop("description", None).strip()

        # convert json object to string
        json_string = json.dumps(app_new_info, indent=3)

        # set new format app information
        with open(config_file, "w") as new_file:
            new_file.write(json_string + "\n")

        # write changelog.txt
        if changelog is not None and changelog != "":
            with open(changelog_file, "w") as new_file:
                new_file.write(changelog + "\n")

        # write description.txt
        if description is not None and description != "":
            with open(description_file, "w") as new_file:
                new_file.write(description + "\n")

        convert_dir = os.getcwd() + "/apk-2.0"
        if not os.path.exists(convert_dir):
            os.mkdir(convert_dir)

        # re-pack apk
        apk_file = self.create(app_dir, dest_dir=convert_dir)

        # cleanup app folder
        shutil.rmtree(app_dir, ignore_errors=True)

        print("Convert success: %s" % (apk_file))

    def upload(self, package):
        # check file is exist
        abs_path = os.path.abspath(package)
        if not os.path.isfile(abs_path):
            print("File doesn't exist: %s" % (abs_path))
            return -1

        print("function not support: %s" % ("upload"))


# main
if __name__ == "__main__":
    # create the top-level parser
    parser = argparse.ArgumentParser(description="asustor package helper.")

    subparsers = parser.add_subparsers(help="arguments")

    # create the parser for the "create" commad
    parser_create = subparsers.add_parser("create", help="<folder> [--destination <folder>] create package")
    parser_create.add_argument("folder", help="select a package layout folder to pack")
    parser_create.add_argument("--destination", help="create apk in destination folder")
    parser_create.set_defaults(command="create")

    args = parser.parse_args()
    apkg = Apkg()

    if args.command == "create":
        apkg.create(args.folder, args.destination)
