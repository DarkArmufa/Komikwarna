# Thema Cosmic V11

Install tema: `sudo bash INSTALL-THEME.sh`

Update tema: `sudo bash UPDATE-THEME.sh`

Installer web: `sudo bash START-INSTALLER.sh`, lalu isi License Key pada formulir.

Install, update dan repair wajib memasukkan license yang benar setiap kali. Kode kosong atau salah membatalkan proses sebelum perubahan. License tidak disimpan ke browser storage atau log. Untuk otomasi terminal gunakan `--license-stdin` dan kirim kode melalui stdin.

Paket mempertahankan fitur V10, termasuk pengumuman global dan User Egg Changer dengan saklar.

Fitur tambahan: Admin → Tampilan & Link → Background Panel dapat mengunggah JPG/PNG/WEBP/GIF sebagai background global panel, mengatur tingkat gelap 0–90%, dan menghapus background kapan saja.

Validasi license lokal memakai SHA-256. Tidak membutuhkan server aktivasi dan bukan sistem lisensi online anti-tamper; pemilik source GitHub dapat memodifikasi pemeriksaan. Jangan menaruh kode license asli di repository publik.

## V12 — Compact File Manager
- Daftar folder/file dibuat lebih rapat, terutama pada Android/mobile.
- Tinggi card, padding, dan jarak antar-file dikurangi agar background panel lebih terlihat.
- Tombol File Manager tetap memiliki area sentuh minimal sekitar 44px dan gaya comic tetap dipertahankan.
