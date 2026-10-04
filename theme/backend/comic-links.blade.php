@extends('layouts.admin')
@section('title', 'Settings — Tampilan & Link')
@section('content-header')
    <h1>Tampilan & Link <small>Welcome screen, papan notifikasi, gerbang join, dan link layanan.</small></h1>
    <ol class="breadcrumb"><li><a href="{{ route('admin.index') }}">Admin</a></li><li><a href="{{ route('admin.settings') }}">Settings</a></li><li class="active">Tampilan & Link</li></ol>
@endsection
@section('content')
    @php
        $bg = $comic['background']; $w = $comic['welcome']; $n = $comic['notice']; $g = $comic['gate'];
        $oldLinks = old('links', $comic['links']);
        $oldGate = old('gate_links', $g['links']);
        $flag = fn ($name, $stored) => session()->hasOldInput() ? (bool) old($name) : (bool) $stored;
    @endphp
    <div class="comic-settings-tabs"><a class="btn btn-default" href="{{ route('admin.settings') }}">Panel Settings</a><a class="btn btn-primary" href="{{ route('admin.settings.comic-links') }}">Tampilan & Link</a>@if(auth()->check() && (int) auth()->id() === \Pterodactyl\Support\ComicSecuritySettings::OWNER_ID)<a class="btn btn-default" href="{{ route('admin.settings.comic-security') }}">Setting Admin</a><a class="btn btn-default" href="{{ route('admin.settings.egg-changer') }}">Eggs Changer</a>@endif</div>
    @if(session('comic_saved'))<div class="alert alert-success" role="status">Pengaturan tersimpan. Muat ulang panel pengguna untuk melihat perubahan.</div>@endif
    @if($errors->any())<div class="alert alert-danger" role="alert"><ul>@foreach($errors->all() as $error)<li>{{ $error }}</li>@endforeach</ul></div>@endif
    <form method="POST" action="{{ route('admin.settings.comic-links.update') }}" class="comic-link-form" enctype="multipart/form-data">
        {!! csrf_field() !!}

        <div class="box"><div class="box-header with-border"><h3 class="box-title">Identitas & Menu</h3></div><div class="box-body">
            <div class="row"><div class="form-group col-md-6"><label for="comic-brand">Nama besar pada header</label><input class="form-control" id="comic-brand" name="brand" maxlength="48" value="{{ old('brand', $comic['brand']) }}" placeholder="{{ config('app.name') }}"><p class="help-block">Kosongkan untuk mengikuti Company Name di Panel Settings.</p></div>
            <div class="form-group col-md-6"><label for="comic-heading">Judul bagian link</label><input class="form-control" id="comic-heading" name="heading" required maxlength="64" value="{{ old('heading', $comic['heading']) }}"></div></div>
        </div></div>

        <div class="box"><div class="box-header with-border"><h3 class="box-title">Background Panel</h3></div><div class="box-body">
            <p class="help-block">Upload gambar untuk dijadikan background utama panel. Background tampil pada halaman pengguna dan Admin, sedangkan card/menu tetap berada di atasnya agar teks tetap terbaca.</p>
            <div class="row">
                <div class="form-group col-md-8"><label for="comic-background">Upload background (JPG/PNG/WEBP/GIF, maks 20 MB)</label><input type="file" id="comic-background" name="background_image" accept="image/jpeg,image/png,image/webp,image/gif"><p class="help-block">Gambar otomatis menggunakan mode cover, posisi tengah, dan tetap memenuhi layar saat halaman di-scroll.</p></div>
                <div class="form-group col-md-4"><label for="comic-background-overlay">Gelap background (0–90%)</label><input type="number" class="form-control" id="comic-background-overlay" name="background_overlay" min="0" max="90" value="{{ old('background_overlay', $bg['overlay']) }}"><p class="help-block">Naikkan jika teks terasa kurang jelas.</p></div>
            </div>
            @if($bg['image'])
                <p>Background sekarang:</p>
                <img class="comic-background-preview" src="{{ $bg['image'] }}" alt="Background panel sekarang">
                <div class="checkbox"><label><input type="checkbox" name="background_remove" value="1"> Hapus background</label></div>
            @endif
        </div></div>

        <div class="box"><div class="box-header with-border"><h3 class="box-title">Banner Welcome (tampil di Dashboard)</h3><label class="pull-right"><input type="checkbox" name="welcome_enabled" value="1" {{ $flag('welcome_enabled', $w['enabled']) ? 'checked' : '' }}> Aktif</label></div><div class="box-body">
            <div class="row">
                <div class="form-group col-md-6"><label for="w-title">Tulisan atas</label><input class="form-control" id="w-title" name="welcome_title" required maxlength="64" value="{{ old('welcome_title', $w['title']) }}"><p class="help-block">Gunakan <code>{user}</code> untuk menyebut username yang sedang login.</p></div>
                <div class="form-group col-md-6"><label for="w-name">Nama besar (kosong = nama header)</label><input class="form-control" id="w-name" name="welcome_name" maxlength="64" value="{{ old('welcome_name', $w['name']) }}"><p class="help-block"><code>{user}</code> juga bisa dipakai di sini.</p></div>
            </div>
            <div class="form-group"><label for="w-text">Teks sambutan (opsional)</label><textarea class="form-control" id="w-text" name="welcome_text" rows="2" maxlength="240">{{ old('welcome_text', $w['text']) }}</textarea><p class="help-block">Token <code>{user}</code> otomatis berubah menjadi username.</p></div>
            <label>Warna</label>
            <div class="comic-color-row">
                @foreach(['title_color' => 'Tulisan atas', 'name_color' => 'Nama besar', 'text_color' => 'Teks sambutan', 'accent_color' => 'Tombol & garis'] as $f => $l)
                    <div class="form-group"><label for="c-{{ $f }}">{{ $l }}</label><input type="color" class="form-control" id="c-{{ $f }}" name="{{ $f }}" value="{{ old($f, $w[$f]) }}"></div>
                @endforeach
                <div class="form-group"><label for="c-overlay">Gelap banner (0–90%)</label><input type="number" class="form-control" id="c-overlay" name="overlay" min="0" max="90" value="{{ old('overlay', $w['overlay']) }}"></div>
            </div>
            <hr>
            <div class="form-group"><label for="w-banner">Upload banner (gambar JPG/PNG/WEBP/GIF atau video MP4/WEBM, maks 30 MB)</label><input type="file" id="w-banner" name="banner" accept="image/jpeg,image/png,image/webp,image/gif,video/mp4,video/webm">
                <p class="help-block">Jika gagal upload, batas biasanya dari PHP <code>upload_max_filesize</code>/<code>post_max_size</code> atau nginx <code>client_max_body_size</code>. Alternatif: isi URL banner di bawah.</p></div>
            <div class="form-group"><label for="w-bannerurl">atau URL banner (https://...)</label><input type="url" class="form-control" id="w-bannerurl" name="banner_url" maxlength="2048" placeholder="https://.../banner.mp4" value="{{ old('banner_url') }}"></div>
            @if($w['banner'])
                <p>Banner sekarang ({{ $w['banner_type'] === 'video' ? 'video' : 'gambar' }}):</p>
                @if($w['banner_type'] === 'video')<video class="comic-banner-preview" src="{{ $w['banner'] }}" muted loop autoplay playsinline></video>@else<img class="comic-banner-preview" src="{{ $w['banner'] }}" alt="Banner sekarang">@endif
                <label><input type="checkbox" name="banner_remove" value="1"> Hapus banner</label>
            @endif
        </div></div>

        <div class="box"><div class="box-header with-border"><h3 class="box-title">Notifikasi Atas — Papan Peringatan</h3><label class="pull-right"><input type="checkbox" name="notice_enabled" value="1" {{ $flag('notice_enabled', $n['enabled']) ? 'checked' : '' }}> Aktif</label></div><div class="box-body">
            <p class="help-block">Hanya satu papan pengumuman. Tampil di halaman pengguna seperti Dashboard, Server, Files, Console, Account, dan halaman client lainnya, tetapi tidak tampil di menu Admin. Di Dashboard posisinya berada di atas Welcome. Bisa berisi link dan nama tombol sendiri. Token <code>{user}</code> bisa dipakai pada judul, pesan, dan nama tombol.</p>
            <div class="row">
                <div class="form-group col-md-6"><label for="n-title">Judul notifikasi</label><input class="form-control" id="n-title" name="notice_title" required maxlength="64" value="{{ old('notice_title', $n['title']) }}" placeholder="PENGUMUMAN"></div>
                <div class="form-group col-md-6"><label for="n-button">Nama tombol link</label><input class="form-control" id="n-button" name="notice_button_label" maxlength="40" value="{{ old('notice_button_label', $n['button_label']) }}" placeholder="Lihat Info"></div>
            </div>
            <div class="form-group"><label for="n-text">Isi notifikasi</label><textarea class="form-control" id="n-text" name="notice_text" rows="2" maxlength="280" placeholder="Contoh: Maintenance malam ini pukul 23.00">{{ old('notice_text', $n['text']) }}</textarea></div>
            <div class="form-group"><label for="n-url">Link tombol (opsional)</label><input class="form-control" id="n-url" type="url" name="notice_url" maxlength="2048" placeholder="https://..." value="{{ old('notice_url', $n['url']) }}"></div>
            <div class="checkbox"><label><input type="checkbox" name="notice_show_once" value="1" {{ $flag('notice_show_once', $n['show_once']) ? 'checked' : '' }}> Tampil sekali per pengguna sampai ditutup atau tombol link diklik</label></div>
            <div class="checkbox"><label><input type="checkbox" name="notice_reset" value="1"> Tampilkan ulang notifikasi ini ke semua pengguna</label></div>
        </div></div>

        <div class="box"><div class="box-header with-border"><h3 class="box-title">Gerbang Join (wajib join dulu)</h3><label class="pull-right"><input type="checkbox" name="gate_enabled" value="1" {{ $flag('gate_enabled', $g['enabled']) ? 'checked' : '' }}> Aktif</label></div><div class="box-body">
            <p class="help-block">Pengguna melihat tombol link dan tombol “Sudah Follow”. Setelah menekan “Sudah Follow”, pilihan disimpan di browser (localStorage + cookie 1 tahun) sehingga tidak muncul lagi saat reload. Gerbang tidak aktif bila belum ada link.</p>
            <div class="row">
                <div class="form-group col-md-6"><label for="g-title">Judul</label><input class="form-control" id="g-title" name="gate_title" required maxlength="48" value="{{ old('gate_title', $g['title']) }}"></div>
                <div class="form-group col-md-6"><label for="g-done">Teks tombol konfirmasi</label><input class="form-control" id="g-done" name="gate_done_label" required maxlength="32" value="{{ old('gate_done_label', $g['done_label']) }}"></div>
            </div>
            <div class="form-group"><label for="g-text">Keterangan</label><input class="form-control" id="g-text" name="gate_text" maxlength="240" value="{{ old('gate_text', $g['text']) }}"></div>
            <div class="checkbox"><label><input type="checkbox" name="gate_require_click" value="1" {{ $flag('gate_require_click', $g['require_click']) ? 'checked' : '' }}> Tombol “Sudah Follow” baru aktif 3 detik setelah salah satu link dibuka</label></div>
            <div class="checkbox"><label><input type="checkbox" name="gate_reset" value="1"> Tampilkan ulang gerbang ke semua pengguna (reset status “sudah follow”)</label></div>
            <label>Link join (maks {{ \Pterodactyl\Support\ComicThemeSettings::MAX_GATE_LINKS }})</label>
            <div id="gate-rows">
                @foreach($oldGate as $i => $gl)
                    <div class="comic-dyn-row"><div class="form-group"><label>Nama</label><input class="form-control" name="gate_links[{{ $i }}][label]" maxlength="48" value="{{ $gl['label'] ?? '' }}"></div><div class="form-group"><label>URL</label><input class="form-control" type="url" name="gate_links[{{ $i }}][url]" maxlength="2048" placeholder="https://..." value="{{ $gl['url'] ?? '' }}"></div><span></span><button type="button" class="btn btn-danger btn-remove" data-remove>Hapus</button></div>
                @endforeach
            </div>
            <button type="button" class="btn btn-success" id="add-gate">+ Tambah link join</button>
        </div></div>

        <div class="box"><div class="box-header with-border"><h3 class="box-title">Link Layanan (menu kanan)</h3></div><div class="box-body">
            <p class="help-block">Tambah sebanyak yang dibutuhkan (maks {{ \Pterodactyl\Support\ComicThemeSettings::MAX_LINKS }}). Baris kosong diabaikan.</p>
            <div id="link-rows">
                @foreach($oldLinks as $i => $l)
                    <div class="comic-dyn-row"><div class="form-group"><label>Nama tombol</label><input class="form-control" name="links[{{ $i }}][label]" maxlength="64" value="{{ $l['label'] ?? '' }}"></div><div class="form-group"><label>URL tujuan</label><input class="form-control" type="url" name="links[{{ $i }}][url]" maxlength="2048" placeholder="https://..." value="{{ $l['url'] ?? '' }}"></div>
                    <div class="form-group"><label>Warna</label><select class="form-control" name="links[{{ $i }}][tone]">@foreach(['green' => 'Hijau', 'yellow' => 'Kuning', 'dark' => 'Gelap'] as $t => $tl)<option value="{{ $t }}" {{ ($l['tone'] ?? 'dark') === $t ? 'selected' : '' }}>{{ $tl }}</option>@endforeach</select></div>
                    <div><label class="checkbox-inline"><input type="checkbox" name="links[{{ $i }}][enabled]" value="1" {{ !empty($l['enabled']) ? 'checked' : '' }}> Aktif</label><button type="button" class="btn btn-danger btn-remove" data-remove>Hapus</button></div></div>
                @endforeach
            </div>
            <button type="button" class="btn btn-success" id="add-link">+ Tambah link</button>
        </div></div>

        <div class="box"><div class="box-body comic-settings-footer"><p>Perubahan tampil ke pengguna setelah halaman dimuat ulang. Link terbuka di tab baru.</p><button type="submit" class="btn btn-primary">Simpan Pengaturan</button></div></div>
    </form>

    <template id="tpl-gate"><div class="comic-dyn-row"><div class="form-group"><label>Nama</label><input class="form-control" name="gate_links[__I__][label]" maxlength="48"></div><div class="form-group"><label>URL</label><input class="form-control" type="url" name="gate_links[__I__][url]" maxlength="2048" placeholder="https://..."></div><span></span><button type="button" class="btn btn-danger btn-remove" data-remove>Hapus</button></div></template>
    <template id="tpl-link"><div class="comic-dyn-row"><div class="form-group"><label>Nama tombol</label><input class="form-control" name="links[__I__][label]" maxlength="64"></div><div class="form-group"><label>URL tujuan</label><input class="form-control" type="url" name="links[__I__][url]" maxlength="2048" placeholder="https://..."></div><div class="form-group"><label>Warna</label><select class="form-control" name="links[__I__][tone]"><option value="green">Hijau</option><option value="yellow">Kuning</option><option value="dark" selected>Gelap</option></select></div><div><label class="checkbox-inline"><input type="checkbox" name="links[__I__][enabled]" value="1" checked> Aktif</label><button type="button" class="btn btn-danger btn-remove" data-remove>Hapus</button></div></div></template>
@endsection
@section('footer-scripts')
    @parent
    <script>
    (function () {
        var counters = {gate: Date.now() % 100000, link: Date.now() % 100000 + 500};
        function wire(btnId, boxId, tplId, key, max) {
            document.getElementById(btnId).addEventListener('click', function () {
                var box = document.getElementById(boxId);
                if (box.children.length >= max) { alert('Batas maksimum ' + max + ' tercapai.'); return; }
                var html = document.getElementById(tplId).innerHTML.split('__I__').join(String(++counters[key]));
                box.insertAdjacentHTML('beforeend', html);
            });
        }
        wire('add-gate', 'gate-rows', 'tpl-gate', 'gate', {{ \Pterodactyl\Support\ComicThemeSettings::MAX_GATE_LINKS }});
        wire('add-link', 'link-rows', 'tpl-link', 'link', {{ \Pterodactyl\Support\ComicThemeSettings::MAX_LINKS }});
        document.addEventListener('click', function (e) {
            var b = e.target.closest('[data-remove]');
            if (b) { var row = b.closest('.comic-dyn-row'); if (row) row.remove(); }
        });
    })();
    </script>
@endsection
