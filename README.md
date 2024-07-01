  Control Panel for Nginx and PHP-FPM

Control Panel for Nginx and PHP-FPM
===================================

This script provides a CLI-based control panel for managing Nginx and PHP-FPM server configurations. It allows you to start, stop, restart, reload services, as well as add, edit, delete, enable, and disable site configurations.

Features
--------

*   Start, stop, restart, and reload the Nginx service.
*   Check Nginx configuration status.
*   Add new site configurations manually or from a file.
*   Edit existing site configurations.
*   Delete site configurations.
*   Enable and disable site configurations.
*   Add new users for the site.
*   Support SSL configuration using Certbot.

Requirements
------------

*   Python 3.x
*   Nginx
*   PHP-FPM
*   Certbot (for SSL)

Installation
------------

1.  Clone this repository:
    
        git clone https://github.com/username/repo.git
        cd repo
    
2.  Ensure you run this script as root:
    
        sudo cpfn
    

Usage
-----

Run the script with the appropriate arguments to perform the desired action. Below are basic usage examples:

### Start, Stop, Restart, and Reload Nginx

    sudo cpfn start
    sudo cpfn stop
    sudo cpfn restart
    sudo cpfn reload
    sudo cpfn status

### Add Site Configuration

Adding a new site configuration manually:

    sudo cpfn add --domain example.com --root-dir /var/www/example --php-sock php7.4-fpm.sock --ssl

Adding a site configuration from a file:

    sudo cpfn add --file mysite.conf

### Edit Site Configuration

    sudo cpfn edit --file mysite.conf

### Delete Site Configuration

    sudo cpfn delete --file mysite.conf

### Enable or Disable Site Configuration

Enable a site:

    sudo cpfn enable --file mysite.conf

Disable a site:

    sudo cpfn disable --file mysite.conf

### Add New User

    sudo cpfn add --create-user

### List Sites

Display a list of available and enabled sites:

    sudo cpfn list

Contributing
------------

If you would like to contribute to this project, please fork this repository and submit a pull request with your changes.

License
-------

This project is licensed under the MIT License. See the `LICENSE` file for more information.
