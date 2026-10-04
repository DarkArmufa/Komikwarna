# Setting Admin (khusus admin ID 1)

Menu **Setting Admin** hanya muncul untuk user dengan ID 1 (sidebar admin dan tab Settings). Admin lain mendapat 404 bila membuka `/admin/settings/comic-security`.

| Toggle | Efek bagi admin selain ID 1 |
|---|---|
| Anti Delete Server Orang | Tidak bisa menghapus server yang bukan miliknya (halaman admin dan API). |
| Anti Akses API PTLA & PTLC | Tidak bisa memakai API Application (PTLA) dan menu Application API; API Client (PTLC) ditolak untuk server milik orang lain. |
| Anti Intip Server / Maling Script | Tidak bisa membuka halaman admin server, console, file, database, startup server orang lain. |

Default semua **OFF**; nyalakan lalu Simpan. Pengguna biasa dan admin ID 1 tidak pernah dibatasi.

## Batasan jujur
- Root admin tetap bisa mengubah akun user lain (termasuk ID 1), membuat node/egg, dan membuka database panel. Beri status admin hanya ke orang tepercaya.
- Proteksi memakai middleware pada route; jangan jalankan `php artisan route:cache`.
- Belum diuji di panel nyata dari sisi pembuat ZIP; coba dulu dengan admin kedua sebelum dipakai produksi.

## Batasi Menu Admin Lain
Bila toggle ini ON, admin selain ID 1 hanya melihat menu **Servers**. Tombol API PTLA/PTLC sengaja tidak ditampilkan di menu tema. Menu admin lain disembunyikan dan juga ditolak di server (403) walau URL dibuka manual; `/admin` diarahkan ke `/admin/servers`. Bila OFF, tampilan admin normal. Jika form Create Server ada bagian yang gagal dimuat, catat URL-nya dan tambahkan ke `menuAllowed()` di `ComicSecurityGuard.php`.
Catatan: toggle Anti API tetap bekerja untuk membatasi endpoint API meskipun tombol API tidak ditampilkan di menu.
