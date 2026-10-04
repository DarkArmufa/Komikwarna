<?php

namespace Pterodactyl\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Pterodactyl\Models\Server;
use Pterodactyl\Support\ComicSecuritySettings;

/**
 * Proteksi untuk admin selain ID 1. Dipasang otomatis oleh routes/comic-theme.php.
 * Admin ID 1 dan pengguna biasa (bukan root admin) tidak pernah dibatasi di sini.
 */
class ComicSecurityGuard
{
    public function handle(Request $request, Closure $next)
    {
        $user = $request->user();
        if (!$user || !$user->root_admin || ComicSecuritySettings::isOwner($user)) {
            return $next($request);
        }

        $cfg = ComicSecuritySettings::read();
        if (!$cfg['anti_delete'] && !$cfg['anti_api'] && !$cfg['anti_peek'] && !$cfg['restrict_menu']) {
            return $next($request);
        }

        $path = trim($request->path(), '/');
        $method = strtoupper($request->method());
        $isApi = str_starts_with($path, 'api/');

        if ($cfg['restrict_menu'] && ($path === 'admin' || str_starts_with($path, 'admin/'))) {
            if ($path === 'admin') {
                return redirect('/admin/servers');
            }
            if (!$this->menuAllowed($path, $method)) {
                return $this->deny($request, 'Menu ini hanya untuk admin utama (ID 1). Admin lain hanya melihat menu Servers.', $isApi);
            }
        }

        $adminServerView = (bool) preg_match('#^admin/servers/view/[^/]+#', $path);
        $adminServerDelete = $method === 'POST' && (bool) preg_match('#^admin/servers/view/[^/]+/delete/?$#', $path);
        $appServerDelete = $method === 'DELETE' && (bool) preg_match('#^api/application/servers/[^/]+#', $path);
        $appApi = str_starts_with($path, 'api/application');
        $adminApiKeys = (bool) preg_match('#^admin/api(/|$)#', $path);
        $clientServer = (bool) preg_match('#^api/client/servers/[^/]+#', $path);

        if ($cfg['anti_delete'] && ($adminServerDelete || $appServerDelete)) {
            if ($this->foreign($request, $user)) {
                return $this->deny($request, 'Anti Delete aktif: kamu tidak boleh menghapus server milik orang lain.', $isApi, true);
            }
        }

        if ($cfg['anti_api']) {
            if ($appApi || $adminApiKeys) {
                return $this->deny($request, 'Anti API aktif: akses API Application (PTLA) hanya untuk admin utama.', $isApi);
            }
            if ($clientServer && $request->bearerToken() && $this->foreign($request, $user)) {
                return $this->deny($request, 'Anti API aktif: API Client (PTLC) tidak boleh dipakai untuk server milik orang lain.', $isApi);
            }
        }

        if ($cfg['anti_peek']) {
            if (($adminServerView || $clientServer) && $this->foreign($request, $user)) {
                return $this->deny($request, 'Anti Intip aktif: kamu tidak bisa membuka server milik orang lain.', $isApi);
            }
            if ($path === 'api/client' && in_array($request->query('type'), ['admin', 'admin-all'], true)) {
                // Daftar server orang lain disembunyikan; tampilkan hanya server milik sendiri.
                $request->query->set('type', 'owner');
            }
        }

        return $next($request);
    }

    /** Halaman admin yang boleh dibuka admin selain ID 1 saat Batasi Menu aktif. */
    private function menuAllowed(string $path, string $method): bool
    {
        if (preg_match('#^admin/(servers|api)(/|$)#', $path)) {
            return true;
        }
        // Endpoint pendukung form "Create Server" (hanya baca).
        if ($method === 'GET' && preg_match('#^admin/(users/accounts\.json|nests/egg/[^/]+|nodes/view/\d+/allocations(\.json)?)$#', $path)) {
            return true;
        }

        return false;
    }

    /** True bila server pada route bukan milik admin ini (bukan owner dan bukan subuser). Gagal = dianggap milik orang lain. */
    private function foreign(Request $request, $user): bool
    {
        $server = $request->route('server');
        if (!$server instanceof Server) {
            $server = is_scalar($server) && $server !== '' ? Server::query()->where('id', $server)->first() : null;
        }
        if (!$server instanceof Server) {
            return true;
        }
        if ((int) $server->owner_id === (int) $user->id) {
            return false;
        }

        return !$server->subusers()->where('user_id', $user->id)->exists();
    }

    private function deny(Request $request, string $message, bool $isApi, bool $flashBack = false)
    {
        if ($isApi || $request->expectsJson()) {
            return response()->json(['errors' => [[
                'code' => 'ComicSecurityGuard',
                'status' => '403',
                'detail' => $message,
            ]]], 403);
        }
        if ($flashBack && class_exists(\Prologue\Alerts\Facades\Alert::class)) {
            \Prologue\Alerts\Facades\Alert::danger($message)->flash();

            return redirect('/admin/servers');
        }

        abort(403, $message);
    }
}
