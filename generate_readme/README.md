# Generate README.md

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

## Examples

Given the following directory structure:

```bash
|- my_scripts
   |- python_scripts
      - README.md
   |- bash_scripts
      - README.md
```
