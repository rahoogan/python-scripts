import sys
import os
import shutil
from copy import copy
from ansible import context
from ansible import constants as C
from ansible.cli import CLI
from ansible.cli.playbook import PlaybookCLI
from ansible.utils.color import stringc
from ansible.utils.collection_loader import get_collection_name_from_path, set_collection_playbook_paths
from ansible.module_utils.common.collections import ImmutableDict
from ansible.module_utils._text import to_bytes
from ansible.module_utils._text import to_text
from ansible.playbook.play import Play
from ansible.executor.playbook_executor import PlaybookExecutor
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.loader import add_all_plugin_dirs
from ansible.plugins.loader import callback_loader
from ansible.plugins.callback.default import CallbackModule as DefaultCallbackModule

###################################################################
## Handle compatibility options to get rid of warnings. Copied from: https://github.com/ansible/ansible/blob/stable-2.9/lib/ansible/plugins/callback/default.py#L46

# These values use ansible.constants for historical reasons, mostly to allow
# unmodified derivative plugins to work. However, newer options added to the
# plugin are not also added to ansible.constants, so authors of derivative
# callback plugins will eventually need to add a reference to the common docs
# fragment for the 'default' callback plugin

# these are used to provide backwards compat with old plugins that subclass from default
# but still don't use the new config system and/or fail to document the options
# TODO: Change the default of check_mode_markers to True in a future release (2.13)
COMPAT_OPTIONS = (('display_skipped_hosts', C.DISPLAY_SKIPPED_HOSTS),
                  ('display_ok_hosts', True),
                  ('show_custom_stats', C.SHOW_CUSTOM_STATS),
                  ('display_failed_stderr', False),
                  ('check_mode_markers', False),
                  ('show_per_host_start', False))
####################################################################

class CallbackModule(DefaultCallbackModule):
    '''
    Prints package information to stdout
    '''

    CALLBACK_VERSION = 1.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'package_check'

    def __init__(self):
        # Define an object to to store results of detected package installs by the playbook and manual installs per host
        # {
        #     "localhost": {
        #         "manual" set{'steam', 'vim'}
        #         "managed": set{'steam'}
        #     },
        #     "192.168.1.40": {
        #         "manual" set{'ntp', 'sshd'}
        #         "managed": set{'sshd', 'ntp'}
        #     }
        # }
        self.package_info = {}
        # for backwards compat with plugins subclassing default, fallback to constants
        for option, constant in COMPAT_OPTIONS:
            try:
                value = self.get_option(option)
            except (AttributeError, KeyError):
                value = constant
            setattr(self, option, value)
        super(CallbackModule, self).__init__()
        
    def v2_runner_on_ok(self, result):
        # Print any warnings
        self._handle_warnings(result._result)
        h = result._host.get_name()

        # Filter for package installs
        if result._task_fields.get('action') == 'apt':
            # We only care about installs (not uninstalls)
            if result._task_fields.get('args', {}).get('state') != 'absent':
                # Add the package name to list of managed packages
                package_name = result._task_fields.get('args', {}).get('name')
                if package_name:
                    # Build up a de-duplicated list of managed packages for each host
                    # List can be unordered, hence the use of sets
                    if h not in self.package_info:
                        self.package_info[h] = {
                            "manual": set(),
                            "managed": set(),
                            "failed": False
                        }
                    # Handle multiple packages being installed
                    if isinstance(package_name, list):
                        self.package_info[h]["managed"].update(package_name)
                    # Handle single package installs
                    elif isinstance(package_name, str):
                        self.package_info[h]["managed"].add(package_name)
                else:
                    print('Got empty package name')

        # Filter for package installs
        if result._task_fields.get('name') == 'package_check - get real manually installed packages':
            packages = result._task_fields.get('args', {}).get('manual_packages', [])
            if h not in self.package_info:
                self.package_info[h] = {
                            "manual": set(),
                            "managed": set(),
                            "failed": False
                        }
            self.package_info[h]["manual"].update(packages)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        h = result._host.get_name()
        if h not in self.package_info:
            self.package_info[h] = {
                    "manual": set(),
                    "managed": set(),
                    "failed": True
            }
        else:
            self.package_info[h]["failed"] = True

        super(CallbackModule, self).v2_runner_on_failed(result)

    def v2_playbook_on_stats(self, stats):
        if self._display.verbosity:
            super(CallbackModule, self).v2_playbook_on_stats(stats)

    def v2_playbook_on_task_start(self, task, is_conditional):
        if self._display.verbosity:
            super(CallbackModule, self).v2_playbook_on_task_start(task, is_conditional)

    def v2_runner_item_on_ok(self, result):
        if self._display.verbosity:
            super(CallbackModule, self).v2_runner_item_on_ok(result)

    def v2_runner_item_on_failed(self, result):
        h = result._host.get_name()
        if h not in self.package_info:
            self.package_info[h] = {
                    "manual": set(),
                    "managed": set(),
                    "failed": True
            }
        else:
            self.package_info[h]["failed"] = True
        super(CallbackModule, self).v2_runner_item_on_failed(result)

# Initialise our custom callback
results_callback = CallbackModule()

# Read all the arguments from the cli
args = [to_text(a, errors='surrogate_or_strict') for a in sys.argv]

# Ensure dry-run option is specified
if '--check' not in args:
    args.append('--check')

pb_cli = PlaybookCLI(args)
pb_cli.parse()

#####################################################################
### Execute a playbook
# This section is copied directly from: https://github.com/ansible/ansible/blob/stable-2.9/lib/ansible/cli/playbook.py#L71

