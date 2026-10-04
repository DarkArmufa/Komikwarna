# Tutorial Install / Update

```bash
unzip Thema_Cosmic_V10_Egg_Changer_Saklar_Android.zip -d cosmic-v10
cd comic-v7
sudo bash UPDATE-THEME.sh
```

## Setting Egg Changer User

1. Login menggunakan **admin utama ID 1**.
2. Buka **Admin → Settings → Eggs Changer**.
3. Nyalakan saklar **Changer Eggs untuk user**.
4. Centang **ID Nest** yang diizinkan, lalu **Save Setting**.
5. User pemilik server yang server-nya berada pada Nest tersebut akan melihat menu **Changer Eggs** di menu server.
6. User hanya dapat memilih Egg dari Nest yang sama. Nest server tidak dapat diganti dari menu user.

Saat Egg diganti, theme menyesuaikan startup, Docker image utama, dan variable ke default Egg baru. File server tidak dihapus dan tidak otomatis reinstall. Sebaiknya Stop server terlebih dahulu.

## Update theme

```bash
sudo bash UPDATE-THEME.sh
```

## Uninstall theme

```bash
sudo bash INSTALL-THEME.sh --remove
```

## V8 — Perbaikan Changer Eggs di menu Server mobile
- Changer Eggs sekarang ditambahkan langsung ke drawer **SERVER MENU** setelah konfigurasi Nest user dinyatakan aktif oleh backend.
- Tidak lagi bergantung pada keberhasilan injeksi tab React/native terlebih dahulu.
- Jika menu dibuka sebelum pengecekan Nest selesai, tombol akan muncul otomatis saat data selesai dimuat tanpa perlu reload halaman.
- Posisi tombol: sebelum **Settings** agar mudah ditemukan.
- Tetap hanya muncul untuk server dengan **Nest ID yang diaktifkan Admin ID 1** di `Admin → Settings → Eggs Changer`.


## V9 - Fix checkbox Eggs Changer di Android
Checkbox **Aktifkan Changer Eggs** dan pilihan **Nest ID** sekarang memakai kontrol native/touch-safe khusus halaman ini supaya dapat diklik di Android/WebView. Label juga terhubung langsung ke checkbox, jadi teks dapat ditekan untuk memilih.


## V10 — Saklar Egg Changer
- Kontrol **Aktifkan Changer Eggs untuk user** sekarang berupa saklar ON/OFF besar.
- Seluruh area saklar dapat ditap, lebih nyaman di Android/WebView.
- Pilihan Nest tetap checkbox native karena dapat memilih beberapa Nest sekaligus.
