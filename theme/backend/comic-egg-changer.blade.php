@extends('layouts.admin')
@section('title', 'Eggs Changer')
@section('content-header')
    <h1>Eggs Changer <small>Atur Nest yang boleh dipakai user untuk mengganti Egg server.</small></h1>
    <ol class="breadcrumb">
        <li><a href="{{ route('admin.index') }}">Admin</a></li>
        <li><a href="{{ route('admin.settings') }}">Settings</a></li>
        <li class="active">Eggs Changer</li>
    </ol>
@endsection
@section('content')
    <div class="comic-settings-tabs">
        <a class="btn btn-default" href="{{ route('admin.settings') }}">Panel Settings</a>
        <a class="btn btn-default" href="{{ route('admin.settings.comic-links') }}">Tampilan &amp; Link</a>
        <a class="btn btn-default" href="{{ route('admin.settings.comic-security') }}">Setting Admin</a>
        <a class="btn btn-primary" href="{{ route('admin.settings.egg-changer') }}">Eggs Changer</a>
    </div>

    @if(session('comic_egg_saved'))
        <div class="alert alert-success" role="status"><b>Berhasil.</b> Pengaturan Egg Changer user sudah disimpan.</div>
    @endif
    @if($errors->any())
        <div class="alert alert-danger" role="alert"><ul>@foreach($errors->all() as $error)<li>{{ $error }}</li>@endforeach</ul></div>
    @endif

    <form method="POST" action="{{ route('admin.settings.egg-changer.update') }}" class="comic-link-form">
        {!! csrf_field() !!}
        <div class="box box-primary">
            <div class="box-header with-border"><h3 class="box-title">Setting Nest untuk User</h3></div>
            <div class="box-body">
                <div class="alert alert-info">
                    <b>Cara kerja:</b> admin ID 1 memilih Nest yang diizinkan. Jika server user memakai salah satu Nest tersebut, menu <b>Changer Eggs</b> muncul di halaman server user. User hanya bisa memilih Egg yang masih berada di <b>Nest server itu sendiri</b>; user tidak bisa pindah Nest.
                </div>

                <input type="hidden" name="user_egg_enabled" value="0">
                <div class="comic-egg-enable-row">
                    <label class="comic-egg-switch-control" for="comic-user-egg-enabled">
                        <input id="comic-user-egg-enabled" class="comic-egg-switch-input" type="checkbox" name="user_egg_enabled" value="1" {{ (string) old('user_egg_enabled', $eggChanger['enabled'] ? '1' : '0') === '1' ? 'checked' : '' }}>
                        <span class="comic-egg-switch-ui" aria-hidden="true"><span class="comic-egg-switch-knob"></span></span>
                        <span class="comic-egg-switch-copy"><b>Aktifkan Changer Eggs untuk user</b><small>Saklar ON/OFF untuk membuka fitur Changer Eggs pada Nest yang dipilih.</small></span>
                    </label>
                </div>

                <hr>
                <label>Pilih ID Nest yang boleh menggunakan Changer Eggs</label>
                <p class="help-block">Centang satu atau beberapa Nest. ID ditampilkan supaya mudah dicocokkan dengan konfigurasi Pterodactyl.</p>
                @php($selected = array_map('intval', old('nest_ids', $eggChanger['nest_ids'] ?? [])))
                <div class="row">
                    @forelse($nests as $nest)
                        <div class="col-md-6">
                            <div class="well well-sm comic-egg-nest-option" style="margin-bottom:10px">
                                <input id="comic-nest-{{ $nest->id }}" class="comic-egg-native-check" type="checkbox" name="nest_ids[]" value="{{ $nest->id }}" {{ in_array((int) $nest->id, $selected, true) ? 'checked' : '' }}>
                                <label for="comic-nest-{{ $nest->id }}">
                                    <span><b>#{{ $nest->id }} — {{ $nest->name }}</b><br><small>{{ $nest->eggs_count }} Egg tersedia</small></span>
                                </label>
                            </div>
                        </div>
                    @empty
                        <div class="col-md-12"><div class="alert alert-warning">Belum ada Nest di panel.</div></div>
                    @endforelse
                </div>

                <div class="alert alert-warning" style="margin-top:12px">
                    Mengganti Egg akan menyesuaikan startup command, Docker image utama, dan variable ke default Egg baru. File server tidak dihapus dan server tidak otomatis reinstall. Disarankan user menghentikan server sebelum mengganti Egg.
                </div>
            </div>
            <div class="box-footer comic-settings-footer">
                <p>Pengaturan ini hanya dapat diubah oleh admin utama user ID 1.</p>
                <button type="submit" class="btn btn-primary">Save Setting</button>
            </div>
        </div>
    </form>
@endsection
