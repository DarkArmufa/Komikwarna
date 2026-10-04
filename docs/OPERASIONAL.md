# Operasional, backup, dan pemulihan

## Apa yang diubah oleh installer nyata

Instalasi Panel baru memakai `/var/www/pterodactyl`, database `panel`, user MariaDB `pterodactyl@127.0.0.1`, PHP 8.3, MariaDB, Redis, Nginx, Composer, cron, dan queue `pteroq`. Wings memakai `/usr/local/bin/wings`, `/etc/pterodactyl/config.yml`, systemd `wings`, dan Docker dari repository Ubuntu.

Konfigurasi baru bernama `comic-pterodactyl.conf`; site Nginx lain tidak dihapus. Konflik domain/port pada VPS yang telah berisi layanan tetap perlu ditangani administrator. Launcher menolak folder Panel/instalasi Wings lama pada fresh install, OS selain Ubuntu 24.04, arsitektur lain, DNS yang belum mengarah ke VPS, serta virtualisasi Wings yang tidak didukung.

“Update system” pada checklist berarti memperbarui **indeks paket apt**, bukan menjalankan upgrade penuh OS atau reboot. Installer tidak me-reboot server.

## Password dan akses

- Password acak memakai Web Crypto. Password tetap di memori tab; sesi launcher token disimpan di sessionStorage tab, tidak localStorage.
- Data sensitif dikirim hanya melalui loopback di dalam SSH tunnel. API memakai bearer token acak, pemeriksaan Host dan Origin, JSON-only, batas request, dan penguncian pekerjaan tunggal.
- Root launcher tidak dapat diakses langsung dari internet karena bind ke `127.0.0.1`.
- Perintah menggunakan daftar argumen tanpa shell. Credential admin/database tidak ditempatkan pada command line. Bridge PHP menerima JSON melalui stdin.
- `.env` dimiliki webserver dengan mode 0640. Konfigurasi Wings, metadata installer, dan backup dilindungi untuk root.
- App key dibuat hanya pada instalasi Panel baru. Update, repair, dan restore tidak membuat APP_KEY baru.
- Log aplikasi tersaring; UI menyimpan maksimal 1.500 baris log terakhir. Error yang bisa memuat credential dari bridge/database tidak dicetak mentah.
- Simpan password admin dan backup `.env`/APP_KEY secara terpisah. Layar COPY LOGIN tidak dapat memulihkan password setelah refresh.

## SSL dan firewall

Domain harus mengarah langsung ke IPv4 publik/lokal VPS yang terdeteksi. IPv4 NAT dikenali melalui layanan ipify jika dapat dijangkau. Jika memakai AAAA, pastikan IPv6 juga menuju VPS yang sama; bila tidak, hapus/perbaiki AAAA sebelum penerbitan sertifikat. Certificate validation tetap dilakukan Let's Encrypt, sehingga Check System bukan jaminan sertifikat akan terbit.

Paket menggunakan certbot Nginx plugin dan timer renew systemd. Hook reload Nginx dan restart Wings setelah sertifikat diperbarui. Penerbitan membutuhkan persetujuan terms Let's Encrypt dari form.

UFW mempertahankan aturan lama, menambahkan port SSH yang terdeteksi, lalu port layanan web/Wings. Port SSH dideteksi dari `sshd -T` serta `SSH_CONNECTION`; jika tidak dapat dideteksi, proses dihentikan sebelum setup. Port provider/security group harus diatur di penyedia VPS. Tidak membuka port game secara otomatis karena allocation belum dibuat. Docker dapat mengelola firewall sendiri; gunakan firewall provider untuk pembatasan port game yang ketat.

## Backup yang disertakan

Backup lokal ada di `/var/lib/comic-ptero-installer/backups`, mode direktori 0700 dan arsip 0600. File `.sha256` mendeteksi korupsi/perubahan; bukan tanda tangan yang melindungi dari penyerang yang sudah punya akses root.

Isi arsip:

- Seluruh file Panel, `.env` dan APP_KEY.
- Dump database `panel`, termasuk trigger/routine.
- Konfigurasi Nginx milik installer.
- Konfigurasi Wings jika tersedia.
- Metadata domain/versi/tipe instalasi.

**Tidak termasuk** volume game, image Docker, database eksternal milik game, sertifikat Let's Encrypt, aturan firewall, ataupun semua konfigurasi OS. Backup ini untuk pemulihan Panel pada VPS asal, bukan bare-metal migration. Untuk backup game gunakan fitur Backups native Panel atau backup volume terpisah. Unduh arsip ke perangkat lain melalui SFTP root, jangan letakkan di folder publik.

Backup menghentikan queue dan membuat Panel maintenance sementara agar konsisten. Game container tidak dihentikan, karena data game memang tidak termasuk. UI Restore hanya menerima backup lokal yang dibuat wizard dan lolos checksum, tidak menerima arsip upload sembarang.

## Restore dan kegagalan

Restore membuat backup pengaman terlebih dahulu. Domain dan tipe node harus sama dengan metadata arsip. File Panel lama dipindah ke `/var/www/pterodactyl-before-restore-<id>` dan dipertahankan; database `panel` dikosongkan/dibuat ulang dan dump dipulihkan. Sertifikat dan akun database pada VPS asal harus masih tersedia. Folder lama boleh dihapus manual setelah pemulihan benar-benar diverifikasi untuk menghemat disk.

Bila instalasi berhenti:

1. Jangan menganggap progress 100% atau warna hijau sebelum layar sukses; status error menghentikan langkah berikutnya.
2. Lihat log tersaring untuk langkah yang gagal: DNS, port 80/443, apt lock, koneksi internet, RAM/disk, atau konfigurasi Wings.
3. Pekerjaan yang sudah selesai tidak otomatis diulang. Fresh install parsial tidak dihapus otomatis karena bisa berisi data berharga.
4. Untuk fresh VPS gagal sebelum selesai, cara sederhana adalah memperbaiki DNS/firewall lalu kembali ke snapshot bersih dan mengulang. Jika ingin menyelamatkan instalasi parsial, minta admin meninjau direktori, database, dan log layanan; tombol Repair hanya menerima metadata instalasi yang sudah selesai.
5. Update yang gagal dapat meninggalkan Panel dalam maintenance agar aplikasi rusak tidak dipakai pengguna. Gunakan Restore dari backup pengaman melalui wizard; bila MariaDB/queue gagal, admin perlu memulihkan layanan dahulu.
6. Jika launcher putus, jalankan launcher lagi dan gunakan URL token baru. Status pekerjaan lama menjadi **interrupted**, tidak diklaim sukses. Tidak ada resume otomatis.

Tidak ada klaim recovery transaksi penuh untuk perubahan paket, database, dan sistem operasi. Backup, snapshot VPS, dan verifikasi hasil tetap diperlukan untuk layanan produksi.
