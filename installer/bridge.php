<?php
// Input secrets arrive only on stdin. Never expose this file under public/.
declare(strict_types=1);
$root = '/var/www/pterodactyl';
require $root . '/vendor/autoload.php';
$app = require $root . '/bootstrap/app.php';
$app->make(Illuminate\Contracts\Console\Kernel::class)->bootstrap();
$data = json_decode(stream_get_contents(STDIN), true, 512, JSON_THROW_ON_ERROR);
switch ($argv[1] ?? '') {
    case 'version':
        echo config('app.version');
        break;
    case 'admin':
        app(Pterodactyl\Services\Users\UserCreationService::class)->handle([
            'email' => $data['email'], 'username' => $data['username'],
            'name_first' => 'Hosting', 'name_last' => 'Administrator',
            'password' => $data['password'], 'root_admin' => true,
        ]);
        echo "Administrator created\n";
        break;
    case 'node':
        $location = app(Pterodactyl\Services\Locations\LocationCreationService::class)->handle([
            'short' => $data['location'], 'long' => 'Created by Comic Ptero Installer',
        ]);
        $node = app(Pterodactyl\Services\Nodes\NodeCreationService::class)->handle([
            'name' => $data['location'], 'description' => 'Local Wings node',
            'location_id' => $location->id, 'public' => true,
            'fqdn' => $data['domain'], 'scheme' => 'https', 'behind_proxy' => false,
            'memory' => $data['memory'], 'memory_overallocate' => 0,
            'disk' => $data['disk'], 'disk_overallocate' => 0,
            'daemonBase' => '/var/lib/pterodactyl/volumes',
            'daemonSFTP' => 2022, 'daemonListen' => 8443, 'upload_size' => 100,
        ]);
        umask(0077);
        if (file_put_contents('/etc/pterodactyl/config.yml', $node->getYamlConfiguration()) === false) {
            throw new RuntimeException('Cannot write Wings configuration');
        }
        chmod('/etc/pterodactyl/config.yml', 0600);
        echo "Node and Wings configuration created\n";
        break;
    default:
        throw new RuntimeException('Unknown bridge operation');
}
