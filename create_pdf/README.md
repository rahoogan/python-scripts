# Create PDF

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

## Examples

- Create a pdf from all jpg and pdf files in a dir:

```bash
python3 create_pdf.py -d ./filedir -t pdf jpg jpeg -o mypdf.pdf
```

- Create a pdf from input files specified
```bash
python3 create_pdf.py ./filedir/file1.jpeg ./filedir/file2.pdf ./filedir/file3.png -o mypdf2.pdf
```

## Dependencies
- [PyPDF2](https://github.com/mstamy2/PyPDF2): Pure python pdf reader/writer lib, including merge functionality
- [img2pdf](https://github.com/josch/img2pdf): Python library to convert images to pdf files. More efficient with resources (memory and CPU usage) than other libraries, or simply just using PIL.




