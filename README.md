# Python Scripts

A collection of useful python utility scripts

### Index

|--- [1. Generate README.md
](generate_readme/README.md)

|--- [2. Create PDF
](create_pdf/README.md)

# 1. Generate README.md

Generate a README.md file with summaries of READMEs in sub-directories

```bash
usage: generate_readme.py [-h] --rootdir REPODIR [--filename FILENAME]
                          [--subfilename SUBFILENAME] [--index] [--regenerate]

Generate a README.md file with summaries of READMEs in sub-directories

optional arguments:
  -h, --help            show this help message and exit
  --rootdir REPODIR, -d REPODIR
                        The root directory to generate the file in
  --filename FILENAME, -f FILENAME
                        Name of file to generate
  --subfilename SUBFILENAME, -s SUBFILENAME
                        Name of file in subdirectories to summarise
  --index, -i           Generate an index of all files in subdirectory
  --regenerate, -r      Regenerate an existing file
```



# 2. Create PDF

Simple script to create a pdf file by merging images or other pdf documents

```bash
usage: create_pdf.py [-h] --output OUTPUT [--filetypes {pdf,png,jpg,jpeg}]
                     [--directory DIRECTORY]
                     [file [file ...]]

Create a PDF file by merging existing pdf files and/or images

positional arguments:
  file

optional arguments:
  -h, --help            show this help message and exit
  --output OUTPUT, -o OUTPUT
                        Output file name
  --filetypes {pdf,png,jpg,jpeg}, -t {pdf,png,jpg,jpeg}
  --directory DIRECTORY, -d DIRECTORY

```



