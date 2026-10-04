<?php

namespace Pterodactyl\Http\Controllers\Admin;

use Illuminate\Http\Request;
use Pterodactyl\Http\Controllers\Controller;
use Pterodactyl\Contracts\Repository\SettingsRepositoryInterface;
use Pterodactyl\Support\ComicSecuritySettings;

class ComicSecurityController extends Controller
{
    public function index(Request $request)
    {
        abort_unless(ComicSecuritySettings::isOwner($request->user()), 404);

        return view('admin.settings.comic-security', ['sec' => ComicSecuritySettings::read()]);
    }

    public function update(Request $request, SettingsRepositoryInterface $settings)
    {
        abort_unless(ComicSecuritySettings::isOwner($request->user()), 404);

        $data = [];
        foreach (array_keys(ComicSecuritySettings::defaults()) as $key) {
            $data[$key] = $request->boolean($key);
        }
        $settings->set(ComicSecuritySettings::KEY, json_encode($data, JSON_THROW_ON_ERROR));

        return redirect()->route('admin.settings.comic-security')->with('comic_saved', true);
    }
}