# manages passwords
sshpass = None
becomepass = None
passwords = {}

b_playbook_dirs = []
for playbook in context.CLIARGS['args']:
    if not os.path.exists(playbook):
        raise AnsibleError("the playbook: %s could not be found" % playbook)
    if not (os.path.isfile(playbook) or stat.S_ISFIFO(os.stat(playbook).st_mode)):
        raise AnsibleError("the playbook: %s does not appear to be a file" % playbook)

    b_playbook_dir = os.path.dirname(os.path.abspath(to_bytes(playbook, errors='surrogate_or_strict')))
    # load plugins from all playbooks in case they add callbacks/inventory/etc
    add_all_plugin_dirs(b_playbook_dir)
    
    b_playbook_dirs.append(b_playbook_dir)

set_collection_playbook_paths(b_playbook_dirs)

playbook_collection = get_collection_name_from_path(b_playbook_dirs[0])

if playbook_collection:
    display.warning("running playbook inside collection {0}".format(playbook_collection))
    AnsibleCollectionLoader().set_default_collection(playbook_collection)

# don't deal with privilege escalation or passwords when we don't need to
if not (context.CLIARGS['listhosts'] or context.CLIARGS['listtasks'] or
        context.CLIARGS['listtags'] or context.CLIARGS['syntax']):
    (sshpass, becomepass) = pb_cli.ask_passwords()
    passwords = {'conn_pass': sshpass, 'become_pass': becomepass}

# create base objects
loader, inventory, variable_manager = pb_cli._play_prereqs()

# Fix this when we rewrite inventory by making localhost a real host (and thus show up in list_hosts())
hosts = CLI.get_host_list(inventory, context.CLIARGS['subset'])

# flush fact cache if requplaybook_pathested
if context.CLIARGS['flush_cache']:
    pb_cli._flush_cache(inventory, variable_manager)

######################################################################

# Execute the playbook file
pbex = PlaybookExecutor(
    playbooks=context.CLIARGS['args'],
    inventory=inventory,
    variable_manager=variable_manager,
    loader=loader,
    passwords=passwords,
    )
# Override the default stdout callback with our custom callback
pbex._tqm._stdout_callback = results_callback
results = pbex.run()

# create base objects again (as PlaybookExecutor cleans them up)
loader, inventory, variable_manager = pb_cli._play_prereqs()

# Get list of hosts that the playbook successfully ran install tasks on
hosts = list(results_callback.package_info.keys())

if hosts:
    play_source = {
    "hosts": hosts,
    "gather_facts": True,
    "become": False,
    "tasks": [
        {
        "name": "package_check - get ubuntu version",
        "set_fact": {
            "ubuntu_version": "{{ ansible_lsb.get('description') | regex_findall('[0-9\\.]+') }}"
        }
        },
        {
        "name": "package_check - get ubuntu manifest packages",
        "shell": "set -o pipefail && wget 'http://releases.ubuntu.com/releases/{{ ansible_distribution_version }}/ubuntu-{{ ubuntu_version.0 }}-desktop-amd64.manifest' -q -O - | cut -f 1 | sort -u",
        "args": {
            "executable": "/bin/bash"
        },
        "register": "ubuntu_manifest_packages"
        },
        {
        "name": "package_check - get manually installed packages",
        "shell": "set -o pipefail && apt-mark showmanual | sort -u",
        "args": {
            "executable": "/bin/bash"
        },
        "register": "manual_installed_packages"
        },
        {
        "name": "package_check - get real manually installed packages",
        "set_fact": {
            "manual_packages": "{{ manual_installed_packages.stdout_lines | difference(ubuntu_manifest_packages.stdout_lines) }}"
        }
        }
    ]
    }

    # Get the cli options from the current context
    options = context.CLIARGS._store
    play_options = copy(options)
    # Ensure --check option is disabled
    if play_options.get('check') != False:
        play_options['check'] = False
    # Ensure all tags are cleared
    if play_options.get('tags'):
        play_options['tags'] = ()
    if play_options.get('skip_tags'):
        play_options['skip_tags'] = ()

    # Override the current context
    context.CLIARGS = ImmutableDict(**play_options)

    # Create play object, playbook objects use .load instead of init or new methods,
    # this will also automatically create the task objects from the info provided in play_source
    play = Play().load(play_source, variable_manager=variable_manager, loader=loader)

    # Run it - instantiate task queue manager, which takes care of forking and setting up all objects to iterate over host list and tasks
    tqm = None
    try:
        tqm = TaskQueueManager(
                inventory=inventory,
                variable_manager=variable_manager,
                loader=loader,
                passwords=passwords,
                stdout_callback=results_callback
            )
        result = tqm.run(play) # most interesting data for a play is actually sent to the callback's methods
    finally:
        # we always need to cleanup child procs and the structures we use to communicate with them
        if tqm is not None:
            tqm.cleanup()

        # Remove ansible tmpdir
        shutil.rmtree(C.DEFAULT_LOCAL_TMP, True)
else:
    print("Failed to create managed package list")

# Print banner title
results_callback._display.banner("UNMANAGED PACKAGE LIST")
# Print summary of results
for hostname, value in results_callback.package_info.items():
    if not results_callback.package_info[hostname]['failed']:
        print("SUCCESS => %s:" % stringc(hostname, "green"))
        for p in results_callback.package_info[hostname]['manual'] - results_callback.package_info[hostname]['managed']:
            print("  - %s" % p)
    else:
        print("FAILED => %s:" % stringc(hostname, "red"))

