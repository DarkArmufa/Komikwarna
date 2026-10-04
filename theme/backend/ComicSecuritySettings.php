<?php

namespace Pterodactyl\Support;

use Pterodactyl\Contracts\Repository\SettingsRepositoryInterface;

/**
 * Pengaturan proteksi admin. Hanya admin dengan ID 1 yang boleh membaca/mengubah lewat menu.
 */
final class ComicSecuritySettings
{
    public const KEY = 'comic-theme::security';
    public const OWNER_ID = 1;

    public static function defaults(): array
    {
        return ['anti_delete' => false, 'anti_api' => false, 'anti_peek' => false, 'restrict_menu' => false];
    }

    public static function read(): array
    {
        try {
            $stored = json_decode((string) app(SettingsRepositoryInterface::class)->get(self::KEY, '{}'), true);
        } catch (\Throwable $e) {
            $stored = [];
        }
        $stored = is_array($stored) ? $stored : [];
        $out = [];
        foreach (self::defaults() as $key => $default) {
            $out[$key] = array_key_exists($key, $stored) ? (bool) $stored[$key] : $default;
        }

        return $out;
    }

    public static function isOwner($user): bool
    {
        return $user !== null && (int) $user->id === self::OWNER_ID;
    }
}
