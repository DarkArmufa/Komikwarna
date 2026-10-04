<?php

namespace Pterodactyl\Support;

use Pterodactyl\Contracts\Repository\SettingsRepositoryInterface;

final class ComicThemeSettings
{
    public const KEY = 'comic-theme::settings';
    public const MAX_LINKS = 20;
    public const MAX_GATE_LINKS = 5;

    public static function defaults(): array
    {
        return [
            'brand' => '',
            'heading' => 'Layanan & Bantuan',
            'links' => [],
            'background' => [
                'image' => '',
                'overlay' => 38,
            ],
            'welcome' => [
                'enabled' => true,
                'title' => 'WELCOME TO {user}',
                'name' => '',
                'text' => '',
                'title_color' => '#ffffff',
                'name_color' => '#f7ca45',
                'text_color' => '#f6f7fb',
                'accent_color' => '#f7ca45',
                'overlay' => 45,
                'banner' => '',
                'banner_type' => 'none',
            ],
            // Satu papan pengumuman di seluruh halaman client (kecuali Admin). Versi dipakai untuk menampilkan ulang
            // pengumuman yang sudah pernah ditutup/diklik oleh pengguna.
            'notice' => [
                'enabled' => false,
                'title' => 'PENGUMUMAN',
                'text' => '',
                'button_label' => 'Lihat Info',
                'url' => '',
                'show_once' => true,
                'version' => 1,
            ],
            'egg_changer' => [
                'enabled' => false,
                'nest_ids' => [],
            ],
            'gate' => [
                'enabled' => false,
                'title' => 'Join dulu ya!',
                'text' => 'Gabung ke link di bawah, lalu tekan Sudah Follow.',
                'done_label' => 'Sudah Follow',
                'require_click' => true,
                'version' => 1,
                'links' => [],
            ],
        ];
    }

    public static function read(): array
    {
        $stored = json_decode(app(SettingsRepositoryInterface::class)->get(self::KEY, '{}'), true);
        $stored = is_array($stored) ? $stored : [];
        $d = self::defaults();
        $background = array_merge($d['background'], is_array($stored['background'] ?? null) ? $stored['background'] : []);
        $background['image'] = (string) ($background['image'] ?? '');
        $background['overlay'] = max(0, min(90, (int) ($background['overlay'] ?? $d['background']['overlay'])));
        $welcome = array_merge($d['welcome'], is_array($stored['welcome'] ?? null) ? $stored['welcome'] : []);
        $notice = array_merge($d['notice'], is_array($stored['notice'] ?? null) ? $stored['notice'] : []);
        $eggChanger = array_merge($d['egg_changer'], is_array($stored['egg_changer'] ?? null) ? $stored['egg_changer'] : []);
        $eggChanger['enabled'] = !empty($eggChanger['enabled']);
        $eggChanger['nest_ids'] = array_values(array_slice(array_unique(array_filter(array_map('intval', is_array($eggChanger['nest_ids'] ?? null) ? $eggChanger['nest_ids'] : []), fn ($id) => $id > 0)), 0, 50));
        $gate = array_merge($d['gate'], is_array($stored['gate'] ?? null) ? $stored['gate'] : []);
        $gate['links'] = array_values(array_slice(is_array($gate['links']) ? $gate['links'] : [], 0, self::MAX_GATE_LINKS));
        return [
            'brand' => (string) ($stored['brand'] ?? ''),
            'heading' => (string) ($stored['heading'] ?? $d['heading']),
            'links' => array_values(array_slice(is_array($stored['links'] ?? null) ? $stored['links'] : [], 0, self::MAX_LINKS)),
            'background' => $background,
            'welcome' => $welcome,
            'notice' => $notice,
            'egg_changer' => $eggChanger,
            'gate' => $gate,
        ];
    }

    public static function safeUrl(string $url): bool
    {
        $parts = parse_url($url);
        return filter_var($url, FILTER_VALIDATE_URL) !== false
            && is_array($parts) && in_array(strtolower($parts['scheme'] ?? ''), ['https', 'http'], true)
            && !isset($parts['user']) && !isset($parts['pass']);
    }
}
