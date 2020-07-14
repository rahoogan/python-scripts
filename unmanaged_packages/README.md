# Ansible Playbook: Check Unmanaged Packages

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