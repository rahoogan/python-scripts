################################
# Name: generate_readme.py
# Description: Generates a README markdown file summarising any READMEs within sub-directories
# Last Updated: June 2020
################################

import argparse
import os

def get_summary(file_desc):
    '''Get the summary of a readme file - content between first title and second title'''
    title, lines, in_quote = '', [], False
    for i, line in enumerate(file_desc):
        # Handle literal quotes
        if line.startswith('```') and not in_quote:
            in_quote = True
        elif line.startswith('```') and in_quote:
            in_quote = False
        # Get contents of markdown (skip header) until the first subsection
        if i == 0:
            title = line
        else:
            if line.startswith('#') and not in_quote:
                break
            lines.append(line)
    return title, lines

def generate(args):
    '''Generate a README.md file'''
    main_doc = []
    main_title = ''
    main_summary = []

    main_file = os.path.join(args.repodir, args.filename)
    if os.path.isfile(os.path.join(main_file)):
        with open(main_file, 'r') as f:
            main_title, main_summary = get_summary(f)

    if not (main_title and main_summary):
        # Get Main Repo Title
        main_title = input('Enter a title for the root repo:\n')
        main_doc.append(f'# {main_title}\n\n')

        # Get Main repo description
        print("Enter a short description for the root repo. Ctrl-D or Ctrl-Z ( windows ) to save it.")
        while True:
            try:
                line = input()
            except EOFError:
                break
            main_summary.append(line)
        main_doc += main_summary
        main_doc.append('\n\n')
    else:
        main_doc.append(main_title)
        main_doc += main_summary

    # Get Subsection details
    index = ['### Index\n\n']
    subsection = []
    num = 1
    for name in os.listdir(args.repodir):
        subfile = os.path.join(os.path.join(args.repodir, name), args.subfilename)
        # Ignore hidden directories
        if not name.startswith('.') and os.path.isfile(subfile):
            with open(subfile, 'r') as f:
                subsection_title, subsection_lines = get_summary(f)
                subsection_title = subsection_title.replace('#', f'{str(num)}.')
                index.append(f'|--- [{subsection_title}]({os.path.relpath(subfile, args.repodir)})\n\n')
                subsection.append(f'## {subsection_title}')
                subsection += subsection_lines
                subsection.append('\n\n')
            num+=1
    
    if args.index:
        main_doc += index
    if not args.nosummary:
        main_doc += subsection

    with open(main_file, 'w') as f:
        f.write(''.join(main_doc))
    print(f'Successfully generated README file: {main_file}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a README.md file with summaries of READMEs in sub-directories')
    parser.add_argument('--rootdir', '-d', help='The root directory to generate the file in', required=True, dest='repodir')
    parser.add_argument('--filename', '-f', default='README.md', help='Name of file to generate')
    parser.add_argument('--subfilename', '-s', default='README.md', help='Name of file in subdirectories to summarise')
    parser.add_argument('--index', '-i', default=False, action='store_true', help='Generate an index of all files in subdirectory')
    parser.add_argument('--no-summary', '-n', dest='nosummary', default=False, action='store_true', help="Don't include a summary of READMEs from sub-directories")

    args = parser.parse_args()
    generate(args)

