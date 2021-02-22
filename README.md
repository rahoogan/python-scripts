# Python Scripts

A collection of useful python utility scripts

## 1. Diaro Export

Simple script to export a diaro backup xml file to markdown plaintext.

```bash
usage: diaro_backup_to_md.py [-h] --filename FILENAME --output OUTPUT

Export a diaro backup xml file to markdown

optional arguments:
  -h, --help            show this help message and exit
  --filename FILENAME, -f FILENAME
                        Name of diaro xml backup file to convert
  --output OUTPUT, -o OUTPUT
                        output filename
```

## 2. Generate README.md

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



## 3. Ansible Playbook: Check Unmanaged Packages

This is a script to run an ansible playbook which runs all the relevant install tasks in `--check` mode, and reports a list of packages that have NOT been installed by the playbook, but have been manually installed on the system, for each play.

```bash
$ python unmanaged_packages.py site.yml -i inventory.yml --ask-sudo-pass --tags package-installs
...
UNMANAGED PACKAGE LIST ************************************************
localhost:
  - sqlite3
  - libsigc++-2.0-0v5
  - build-essential
  - jekyll
  - libxkbcommon-x11-0
192.168.1.3:
  - net-tools
  - packer
```

## 4. Create PDF

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



## 5. JIRA Timehseet

Simple script to update worklogs for JIRA issues based on time tracked in local plaintext file. An example timesheet file format recognised by the script is provided in `example_timesheet.md`.

```bash
usage: Upload worklogs to JIRA from a plaintext timesheet file
       [-h] --file FILE --username USERNAME --password PASSWORD
       [--jira-url JIRA_URL] --projects PROJECTS [PROJECTS ...]

optional arguments:
  -h, --help            show this help message and exit
  --file FILE           Path to timesheet file
  --username USERNAME   JIRA Username
  --password PASSWORD   JIRA Password
  --jira-url JIRA_URL   JIRA URL
  --projects PROJECTS [PROJECTS ...]
```




