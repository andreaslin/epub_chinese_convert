#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sys import exit
from subprocess import check_output
from os.path import dirname, realpath, basename, splitext
import os
import argparse
import zipfile
import opencc


class EpubChineseConvert:
    # Configurations available directly from opencc
    ALL_CONFIGS = ["s2t", "t2s", "s2tw", "tw2s", "s2hk", "hk2s", "s2twp",
                   "tw2sp", "t2tw", "t2hk"]
    # Files in epub that needs to convert
    CONVERT_EXTENSIONS = ("html", "htm", "ncx", "opf", "xhtml")

    # The limit size prevent the stdout from overflow, this is system
    # dependence. The size I use here is for Mac OS X
    STDOUT_PIPE_BUFFER_LIMIT = 65536

    def __init__(self, options):
        # Old way of using opencc from command line
        self.OPENCC_BIN_PATH = check_output(["which", "opencc"]).strip()
        self.OPENCC_CONFIG_PATH = check_output(
            ["find", "/usr/local",
             "-name", options.config_option+".json"]).strip()
        self.ABSOLUTE_INPUT_PATH = dirname(realpath(options.input_file))
        self.INPUT_FILE_NAME = splitext(
            basename(realpath(options.input_file)))[0]
        self.COMPRESSION_MODE = zipfile.ZIP_DEFLATED
        self.VERBOSE = True if options.verbose else False

        # Check configuration
        if options.config_option not in EpubChineseConvert.ALL_CONFIGS:
            print("Configuration unavailable. Please use the following: ")
            print(EpubChineseConvert.ALL_CONFIGS)
            exit(1)
        # Setup opencc converter
        self.opencc_converter = opencc.OpenCC(options.config_option + ".json")

        # Check for custom output file
        if not options.output_file:
            self.ABSOLUTE_OUTPUT_PATH = self.ABSOLUTE_INPUT_PATH
            self.OUTPUT_FILE_NAME = self.INPUT_FILE_NAME + "_" + \
                                    options.config_option
        else:
            self.ABSOLUTE_OUTPUT_PATH = dirname(realpath(options.output_file))
            self.OUTPUT_FILE_NAME = basename(self.ABSOLUTE_OUTPUT_PATH)

    def check_install(self):
        if not self.OPENCC_BIN_PATH:
            print("Cannot find opencc command)"),
            print("please check if opencc is installed or linked")
            exit(1)

        if not self.OPENCC_CONFIG_PATH:
            print("Cannot find configuration file")
            exit(1)

    def check_output_path_read_write_permissions(self):
        try:
            os.listdir(self.ABSOLUTE_OUTPUT_PATH)
        except OSError:
            print("No output directory:" + self.ABSOLUTE_OUTPUT_PATH +
                  " permission")
            exit(1)

    def convert_content(self, input_bytes):
        try:
            # Using Popen to execute opencc in command line
            # convert_result = Popen(
            #     [self.OPENCC_BIN_PATH, "-c", self.OPENCC_CONFIG_PATH],
            #     stdin=PIPE, stdout=PIPE)
            # convert_result.stdin.write(input_bytes)
            # convert_result.poll()
            # return convert_result.communicate()[0]
            return self.opencc_converter.convert(input_bytes)
        except ValueError as value_error:
            print("Invalid argument to call opencc")
            raise value_error
        except Exception as e:
            print(e)
            print("Error while using opencc.")
            raise e

    def convert_file(self, file, file_size):
        content = ""
        # Check file extension
        if file.name.endswith(EpubChineseConvert.CONVERT_EXTENSIONS):
            if self.VERBOSE:
                print("Converting {}...".format(file.filename), end='\r')

            # If not able to read file within stdin buffer size, read by lines
            if file_size >= EpubChineseConvert.STDOUT_PIPE_BUFFER_LIMIT:
                for line in file:
                    content += \
                        self.convert_content(line).replace('zh-CN', 'zh-TW')
            # Else convert the content directly through one read
            else:
                content = self.convert_content(
                    file.read()).replace('zh-CN', 'zh-TW')
        else:
            content = file.read()
        file.close()
        return content

    def convert(self):
        self.check_install()
        self.check_output_path_read_write_permissions()

        # Extract file locations
        epub_files = zipfile.ZipFile(self.ABSOLUTE_INPUT_PATH + "/" +
                                     self.INPUT_FILE_NAME + ".epub", mode='r')
        epub_files_output = zipfile.ZipFile(self.ABSOLUTE_OUTPUT_PATH + "/" +
                                            self.OUTPUT_FILE_NAME + ".epub",
                                            mode='w')
        file_list = epub_files.infolist()
        total_num_files = len(file_list)
        try:
            print("Processing files:")
            for i, zipinfo_file in enumerate(file_list):
                content = self.convert_file(epub_files.open(zipinfo_file),
                                            zipinfo_file.file_size)
                percentage = (i + 1) * 100 / total_num_files
                print("{0:20} {1:.2f}%".format(
                    u"\u2588" * int(percentage / 5), percentage), end='\r')
                epub_files_output.writestr(
                    zipinfo_file, content,
                    compress_type=self.COMPRESSION_MODE)
            print("\nConversion complete. Name of file is {"
                  "}.epub".format(self.OUTPUT_FILE_NAME))
        except Exception as e:
            print(e)
            print("Error while extracting/converting...")
            os.remove(self.ABSOLUTE_OUTPUT_PATH + "/" +
                      self.OUTPUT_FILE_NAME + ".epub")
            raise e
        finally:
            epub_files.close()
            epub_files_output.close()


def parse_options():
    parser = argparse.ArgumentParser(
        description=
        "Convert between Traditional/Simplified Chinese characters in epub "
        "file")
    parser.add_argument(
        '-i', '--input_file', required=True,
        help="The name of the input file.")
    parser.add_argument(
        '-o', '--output_file',
        help="The name of the output file (if specified).")
    parser.add_argument(
        '-c', '--config_option', required=True,
        help="The configuration file used, refer to opencc json config "
             "files.\n" + ','.join(EpubChineseConvert.ALL_CONFIGS))
    parser.add_argument(
        '-v', '--verbose',
        help="Verbose output")
    return parser.parse_args()


def main():
    converter = EpubChineseConvert(parse_options())
    converter.convert()
    return 0

if __name__ == "__main__":
    main()
