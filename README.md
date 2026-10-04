# Thema Cosmic V12 — Comic Pterodactyl Theme

Theme Pterodactyl bergaya comic dengan kombinasi warna hitam, kuning, dan hijau. Paket ini sudah dilengkapi installer terminal, updater, installer web, pengumuman global, User Egg Changer, Background Panel, dan File Manager yang dibuat lebih compact terutama untuk Android/mobile.

---

## Fitur Utama

- Tampilan comic gaming hitam / kuning / hijau.
- Responsive untuk desktop dan Android/mobile.
- Pengumuman global panel.
- User Egg Changer dengan saklar.
- Admin → Tampilan & Link → Background Panel.
- Upload background JPG / PNG / WEBP / GIF.
- Pengaturan tingkat gelap background 0–90%.
- Background dapat dihapus kapan saja dari menu Admin.
- Compact File Manager agar daftar folder/file lebih rapat dan background tetap terlihat.
- Installer terminal.
- Update theme dari terminal.
- Installer web.
- Pemeriksaan license sebelum install / update / repair.

---

# 1. Tutorial Upload Project ke GitHub

Contoh repository yang digunakan:

```text
https://github.com/DarkArmufa/Komikwarna.git
```

> Jalankan perintah berikut **satu per satu** dari folder project/theme yang ingin di-upload.

### Step 1 — Install Git

```bash
apt update -y
```

Lalu:

```bash
apt install git -y
```

### Step 2 — Masuk ke folder project

Contoh jika project berada di `/root/Komikwarna`:

```bash
cd /root/Komikwarna
```

Pastikan file project sudah ada:

```bash
ls -la
```

### Step 3 — Inisialisasi Git

```bash
git init
```

### Step 4 — Atur nama branch menjadi `main`

```bash
git branch -M main
```

### Step 5 — Tambahkan semua file

```bash
git add .
```

### Step 6 — Buat commit pertama

```bash
git commit -m "Initial upload Thema Cosmic"
```

Jika Git meminta nama dan email, atur dulu:

```bash
git config --global user.name "DarkArmufa"
```

Lalu:

```bash
git config --global user.email "EMAIL_GITHUB_KAMU"
```

Setelah itu ulangi commit:

```bash
git commit -m "Initial upload Thema Cosmic"
```

### Step 7 — Hubungkan ke repository GitHub

```bash
git remote add origin https://github.com/DarkArmufa/Komikwarna.git
```

Cek remote:

```bash
git remote -v
```

Jika `origin` sudah pernah dibuat, gunakan:

```bash
git remote set-url origin https://github.com/DarkArmufa/Komikwarna.git
```

### Step 8 — Upload ke GitHub

```bash
git push -u origin main
```

GitHub dapat meminta login/autentikasi. Gunakan metode autentikasi GitHub yang aktif pada akun kamu. Jangan menaruh password, token, license key asli, atau secret langsung di source/repository publik.

---

# 2. Tutorial Update Source yang Sudah Ada di GitHub

Setelah kamu mengubah file di VPS atau komputer, masuk ke folder repository:

```bash
cd /root/Komikwarna
```

Cek perubahan:

```bash
git status
```

Tambahkan semua perubahan:

```bash
git add .
```

Buat commit:

```bash
git commit -m "Update Thema Cosmic"
```

Upload perubahan:

```bash
git push origin main
```

Selesai. File terbaru akan masuk ke repository GitHub.

---

# 3. Tutorial Install Theme dari GitHub

Masuk ke VPS Pterodactyl sebagai `root`, lalu jalankan perintah berikut **satu per satu**.

### Step 1 — Update package VPS

```bash
apt update -y
```

### Step 2 — Install Git

```bash
apt install git -y
```

### Step 3 — Masuk ke folder root

```bash
cd /root
```

### Step 4 — Clone repository

```bash
git clone https://github.com/DarkArmufa/Komikwarna.git
```

### Step 5 — Masuk ke folder theme

```bash
cd Komikwarna
```

### Step 6 — Berikan permission ke file installer

```bash
chmod +x *.sh
```

### Step 7 — Jalankan installer

```bash
bash INSTALL-THEME.sh
```

Ikuti instruksi yang muncul di terminal dan masukkan **License Key** ketika diminta.

---

# 4. Versi Install Cepat

Jika ingin copy-paste sekaligus:

```bash
apt update -y
apt install git -y

cd /root
git clone https://github.com/DarkArmufa/Komikwarna.git
cd Komikwarna

chmod +x *.sh
bash INSTALL-THEME.sh
```

---

# 5. Tutorial Update Theme dari GitHub

Jika sebelumnya theme sudah pernah di-clone:

### Step 1 — Masuk ke folder repository

```bash
cd /root/Komikwarna
```

### Step 2 — Ambil source terbaru

```bash
git pull
```

### Step 3 — Pastikan file `.sh` dapat dijalankan

```bash
chmod +x *.sh
```

### Step 4 — Jalankan updater

```bash
bash UPDATE-THEME.sh
```

Masukkan License Key jika diminta.

---

# 6. Menjalankan Installer Web

Masuk ke folder repository:

```bash
cd /root/Komikwarna
```

Berikan permission:

```bash
chmod +x *.sh
```

Jalankan installer web:

```bash
bash START-INSTALLER.sh
```

Setelah aktif, buka alamat installer yang ditampilkan di terminal, lalu isi License Key pada form installer.

---

# 7. Uninstall / Remove Theme

Masuk ke folder repository:

```bash
cd /root/Komikwarna
```

Lalu jalankan:

```bash
bash INSTALL-THEME.sh --remove
```

---

# 8. Background Panel

Menu:

```text
Admin → Tampilan & Link → Background Panel
```

Fitur Background Panel:

- Upload JPG / PNG / WEBP / GIF.
- Background diterapkan secara global pada panel.
- Tampilan background menggunakan mode cover dan posisi tengah.
- Tingkat gelap dapat diatur 0–90%.
- Preview background aktif tersedia di menu Admin.
- Background dapat diganti atau dihapus kapan saja.

---

# 9. Compact File Manager

Pada versi V12:

- Daftar folder/file dibuat lebih rapat, terutama pada Android/mobile.
- Tinggi card diperkecil.
- Padding isi diperkecil.
- Jarak antar file/folder dikurangi.
- Tombol aksi tetap nyaman disentuh.
- Outline dan shadow comic tetap dipertahankan.
- Background panel menjadi lebih terlihat di sela daftar file.

---

# 10. Catatan License

Install, update, dan repair wajib memasukkan license yang benar. License kosong atau salah akan membatalkan proses sebelum perubahan diterapkan.

Untuk otomasi terminal tersedia mode:

```bash
--license-stdin
```

Validasi license lokal menggunakan SHA-256. Ini bukan sistem lisensi online anti-tamper karena pemilik source masih dapat memodifikasi source code.

**Penting:** jangan upload License Key asli, token GitHub, password, API key, atau secret lainnya ke repository publik.

---

## Repository

```text
https://github.com/DarkArmufa/Komikwarna.git
```
