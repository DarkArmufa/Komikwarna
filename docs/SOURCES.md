# Sumber dan kompatibilitas

Implementasi mengacu pada dokumentasi serta source resmi; diperiksa saat paket dibuat. Tidak membundel distribusi inti Pterodactyl. Unduhan instalasi berlangsung dari GitHub resmi dan dibandingkan dengan SHA-256 yang dikunci dalam `installer/deploy.py`.

- Getting started: https://pterodactyl.io/panel/1.0/getting_started.html
- Web server: https://pterodactyl.io/panel/1.0/webserver_configuration.html
- Wings: https://pterodactyl.io/wings/1.0/installing.html
- Panel update: https://pterodactyl.io/panel/1.0/updating.html
- Panel release: https://github.com/pterodactyl/panel/releases/tag/v1.15.1
- Wings release: https://github.com/pterodactyl/wings/releases/tag/v1.13.3
- Official Panel source: https://github.com/pterodactyl/panel/tree/v1.15.1
- Font Inter: https://github.com/google/fonts/tree/main/ofl/inter
- Font Barlow Condensed: https://github.com/google/fonts/tree/main/ofl/barlowcondensed
- Let's Encrypt terms: https://letsencrypt.org/repository/

Panel version: **v1.15.1**. SHA-256 panel.tar.gz: `62c88c035b3e0f3c3ddd06bc3ef12249d087af0e765f49878b6327a066ed860b`.

Wings version: **v1.13.3**. SHA-256 amd64: `010d894a895fe4f914e3f1c1e75fb2fda4ebe50cc249e7e456887ea5b422c8fa`. SHA-256 arm64: `8e3114cb0ee5ec617831d5ec35097b1096c6c972f05ef80c683a9f396d0fe9f5`.

Brand BOLT HOST adalah nama contoh dalam desain ini. Pterodactyl adalah proyek pihak ketiga dengan lisensinya sendiri. Paket ini bukan produk resmi atau afiliasi Pterodactyl. Font dibundel beserta lisensi SIL OFL masing-masing.

## Referensi integrasi revisi menu kanan

Source resmi yang diperiksa selama revisi:
- https://github.com/pterodactyl/panel/blob/v1.12.0/resources/scripts/components/NavigationBar.tsx
- https://github.com/pterodactyl/panel/blob/v1.12.0/resources/scripts/components/dashboard/search/SearchContainer.tsx
- https://github.com/pterodactyl/panel/blob/v1.12.0/app/Repositories/Eloquent/SettingsRepository.php
- https://github.com/pterodactyl/panel/blob/v1.12.0/resources/views/layouts/admin.blade.php
- https://github.com/pterodactyl/panel/blob/v1.12.0/routes/admin.php
- https://github.com/pterodactyl/panel/blob/v1.15.1/app/Providers/RouteServiceProvider.php

## Pemeriksaan Android

- https://github.com/pterodactyl/panel/blob/v1.15.1/public/themes/pterodactyl/vendor/adminlte/admin.min.css
- https://github.com/pterodactyl/panel/blob/v1.15.1/public/themes/pterodactyl/vendor/bootstrap/bootstrap.min.css
- https://github.com/pterodactyl/panel/blob/v1.15.1/resources/scripts/components/dashboard/ServerRow.tsx
- https://github.com/pterodactyl/panel/blob/v1.15.1/resources/scripts/components/NavigationBar.tsx
