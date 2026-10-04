@extends('layouts.admin')
@section('title', 'Settings — Setting Admin')
@section('content-header')
    <h1>Setting Admin <small>Proteksi khusus admin utama (ID 1).</small></h1>
    <ol class="breadcrumb"><li><a href="{{ route('admin.index') }}">Admin</a></li><li><a href="{{ route('admin.settings') }}">Settings</a></li><li class="active">Setting Admin</li></ol>
@endsection
@section('content')
    <div class="comic-settings-tabs"><a class="btn btn-default" href="{{ route('admin.settings') }}">Panel Settings</a><a class="btn btn-default" href="{{ route('admin.settings.comic-links') }}">Tampilan &amp; Link</a><a class="btn btn-primary" href="{{ route('admin.settings.comic-security') }}">Setting Admin</a><a class="btn btn-default" href="{{ route('admin.settings.egg-changer') }}">Eggs Changer</a></div>
    @if(session('comic_saved'))<div class="alert alert-success" role="status">Pengaturan tersimpan dan langsung aktif.</div>@endif
    <form method="POST" action="{{ route('admin.settings.comic-security.update') }}" class="comic-link-form">
        {!! csrf_field() !!}
        <div class="box box-danger"><div class="box-header with-border"><h3 class="box-title">Anti Delete Server Orang</h3><label class="pull-right"><input type="checkbox" name="anti_delete" value="1" {{ $sec['anti_delete'] ? 'checked' : '' }}> ON / OFF</label></div><div class="box-body">
            <p>Admin lain tidak bisa menghapus server yang bukan miliknya (lewat halaman admin maupun API). Server milik sendiri tetap boleh dihapus.</p>
        </div></div>
        <div class="box box-warning"><div class="box-header with-border"><h3 class="box-title">Anti Akses API PTLA &amp; PTLC</h3><label class="pull-right"><input type="checkbox" name="anti_api" value="1" {{ $sec['anti_api'] ? 'checked' : '' }}> ON / OFF</label></div><div class="box-body">
            <p>Admin lain tidak bisa memakai API Application (PTLA), tidak bisa membuka menu Application API, dan tidak bisa memakai API Client (PTLC) untuk server milik orang lain. Pengguna biasa tidak terpengaruh.</p>
        </div></div>
        <div class="box box-info"><div class="box-header with-border"><h3 class="box-title">Anti Intip Server / Maling Script</h3><label class="pull-right"><input type="checkbox" name="anti_peek" value="1" {{ $sec['anti_peek'] ? 'checked' : '' }}> ON / OFF</label></div><div class="box-body">
            <p>Admin lain tidak bisa membuka halaman admin server orang lain, console, file manager, database, dan startup server tersebut. Daftar "semua server" di dashboard hanya menampilkan server miliknya.</p>
        </div></div>
        <div class="box box-primary"><div class="box-header with-border"><h3 class="box-title">Batasi Menu Admin Lain</h3><label class="pull-right"><input type="checkbox" name="restrict_menu" value="1" {{ $sec['restrict_menu'] ? 'checked' : '' }}> ON / OFF</label></div><div class="box-body">
            <p>Admin selain ID 1 hanya melihat menu <b>Servers</b>. Tombol API PTLA/PTLC tidak ditampilkan di menu tema. Menu lain (Settings, Users, Nodes, Locations, Databases, Mounts, Nests) hanya untuk ID 1 dan ditolak di server walau alamatnya dibuka manual. Kalau OFF, tampilan admin kembali normal.</p>
        </div></div>
        <div class="box box-success"><div class="box-body comic-settings-footer"><p>Hanya admin ID 1 yang melihat menu ini. Admin lain mendapat error 404 bila membuka alamatnya.</p><button type="submit" class="btn btn-primary">Simpan Pengaturan</button></div></div>
    </form>
@endsection
