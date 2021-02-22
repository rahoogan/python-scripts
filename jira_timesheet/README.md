# JIRA Timehseet

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


## Example Usage

```bash
$ python timesheet.py --file example_timesheet.md --password ${JIRA_PASSWORD} --username "${JIRA_USERNAME}" --projects BUG
About to log the following to JIRA:
BUG-2020:
    * 2020-01-09 00:00:00 - 3h 30m: A pandemic is born BUG-2020
BUG-2019:
    * 2020-01-09 00:00:00 - 2h: Hello, I am bug BUG-2019
BUG-2022:
    * 2020-01-09 00:00:00 - 2h 30m: Finishing work on BUG-2022
BUG-1345:
    * 2020-01-10 00:00:00 - 1h 40m: Another day another bug BUG-1345
BUG-5050:
    * 2020-01-10 00:00:00 - 5h 40m: Worked like a dog on BUG-5050
Do you wish to continue? answer y or n
n
```
