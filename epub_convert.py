#!/usr/bin/env python
#-*- coding: utf-8 -*-

from sys import argv, exit
from subprocess import check_output, Popen, PIPE
from shutil import copy
from os.path import dirname, realpath, basename, splitext
from multiprocessing import Pool
import os
import argparse
import zipfile
import zlib

class epub_convert:
    def __init__(self, options):
        self.OPENCC_BIN_PATH = check_output(["which", "opencc"]).strip()    
        self.OPENCC_CONFIG_PATH = check_output(["find", "/usr/local",
                                                "-name", options.config_option+".json"]).strip()
        self.ALL_CONFIGS = ["s2t", "t2s", "s2tw", "tw2s", "s2hk", "hk2s", "s2twp",
                            "tw2sp", "t2tw", "t2hk"]
        self.CONVERT_EXTENSIONS = ("html", "htm", "ncx", "opf", "xhtml")
        self.ABSOLUTE_INPUT_PATH = dirname(realpath(options.input_file))
        self.INPUT_FILE_NAME = splitext(basename(realpath(options.input_file)))[0]
        
        if not options.output_file:
            self.ABSOLUTE_OUTPUT_PATH = self.ABSOLUTE_INPUT_PATH
            self.OUTPUT_FILE_NAME = self.INPUT_FILE_NAME + "_output"
        else:
            self.ABSOLUTE_OUTPUT_PATH = dirname(realpath(options.output_file))
            self.OUTPUT_FILE_NAME = basename(self.ABSOLUTE_OUTPUT_PATH)

        if not options.config_option in self.ALL_CONFIGS:
            print("Configuration unavailable. Please use the following: ")
            print self.ALL_CONFIGS
            exit(1)
            
    def checkInstall(self):
        if not self.OPENCC_BIN_PATH:
            print("Cannot find opencc command, please check if opencc is installed or linked")
            exit(1)

        if not self.OPENCC_CONFIG_PATH:
            print("Cannot find configuration file")
            exit(1)        

    def checkOutputPathReadWritePermissions(self):
        try:
            os.listdir(self.ABSOLUTE_OUTPUT_PATH)
        except OSError:
            print ("No output directory:" + self.ABSOLUTE_OUTPUT_PATH + " permission")
            exit(1)
            
    def convertContent(self, input_bytes):
        try:
            convert_result = Popen(
                [self.OPENCC_BIN_PATH, "-c", self.OPENCC_CONFIG_PATH], stdin=PIPE, stdout=PIPE)
            convert_result.stdin.write(input_bytes)
            convert_result.poll()
            return convert_result.communicate()[0]
        except Exception, e:
            print e
            print "Error while using opencc."
            raise e
                      
    def convert(self):
        self.checkInstall()
        self.checkOutputPathReadWritePermissions()

        epub_files = zipfile.ZipFile(self.ABSOLUTE_INPUT_PATH + "/" + self.INPUT_FILE_NAME + ".epub", mode='r')
        epub_files_output = zipfile.ZipFile(self.ABSOLUTE_OUTPUT_PATH + "/" + self.OUTPUT_FILE_NAME + ".epub",
                                            mode='w')
        compression_mode = zipfile.ZIP_DEFLATED
        num_file_converted = 0
        try:
            for zipinfo_file in epub_files.infolist():
                content = ""
                if zipinfo_file.filename.endswith(self.CONVERT_EXTENSIONS):
                    print "Converting " + zipinfo_file.filename + "..."
                    if zipinfo_file.file_size > 300000:
                        with epub_files.open(zipinfo_file) as f:
                            for line in f:
                                content += self.convertContent(line.replace('zh-CN', 'zh-TW'))
                    else:
                        content = self.convertContent(epub_files.read(zipinfo_file)
                                                      .replace('zh-CN', 'zh-TW'))
                    num_file_converted += 1
                else:
                    content = epub_files.read(zipinfo_file)
                epub_files_output.writestr(zipinfo_file, content,
                                           compress_type = compression_mode)
        except Exception, e:
            print e
            print "Error while extracting/converting..."
            epub_files.close()
            epub_files_output.close()
            os.remove(self.ABSOLUTE_OUTPUT_PATH + "/" + self.OUTPUT_FILE_NAME + ".epub")
            exit(1)
        finally:
            print "Convertion done."
            epub_files.close()
            epub_files_output.close()

        return num_file_converted
            
        
def parseOptions():
    parser = argparse.ArgumentParser(description=
                                     "Convert epub file using opencc in python")
    parser.add_argument('-i', '--input_file', required=True,
                        help="The name of the input file.")
    parser.add_argument('-o', '--output_file',
                        help="The name of the output file (if specified).")
    parser.add_argument('-c', '--config_option', required=True,
                        help="The configuration file used, refer to opencc json config files.")
    return parser.parse_args()
            
def main():
    convertor = epub_convert(parseOptions())
    convert_num = convertor.convert();
    if convert_num:
        print "Successfully converted " + str(convert_num) + " items."
    else:
        print "Error"
    
    return 0

if __name__ == "__main__":
    main()
