#!/usr/bin/env python3

import argparse
import os
import shutil
import subprocess
import sys
import re
import getpass

def is_root():
    return os.geteuid() == 0

def check_service_exists(service_name):
    result = subprocess.run(["which", service_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.returncode == 0

def manage_nginx(action):
    if action == "start":
        print("Starting Nginx...")
        subprocess.run(["systemctl", "start", "nginx"])
    elif action == "stop":
        print("Stopping Nginx...")
        subprocess.run(["systemctl", "stop", "nginx"])
    elif action == "restart":
        print("Restarting Nginx...")
        subprocess.run(["systemctl", "restart", "nginx"])
    elif action == "reload":
        print("Reloading Nginx...")
        subprocess.run(["systemctl", "reload", "nginx"])
    elif action == "status":
        print("Checking Nginx configuration...")
        subprocess.run(["nginx", "-t"])

def edit_config(file_path):
    editor = os.getenv('EDITOR', 'nano')
    subprocess.run([editor, file_path])

def add_config_manual(file_name, ssl, port, domains, root_dir, php_sock, routing_file=None):
    available_path = "/etc/nginx/sites-available/" + file_name
    enabled_path = "/etc/nginx/sites-enabled/" + file_name

    if os.path.exists(available_path):
        print(f"Cannot create config file.")
        print(f"Config file '{available_path}' already exists.")
        return

    if routing_file:
        routing = f"try_files $uri $uri/ /{routing_file}$is_args$args;"
    else:
        routing = "try_files $uri $uri/ =404;"

    config_content = f"""
server {{
    listen {port};
    listen [::]:{port};

    root {root_dir};

    index index.php index.html index.htm index.nginx-debian.html;

    access_log {root_dir}/logs/access.log;
    error_log {root_dir}/logs/error.log;

    server_name {' '.join(domains)};

    location / {{
        {routing}
    }}

    location ~ \.php$ {{
        include snippets/fastcgi-php.conf;
        fastcgi_pass unix:/run/php/{php_sock};
    }}

    location ~ /\.ht {{
        deny all;
    }}
}}
"""

    with open(available_path, 'w') as file:
        file.write(config_content)

    if not os.path.exists(enabled_path):
        os.symlink(available_path, enabled_path)

    print(f"Configuration for {file_name} added and enabled.")
    print(f"Run `cpfn restart` to restart nginx service.")

    if ssl:
        run_certbot(domains)

def add_config_file(file_name):
    current_path = os.getcwd()
    source_file = f"{current_path}/{file_name}"
    available_path = "/etc/nginx/sites-available/" + os.path.basename(file_name)
    enabled_path = "/etc/nginx/sites-enabled/" + os.path.basename(file_name)


    try:
        shutil.copy(source_file, available_path)
    except FileNotFoundError:
        print(f"File {source_file} not found.")
        return
    except FileExistsError:
        print(f"File {available_path} already exists.")
        return

    print(f"Copied {source_file} to {available_path}")

    if not os.path.exists(enabled_path):
        os.symlink(available_path, enabled_path)

    print(f"Configuration for {file_name} added and enabled.")

def run_certbot(domains):
    domain_args = []
    for domain in domains:
        domain_args.extend(["-d", domain])
    certbot_command = ["certbot", "--nginx"] + domain_args
    print(f"Running: {' '.join(certbot_command)}")
    subprocess.run(certbot_command)

def list_sites():
    available_path = "/etc/nginx/sites-available"
    enabled_path = "/etc/nginx/sites-enabled"

    available_sites = os.listdir(available_path)
    enabled_sites = os.listdir(enabled_path)

    print("Available sites:")
    for site in available_sites:
        print(f"  - {site}")

    print("\nEnabled sites:")
    for site in enabled_sites:
        print(f"  - {site}")

def delete_site(file_name):
    available_path = "/etc/nginx/sites-available/" + file_name
    enabled_path = "/etc/nginx/sites-enabled/" + file_name

    if os.path.exists(enabled_path):
        os.remove(enabled_path)

    if os.path.exists(available_path):
        os.remove(available_path)

    print(f"Configuration for {file_name} deleted.")

def enable_site(file_name):
    available_path = "/etc/nginx/sites-available/" + file_name
    enabled_path = "/etc/nginx/sites-enabled/" + file_name

    if os.path.exists(available_path) and not os.path.exists(enabled_path):
        os.symlink(available_path, enabled_path)
        print(f"Site {file_name} enabled.")
    else:
        print(f"Site {file_name} is already enabled or does not exist.")

def disable_site(file_name):
    enabled_path = "/etc/nginx/sites-enabled/" + file_name

    if os.path.exists(enabled_path):
        os.remove(enabled_path)
        print(f"Site {file_name} disabled.")
    else:
        print(f"Site {file_name} is not enabled or does not exist.")

def remove_protocol(url):
    domain_match = re.match(r'^(?:http[s]?://)?([^/]+)', url)
    if domain_match:
        return domain_match.group(1)
    return url

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

def main():
    parser = argparse.ArgumentParser(description="Control Panel For Nginx Server")
    parser.add_argument("action", choices=["start", "stop", "restart", "reload", "edit", "add", "list", "delete", "enable", "disable", "status"], help="Action to perform.")
    parser.add_argument("--file", help="Configuration file to edit (for edit action), name to add (for add action), or name to delete/enable/disable (for delete/enable/disable action)")
    parser.add_argument("--ssl", action='store_true', help="Enable SSL for the site")
    parser.add_argument("--port", type=int, default=80, help="Port to listen on")
    parser.add_argument("--domain", nargs='+', help="Domain(s) for the site, please do not use protocol (e.g., example.com)")
    parser.add_argument("--root-dir", help="Root directory for the site")
    parser.add_argument("--create-user", action='store_true', help="Add new user before creating the site")
    parser.add_argument("--php-sock", help="PHP socket to use")
    parser.add_argument("--routing", help="Custom routing file for the site")
    args = parser.parse_args()

    if not is_root():
        print("This script must be run as root!")
        print("Use -h for help.")
        sys.exit(1)

    if args.create_user:
        add_user()

    if not check_service_exists("nginx"):
        print("Nginx service does not exist. Using systemctl.")
        manage_nginx(args.action)
    else:
        if args.action in ["start", "stop", "restart", "reload", "status"]:
            manage_nginx(args.action)
        elif args.action == "edit":
            if not args.file:
                print("Please provide the file to edit using --file")
                print("Use -h for help.")
                sys.exit(1)
            file_path = f"/etc/nginx/sites-available/{args.file}"
            if not os.path.exists(file_path):
                print(f"File {file_path} does not exist.")
                sys.exit(1)
            edit_config(file_path)
        elif args.action == "add":
            if args.file:
                add_config_file(args.file)
            else:
                if not args.domain or not args.root_dir or not args.php_sock:
                    print("Please provide all required options: domains, root directory, and PHP socket")
                    print("Or use --file option to add a configuration file.")
                    print("Use -h for help.")
                    sys.exit(1)
                domain = remove_protocol(' '.join(args.domain))
                add_config_manual(f'{domain}.conf', args.ssl, args.port, args.domain, args.root_dir, args.php_sock, args.routing)
        elif args.action == "list":
            list_sites()
        elif args.action == "delete":
            if not args.file:
                print("Please provide the file name to delete using --file")
                print("Use -h for help.")
                sys.exit(1)
            delete_site(args.file)
        elif args.action == "enable":
            if not args.file:
                print("Please provide the file name to enable using --file")
                print("Use -h for help.")
                sys.exit(1)
            enable_site(args.file)
        elif args.action == "disable":
            if not args.file:
                print("Please provide the file name to disable using --file")
                print("Use -h for help.")
                sys.exit(1)
            disable_site(args.file)

if __name__ == "__main__":
    main()
