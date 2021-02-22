from datetime import datetime
import xml.etree.ElementTree as ET
import argparse

tags = {}
folders = {}

def convert(args):
    tree = ET.parse(args.filename)
    for x in tree.getroot().findall(".//*[@name='diaro_folders']/r"):
        folders[x.find('./uid').text] = x.find('./title').text
    for x in tree.getroot().findall(".//*[@name='diaro_tags']/r"):
        tags[x.find('./uid').text] = x.find('./title').text
    with open(args.output, 'w') as f:
        for entry in tree.getroot().findall(".//*[@name='diaro_entries']/r"):
            # Print title
            dt = datetime.fromtimestamp(int(int(entry.find('./date').text)/1000)).strftime("%Y-%m-%d %H:%M")
            title = entry.find('./title').text
            f.write(f'# {dt} {title}')

            # Print text
            f.write('\n\n')
            f.write(f"{entry.find('./text').text}")
            f.write('\n')

            # Print tags
            entry_tags = entry.find('./tags').text
            if entry_tags:
                for tag in entry_tags.split(','):
                    tag_name = tags.get(tag)
                    if tag_name:
                        f.write(f'#{tag_name} ')
            folder = entry.find('./folder_uid').text
            if folder:
                folder_name = folders.get(folder)
                if folder_name:
                    f.write(f'#{folder_name}')

            f.write('\n\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Export a diaro backup xml file to markdown')
    parser.add_argument('--filename', '-f', help='Name of diaro xml backup file to convert', required=True)
    parser.add_argument('--output', '-o', help='output filename', required=True)

    args = parser.parse_args()
    convert(args)