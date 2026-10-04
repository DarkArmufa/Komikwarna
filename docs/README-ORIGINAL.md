> Dokumentasi paket sebelum revisi. Untuk fitur dan instalasi tema terbaru, gunakan ../README-ID.md. Screenshot lama yang tidak sesuai revisi telah dihapus.

# COMIC PTERO — Theme + Auto Installer

Paket desain original **BOLT HOST**: hitam/navy, kuning keemasan, hijau emerald, outline tebal, offset shadow, serta layout yang nyaman di HP. Nama hosting dapat diganti. Tidak menggunakan logo atau aset referensi pihak lain.

## Mulai dari sini

| Kebutuhan | Buka / jalankan |
|---|---|
| Lihat desain langsung | Ekstrak ZIP, lalu buka `PREVIEW.html` atau `web/index.html` |
| Coba wizard tanpa mengubah VPS | Buka Auto Installer pada preview |
| Pasang theme ke Panel yang sudah ada | `sudo bash INSTALL-THEME.sh` |
| Pasang Panel/Wings baru lewat browser | Jalankan `sudo bash START-INSTALLER.sh` sekali di VPS |
| Lepas theme | `sudo bash INSTALL-THEME.sh --remove` |

**Preview menggunakan data contoh.** File Manager, editor, folder, console, backup contoh, dan wizard demo dapat dicoba. Semua perubahan demo hanya berada di memori halaman dan hilang saat reload. Preview bukan pengganti backend game panel. Setelah theme dipasang ke Pterodactyl, fungsi file/server/permission yang sebenarnya tetap berasal dari Pterodactyl.

## Paket ini berisi

- `web/`: preview dashboard dan antarmuka wizard. Semua font/aset lokal, tanpa CDN.
- `theme/`: CSS dan enhancement JS untuk client panel dan AdminLTE, pemasang/pelepas theme.
- `installer/`: backend Python tanpa dependency pip, recipe instalasi nyata, serta integrasi PHP untuk admin/node.
- `docs/`: screenshot preview, detail operasional, dan sumber.
- `tests/`: tes validasi, autentikasi API, arsip, penghentian saat error, penyamaran rahasia, dan pemasangan theme.

## 1. Melihat preview dari HP

1. Ekstrak ZIP terlebih dahulu; jangan membuka HTML dari dalam arsip.
2. Buka `PREVIEW.html` pada browser yang mendukung file HTML lokal.
3. Jika penampil file Android tidak menjalankan JavaScript, jalankan preview di komputer dengan `bash START-INSTALLER.sh --preview`, kemudian buka alamat yang dicetak. Untuk akses HP gunakan SSH local forwarding sebagaimana di bawah.
4. Menu **Files**: create directory, upload file kecil, new file, edit, rename, delete, search, pilih file, masuk/keluar folder.
5. Menu **Auto Installer**: pilih mode → isi setup → Check System → Start Demo → Ya, Lanjutkan.

Batas upload pada preview 2 MB/file. File server produksi tetap memakai batas asli Pterodactyl. Statistik dan server contoh tidak mengklaim koneksi ke VPS.

## 2. Theme untuk Panel yang sudah ada

Target struktur: Pterodactyl **1.x** dengan template `resources/views/templates/wrapper.blade.php` dan `resources/views/layouts/admin.blade.php`; struktur diperiksa terhadap source **v1.15.1**. Tidak ditujukan untuk Blueprint/addon/theme pihak lain yang mengubah struktur ini.

Upload dan ekstrak folder `COMIC_PTERO` di VPS, masuk ke folder itu lalu jalankan:

```bash
sudo bash INSTALL-THEME.sh
```

Untuk folder Panel berbeda:

```bash
sudo PANEL_DIR=/lokasi/panel bash INSTALL-THEME.sh
```

Theme menambahkan aset ke Blade, membuat backup template di `storage/comic-theme-backups/`, lalu membersihkan view cache. Tidak perlu npm/yarn build. Komponen client dan admin mengikuti struktur native Pterodactyl; layout native tidak identik 1:1 dengan sidebar tambahan pada preview. Warna, tipografi, card, border, tombol, navbar, file row, dialog, dan status memakai bahasa visual yang sama.

Nama hosting asli mengikuti **Admin → Settings → General**. Tombol notifikasi tambahan menampilkan aktivitas akun jika endpoint client activity tersedia. Fitur inti tetap memakai React, permission, CSRF, dan endpoint bawaan Panel.

Pelepasan:

```bash
sudo bash INSTALL-THEME.sh --remove
```

Hanya blok aset milik theme yang dihapus, sehingga perubahan template lain dipertahankan. Aset dan backup template dibiarkan untuk pemulihan. Update resmi Pterodactyl dapat menimpa Blade; pasang kembali theme setelah update. Update melalui wizard akan memasang ulang theme otomatis.

## 3. Instalasi nyata dari browser

**Butuh satu bootstrap di VPS.** HTML/ZIP yang dibuka di HP tidak mempunyai hak root untuk menginstal VPS. Setelah launcher dan koneksi browser siap, semua langkah instalasi dijalankan dari tombol wizard.

Persiapan:

- VPS/VM Ubuntu **24.04 LTS**, systemd, amd64 atau arm64; akses root/sudo dan Python 3.12 bawaan Ubuntu.
- Minimal 1 GB RAM dan 5 GB kosong; alokasikan lebih untuk game dan backup. KVM disarankan.
- Untuk instalasi baru, gunakan VPS bersih. Folder Panel, database `panel`, dan instalasi Wings lama tidak ditimpa.
- Domain mengarah langsung ke IP VPS. Gunakan DNS-only saat penerbitan SSL; port TCP 80/443 terbuka di firewall provider.
- Pertahankan akses SSH dan siapkan aplikasi SSH yang mendukung **local port forwarding** di HP/laptop.

