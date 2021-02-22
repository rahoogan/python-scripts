import argparse
import re
import os
from datetime import datetime
from dateutil import parser as dparser
from jira import JIRA
from pprint import pprint

date_rgx = re.compile(r'[0-9]{1,2}/[0-9]{1,2}/[0-9]{2,4}') #TODO: support other formats
entry_rgx = re.compile(r'^\s*([0-9]{1,2}:[0-9]{1,2}[\s-]*[0-9]{1,2}:[0-9]{1,2})[\s-]*(.*)$')

def get_project_regex(projects):
    project_string = f'(?:{"|".join(projects)})'
    return re.compile(rf'({project_string}-[0-9]{{1,9}})')

def print_summary(data):
    for issue, wls in data.items():
        print(f'{issue}:')
        for wl in wls:
            print(f'    * {wl.get("dateStarted")} - {wl.get("timeSpent")}: {wl.get("comment")}')

def log_to_jira(data, jira_url, username, password):
    jira = JIRA(options={"server": jira_url, "verify": False}, auth=(username, password))

    skipped = {}
    for issue, wls in to_log.items():
        if jira.issue(issue):
            for wl in wls:
                jira.add_worklog(
                    issue,
                    timeSpent=wl.get('timeSpent'),
                    started=wl.get('dateStarted'),
                    comment=wl.get('comment')
                )
                print(f'Updated {issue}: {wl.get("timeSpent")}')
        else:
            skipped[issue] = wls
    if skipped:
        print('WARNING: The following issues were skipped:')
        print_summary(skipped)

def on_run(a):
    # Check timesheet file exists
    if not os.path.exists(a.file):
        raise Exception(f'timesheet file does not exists: {a.file}')

    if not a.projects:
        raise Exception('at least one project must be specified')

    to_log = {}

    with open(a.file, 'r') as f:
        skip = False
        current_date = None
        for idx, line in enumerate(f):
            # Search for a line with a date
            date = re.search(date_rgx, line)
            if date:
                # Check if already logged
                if '@logged' in line:
                    skip = True
                else:
                    try:
                        current_date = datetime.strptime(date.group(), '%d/%m/%Y')
                        skip = False
                    except ValueError:
                        print(f'WARNING: Could not parse date - {current_date}, skipping entry')
                        current_date = None
                        skip = True
            elif current_date and not skip:
                # Check if entry contains JIRA issue
                project_rgx = get_project_regex(a.projects)
                issues = re.findall(project_rgx, line)
                if issues:
                    # Check if valid entry for date
                    parsed_entry = re.match(entry_rgx, line)
                    if not parsed_entry:
                        print(f'WARNING: Skipping entry as it does not match format: {line}')
                        continue
                    if len(parsed_entry.groups()) != 2:
                        print(f'WARNING: Could not parse entry on line {idx}: {line}')
                    else:
                        parsed_entry = parsed_entry.groups()
                        start, end = None, None
                        if '-' in parsed_entry[0]:
                            start, end = parsed_entry[0].split('-')
                        else:
                            start, end = parsed_entry.split()
                        if start and end:
                            start = dparser.parse(start.strip())
                            end = dparser.parse(end.strip())
                            delta = end - start

                            total_seconds = delta.seconds
                            if len(issues) > 1:
                                # Divide the time equally between issues if multiple issues mentioned in same entry
                                total_seconds = delta.seconds/len(issues)
                            
                            m, s = divmod(total_seconds, 60)
                            h, m = divmod(m, 60)

                            if h >= 12:
                                h = h - 12 # handle 12h/24h

                            time_spent = ""
                            if h and m:
                                time_spent = f'{h}h {m}m'
                            elif m:
                                time_spent = f'{m}m'
                            elif h:
                                time_spent = f'{h}h'

                            for issue in issues:
                                if issue not in to_log:
                                    to_log[issue] = []
                                to_log[issue].append({
                                    "timeSpent": time_spent,
                                    "dateStarted": current_date,
                                    "comment": parsed_entry[1]
                                })
        
    print("About to log the following to JIRA:")
    print_summary(to_log)
    while True:
        prompt = input("Do you wish to continue? answer y or n\n")
        if prompt in ['y', 'yes']:
            log_to_jira(to_log, a.jira_url, a.username, a.password)
            break
        elif prompt in ['n', 'no']:
            break


if __name__ == '__main__':
    parser = argparse.ArgumentParser('Upload worklogs to JIRA from a plaintext timesheet file')
    parser.add_argument('--file', help='Path to timesheet file', required=True)
    parser.add_argument('--username', help='JIRA Username', required=True)
    parser.add_argument('--password', help='JIRA Password', required=True)
    parser.add_argument('--jira-url', help='JIRA URL', required=False, default='https://jira.atlassian.com')
    parser.add_argument('--projects', nargs='+', type=str, required=True)

    parser.set_defaults(func=on_run)
    args = parser.parse_args()
    args.func(args)