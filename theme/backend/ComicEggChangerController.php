<?php

namespace Pterodactyl\Http\Controllers\Admin;

use Illuminate\Http\Request;
use Pterodactyl\Contracts\Repository\SettingsRepositoryInterface;
use Pterodactyl\Http\Controllers\Controller;
use Pterodactyl\Models\Nest;
use Pterodactyl\Support\ComicSecuritySettings;
use Pterodactyl\Support\ComicThemeSettings;

/**
 * Pengaturan Egg Changer untuk user. Hanya admin utama (ID 1) yang boleh
 * menentukan Nest mana yang boleh dipakai user untuk mengganti Egg.
 */
class ComicEggChangerController extends Controller
{
    public function index(Request $request)
    {
        $this->ownerOnly($request);

        $nests = Nest::query()
            ->withCount('eggs')
            ->orderBy('name')
            ->get();

        return view('admin.settings.comic-egg-changer', [
            'nests' => $nests,
            'eggChanger' => ComicThemeSettings::read()['egg_changer'],
        ]);
    }

    public function update(Request $request, SettingsRepositoryInterface $settings)
    {
        $this->ownerOnly($request);

        $data = $request->validate([
            'user_egg_enabled' => ['sometimes', 'boolean'],
            'nest_ids' => ['nullable', 'array', 'max:50'],
            'nest_ids.*' => ['integer', 'distinct', 'exists:nests,id'],
        ]);

        $current = ComicThemeSettings::read();
        $current['egg_changer'] = [
            'enabled' => !empty($data['user_egg_enabled']),
            'nest_ids' => array_values(array_map('intval', $data['nest_ids'] ?? [])),
        ];

        $settings->set(ComicThemeSettings::KEY, json_encode($current, JSON_THROW_ON_ERROR));

        return redirect()->route('admin.settings.egg-changer')->with('comic_egg_saved', true);
    }

    private function ownerOnly(Request $request): void
    {
        abort_unless(ComicSecuritySettings::isOwner($request->user()), 404);
    }
}