Langkah:

1. Upload ZIP melalui SFTP/file manager provider, ekstrak, dan masuk ke folder `COMIC_PTERO`.
2. Di terminal VPS jalankan satu kali:

   ```bash
   sudo bash START-INSTALLER.sh
   ```

3. Di aplikasi SSH buat **Local Port Forward**:

   | Field | Nilai |
   |---|---|
   | Local/listen address | `127.0.0.1` |
   | Local port | `8787` |
   | Destination host | `127.0.0.1` |
   | Destination port | `8787` |
   | SSH connection | VPS Anda |

   Jika memakai OpenSSH di laptop, koneksi tunnel setara dengan:

   ```bash
   ssh -L 8787:127.0.0.1:8787 root@IP_VPS
   ```

4. Buka **URL lengkap yang dicetak launcher**, termasuk `#token=...`, di browser perangkat yang menjalankan tunnel. Token hanya berlaku selama launcher aktif. Jangan bagikan URL ini.
5. Badge menjadi **VPS CONNECTED**. Pilih mode → Next → isi informasi → Check System → Install/Run → **YA, LANJUTKAN**.
6. Biarkan launcher dan SSH tetap hidup sampai selesai. Simpan login dari layar sukses. Tutup launcher setelah selesai.

Port installer **hanya listen di 127.0.0.1**. Jangan publish port 8787, jangan membuat reverse proxy publik untuk wizard root ini. Pterodactyl hasil instalasi tetap tersedia di domain HTTPS publik.

## 4. Mode yang tersedia

| Mode | Perilaku |
|---|---|
| Panel + Wings | Dependency, PHP 8.3, MariaDB, Redis, Panel, Docker/Wings, database, Nginx, firewall, SSL, admin, lokasi, node lokal, layanan, theme |
| Panel Only | Instalasi Panel lengkap tanpa Docker/Wings/node |
| Wings Only | Install Docker/Wings memakai konfigurasi dari node Panel yang sudah ada; tidak membuat Panel baru |
| Update | Backup → maintenance → Panel v1.15.1 → migrasi → Wings v1.13.3 bila ada → theme → pemeriksaan |
| Repair | Backup → permission/cache/theme → restart layanan → pemeriksaan; tidak reset password/APP_KEY |
| Backup | Arsip Panel, DB, .env/APP_KEY, Nginx, config Wings. Layanan panel berhenti sementara untuk konsistensi |
| Restore | Verifikasi hash → backup pengaman → pulihkan arsip terpilih pada VPS asal → pemeriksaan |

Update/Repair/Backup/Restore hanya untuk instalasi yang dibuat paket ini. Tidak menebak kredensial dan konfigurasi instalasi pihak lain. Update ditahan pada versi rilis di dalam paket, **bukan update “latest” tanpa batas**. Downgrade ditolak. Versi baru dapat ditambahkan dengan memperbarui versi/hash setelah review kompatibilitas.

**Wings Only:** tempel YAML/JSON dari **Admin → Nodes → Configuration**. Bila memakai HTTPS, sertifikat yang dirujuk config harus sudah tersedia di VPS Wings. Mode ini tidak meminta domain/credential Panel atau membuat sertifikat baru. HTTP diperbolehkan jika konfigurasi node memang HTTP. Jangan tempel perintah shell Generate Token; tempel konfigurasi lengkap.

**Panel + Wings:** node memakai domain Panel yang sama dengan port HTTPS **8443**, SFTP **2022**, direktori data `/var/lib/pterodactyl/volumes`. Sertifikat dibagikan dengan Panel dan Wings direstart otomatis sesudah renew SSL. Lokasi/node dibuat otomatis; Anda tetap perlu membuat allocation, memilih egg, lalu membuat game server dari halaman Admin. Installer tidak membuat game server contoh.

## 5. Setelah sukses

- OPEN PANEL → login pengguna.
- OPEN ADMIN PANEL → administrasi Pterodactyl.
- COPY LOGIN → menyalin username/password sesi saat ini; password tidak disimpan ke localStorage atau log. Setelah reload, gunakan password yang sudah Anda simpan.
- VIEW INSTALL LOG → unduh log tersaring yang ditampilkan.
- Ubah brand di Admin → Settings.
- Atur SMTP di Admin → Settings agar email/reset password benar-benar terkirim. Default awal memakai mailer `log`.
- Atur allocation port dan firewall provider untuk game yang Anda pilih. Installer hanya membuka port layanan Panel/Wings dan mempertahankan port SSH yang terdeteksi; **tidak** membuka semua port game.

## 6. Batas pengujian

Tes otomatis mencakup validator, otorisasi endpoint, Host/Origin, traversal arsip, penyamaran rahasia, failure-stop, integrity backup, dan pemasangan/pelepasan theme. Preview diperiksa pada berbagai lebar layar. **Instalasi end-to-end pada VPS sungguhan belum dijalankan dalam pembuatan paket ini.** Uji dahulu pada VPS kosong/snapshot sebelum memakai layanan produksi. Kompatibilitas theme lintas seluruh versi/addon Pterodactyl belum dijamin.

Lihat `docs/OPERASIONAL.md` untuk backup, kegagalan, dan pemulihan.
