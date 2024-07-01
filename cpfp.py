#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import re
import getpass
import shutil

def is_root():
    return os.geteuid() == 0

def manage_php(action, version):
    if action == "start":
        print(f"Starting PHP-FPM {version}...")
        subprocess.run(["systemctl", "start", f"php{version}-fpm"])
    elif action == "stop":
        print(f"Stopping PHP-FPM {version}...")
        subprocess.run(["systemctl", "stop", f"php{version}-fpm"])
    elif action == "restart":
        print(f"Restarting PHP-FPM {version}...")
        subprocess.run(["systemctl", "restart", f"php{version}-fpm"])
    elif action == "reload":
        print(f"Reloading PHP-FPM {version}...")
        subprocess.run(["systemctl", "reload", f"php{version}-fpm"])
    elif action == "status":
        print(f"Checking PHP-FPM {version} configuration...")
        subprocess.run([f"php-fpm{version}", "-t"])

def edit_config(file_path):
    editor = os.getenv('EDITOR', 'nano')
    subprocess.run([editor, file_path])

def check_php_ver():
    result = subprocess.run(["php", "-v"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    version = re.search(r'PHP (\d+\.\d+)', result.stdout.decode())
    if version:
        return version.group(1)
    return "7.4"  # Default to PHP 7.4 if version cannot be determined

def add_config_manual(file_name, domain, root_dir, user):
    if not file_name:
        print("Please provide a file name.")
        print("Use -h for help.")
        sys.exit(1)

    ver = check_php_ver()
    available_path = f"/etc/php/{ver}/fpm/pool.d/" + file_name

    if os.path.exists(available_path):
        print(f"Cannot create config file.")
        print(f"Config file '{available_path}' already exists.")
        return

    config_content = f"""
[{domain}]
user = {user}
group = {user}
listen = /run/php/php{ver}-fpm-{domain}.sock
listen.owner = www-data
listen.group = www-data
pm = dynamic
pm.max_children = 50
pm.start_servers = 5
pm.min_spare_servers = 5
pm.max_spare_servers = 35
pm.max_requests = 500
chdir = {root_dir}

; Adjust php.ini settings for this pool
php_admin_value[error_log] = /var/log/php{ver}-fpm-{domain}.log
"""

    with open(available_path, 'w') as file:
        file.write(config_content)

    print(f"Configuration for {file_name} added.")
    print(f"Run 'systemctl restart php{ver}-fpm' to restart PHP-FPM service.")

def add_user():
    username = input("Please type username for the new user: ")
    password = getpass.getpass("Password: ")
    repassword = getpass.getpass("Retype password: ")
    if password == repassword:
        subprocess.run(["useradd", "-m", "-s", "/bin/bash", username])
        subprocess.run(["chpasswd"], input=f"{username}:{password}", text=True)
    else:
        print("Passwords do not match.")
        sys.exit(1)

def list_configs():
    php_ver = check_php_ver()
    config_path = f"/etc/php/{php_ver}/fpm/pool.d/"

    config_files = os.listdir(config_path)

    print("PHP-FPM pool configurations:")
    for config in config_files:
        print(f"  - {config}")

def delete_config(file_name):
    php_ver = check_php_ver()
    config_path = f"/etc/php/{php_ver}/fpm/pool.d/" + file_name

    if os.path.exists(config_path):
        os.remove(config_path)
        print(f"Configuration for {file_name} deleted.")
    else:
        print(f"Configuration file {file_name} does not exist.")

def add_config_file(file_name):
    current_path = os.getcwd()
    php_ver = check_php_ver()
    source_file = f"{current_path}/{file_name}"
    available_path = f"/etc/php/{php_ver}/fpm/pool.d/"

    try:
        shutil.copy(source_file, available_path)
    except FileNotFoundError:
        print(f"File {source_file} not found.")
        return
    except FileExistsError:
        print(f"File {available_path} already exists.")
        return

    print(f"Configuration for {file_name} added.")

def main():
    parser = argparse.ArgumentParser(description="Control Panel For PHP-FPM Server")
    parser.add_argument("action", choices=["start", "stop", "restart", "reload", "add", "list", "delete", "status"], help="Action to perform.")
    parser.add_argument("--file", help="Configuration file name to add (for add action), or name to delete (for delete action)")
    parser.add_argument("--domain", help="Domain(s) for the site, please do not use protocol (e.g., example.com)")
    parser.add_argument("--user", help="The user to pointing php server (required)")
    parser.add_argument("--adduser", action="store_true", help="Create user before create the site")
    parser.add_argument("--root-dir", help="Root directory for the site")
    parser.add_argument("--php-version", help="PHP version to manage (e.g., 7.4, 8.0)", default=check_php_ver())
    args = parser.parse_args()

    if not is_root():
        print("This script must be run as root!")
        sys.exit(1)

    if args.adduser:
        add_user()

    if args.action in ["start", "stop", "restart", "reload", "status"]:
        manage_php(args.action, args.php_version)
    elif args.action == "add":
        if args.file:
            add_config_file(args.file)
        else:
            if not args.domain or not args.root_dir or not args.user:
                print("Please provide all required options: domain, root directory, and user.")
                sys.exit(1)
            else:
                domain = re.sub(r'^(?:http[s]?://)?([^/]+)', r'\1', args.domain)
                add_config_manual(f'{domain}.conf', domain, args.root_dir, args.user)
    elif args.action == "list":
        list_configs()
    elif args.action == "delete":
        if not args.file:
            print("Please provide the file name to delete using --file")
            sys.exit(1)
        delete_config(args.file)

if __name__ == "__main__":
    main()
