# Control Panel untuk Nginx dan PHP-FPM

Skrip ini menyediakan panel kontrol berbasis CLI untuk mengelola konfigurasi server Nginx dan PHP-FPM. Skrip ini memungkinkan Anda untuk memulai, menghentikan, memulai ulang, memuat ulang layanan, serta menambah, mengedit, menghapus, mengaktifkan, dan menonaktifkan konfigurasi situs.

## Fitur

- Memulai, menghentikan, memulai ulang, dan memuat ulang layanan Nginx.
- Memeriksa status konfigurasi Nginx.
- Menambah konfigurasi situs baru secara manual atau dari file.
- Mengedit konfigurasi situs yang ada.
- Menghapus konfigurasi situs.
- Mengaktifkan dan menonaktifkan konfigurasi situs.
- Menambah pengguna baru untuk situs.
- Mendukung konfigurasi SSL menggunakan Certbot.

## Persyaratan

- Python 3.x
- Nginx
- PHP-FPM
- Certbot (untuk SSL)

## Instalasi

1. Clone repositori ini:
   ```bash
   git clone https://github.com/username/repo.git
   cd repo

2. chmod +x install.sh
3. ./install.sh
