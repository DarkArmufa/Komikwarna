<?php

namespace Pterodactyl\Http\Controllers\Base;

use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;
use Illuminate\Validation\ValidationException;
use Pterodactyl\Exceptions\Http\Connection\DaemonConnectionException;
use Pterodactyl\Http\Controllers\Controller;
use Pterodactyl\Models\Egg;
use Pterodactyl\Models\Server;
use Pterodactyl\Models\ServerVariable;
use Pterodactyl\Models\User;
use Pterodactyl\Repositories\Wings\DaemonServerRepository;
use Pterodactyl\Services\Servers\StartupModificationService;
use Pterodactyl\Support\ComicThemeSettings;

/**
 * Endpoint web-session untuk Egg Changer di halaman server user.
 * User hanya dapat mengganti Egg server miliknya sendiri, dan hanya di dalam
 * Nest server saat ini yang sudah diizinkan oleh admin ID 1.
 */
class ComicClientEggChangerController extends Controller
{
    public function index(Request $request, string $identifier): JsonResponse
    {
        $server = $this->serverForUser($request, $identifier);
        $config = ComicThemeSettings::read()['egg_changer'];

        if (!$this->nestAllowed($server, $config)) {
            return response()->json(['enabled' => false]);
        }

        $nest = $server->nest()->first();
        $eggs = Egg::query()
            ->where('nest_id', $server->nest_id)
            ->orderBy('name')
            ->get(['id', 'name', 'description'])
            ->map(fn (Egg $egg) => [
                'id' => (int) $egg->id,
                'name' => (string) $egg->name,
                'description' => trim(strip_tags((string) ($egg->description ?? ''))),
            ])
            ->values();

        return response()->json([
            'enabled' => true,
            'server' => ['name' => (string) $server->name],
            'nest' => ['id' => (int) $server->nest_id, 'name' => (string) ($nest->name ?? ('Nest #' . $server->nest_id))],
            'current_egg_id' => (int) $server->egg_id,
            'eggs' => $eggs,
        ]);
    }

    public function update(
        Request $request,
        string $identifier,
        StartupModificationService $service,
        DaemonServerRepository $daemon
    ): JsonResponse {
        $server = $this->serverForUser($request, $identifier);
        $config = ComicThemeSettings::read()['egg_changer'];

        if (!$this->nestAllowed($server, $config)) {
            abort(403, 'Egg Changer tidak aktif untuk Nest server ini.');
        }

        $data = $request->validate([
            'egg_id' => ['required', 'integer', 'exists:eggs,id'],
        ]);

        /** @var Egg $egg */
        $egg = Egg::query()->with('variables')->findOrFail((int) $data['egg_id']);
        if ((int) $egg->nest_id !== (int) $server->nest_id) {
            throw ValidationException::withMessages([
                'egg_id' => 'Egg harus berasal dari Nest server yang sudah diizinkan admin.',
            ]);
        }

        if ((int) $egg->id === (int) $server->egg_id) {
            return response()->json(['ok' => true, 'unchanged' => true, 'message' => 'Egg ini sudah digunakan.']);
        }

        $images = array_values(array_filter((array) $egg->docker_images, static function ($value) {
            return is_string($value) && trim($value) !== '';
        }));
        $environment = [];
        foreach ($egg->variables as $variable) {
            $environment[$variable->env_variable] = (string) ($variable->default_value ?? '');
        }

        $changed = DB::transaction(function () use ($server, $egg, $images, $environment, $service) {
            /** @var Server $locked */
            $locked = Server::query()->lockForUpdate()->findOrFail($server->id);

            // Validasi ulang setelah lock agar perubahan admin/Nest di waktu bersamaan
            // tidak dapat dipakai untuk menyeberang ke Nest lain.
            $freshConfig = ComicThemeSettings::read()['egg_changer'];
            if (!$this->nestAllowed($locked, $freshConfig) || (int) $egg->nest_id !== (int) $locked->nest_id) {
                abort(409, 'Pengaturan Egg Changer berubah. Muat ulang halaman lalu coba lagi.');
            }

            ServerVariable::query()->where('server_id', $locked->id)->delete();

            return $service->setUserLevel(User::USER_LEVEL_ADMIN)->handle($locked, [
                'egg_id' => (string) $egg->id,
                'startup' => is_string($egg->startup) && trim($egg->startup) !== '' ? $egg->startup : $locked->startup,
                'docker_image' => $images[0] ?? $locked->image,
                'skip_scripts' => (bool) $locked->skip_scripts,
                'environment' => $environment,
            ]);
        }, 3);

        $warning = null;
        try {
            $daemon->setServer($changed)->sync();
        } catch (DaemonConnectionException $exception) {
            // Data panel sudah aman tersimpan. Wings bisa disinkronkan saat kembali online.
            $warning = 'Egg tersimpan di panel, tetapi Wings sedang tidak dapat disinkronkan. Coba restart server setelah Wings online.';
        }

        return response()->json([
            'ok' => true,
            'egg_id' => (int) $egg->id,
            'message' => 'Egg berhasil diganti.',
            'warning' => $warning,
        ]);
    }

    private function serverForUser(Request $request, string $identifier): Server
    {
        $user = $request->user();
        abort_unless($user, 401);

        $shortColumn = Schema::hasColumn('servers', 'uuidShort') ? 'uuidShort' : (Schema::hasColumn('servers', 'uuid_short') ? 'uuid_short' : null);
        $query = Server::query()->where('uuid', $identifier);
        if ($shortColumn !== null) {
            $query->orWhere($shortColumn, $identifier);
        }

        /** @var Server $server */
        $server = $query->firstOrFail();
        abort_unless((int) $server->owner_id === (int) $user->id || (bool) $user->root_admin, 403);

        return $server;
    }

    private function nestAllowed(Server $server, array $config): bool
    {
        $ids = array_map('intval', is_array($config['nest_ids'] ?? null) ? $config['nest_ids'] : []);
        return !empty($config['enabled']) && in_array((int) $server->nest_id, $ids, true);
    }
}
