########################################
# Name: create_pdf.py
# Description: Create a PDF file by merging existing pdf files and/or images (JPEG, PNG supported)
# Author: Rahul Raghavan
# Last Updated: June 2020
########################################

from io import BytesIO
from PyPDF2 import PdfFileMerger
from PIL import Image
from functools import partial
import argparse
import img2pdf
import os
import re

supported_formats = ['pdf', 'jpeg', 'jpg', 'png', 'bmp']

def alphanum_key(s):
    '''Create a natutal sorting key
    From: https://nedbatchelder.com/blog/200712/human_sorting.html
    '''
    return [ int(c) if c.isdigit() else c for c in re.split('(\d+)', s) ]

def merge(files, output_file):
    '''Merge multiple pdf files'''
    if files:
        merger = PdfFileMerger()
        try:
            for pdf in files:
                if pdf.endswith('pdf'):
                    merger.append(pdf)
                else:
                    f = BytesIO()
                    with open(pdf, 'rb') as f2:
                        img2pdf.convert(f2, outputstream=f)
                        f.seek(0)
                    merger.append(f)
            merger.write(output_file)
        finally:
            merger.close()

def create_pdf(args):
    '''Create a pdf file from multiple files'''
    filtered_files = []
    # Filter files
    for path in args.directory:
        if os.path.isdir(path):
            for filen in sorted(os.listdir(path), key=alphanum_key):
                if filen.split('.')[-1] in supported_formats:
                    filtered_files.append(os.path.join(path, filen))
        elif os.path.isfile(path):
            if filen.split('.')[-1] in supported_formats:
                filtered_files.append(os.path.join(path, filen))
        else:
            raise Exception('File or directory does not exist:{}'.format(path))
    if args.files:
        for path in args.files:
            if os.path.isfile(path):
                add_file(path)

    # Merge files
    merge(filtered_files, args.output)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create a PDF file by merging existing pdf files and/or images')
    parser.add_argument('--output', '-o', help="Output file name", dest='output', required=True)
    parser.add_argument('--filetypes', '-t', choices=['pdf', 'png', 'jpg', 'jpeg'], action='append', default=['pdf', 'png', 'jpg', 'jpeg'], required=False)
    parser.add_argument('--directory', '-d', action='append', default=[], required=False)
    parser.add_argument('files', nargs='*', metavar='file')

    args = parser.parse_args()
    if not args.directory and not args.files:
        print('create_pdf.py: error: one of the following arguments are required: --directory/-d or [files]')
    create_pdf(args)
