#!/usr/bin/env python3
"""Reversible assets and isolated admin settings module for Pterodactyl."""
import sys
sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "installer"))
from license_gate import require_license, prompt_license
import argparse
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

BASE = Path(__file__).resolve().parent.parent
START = '<!-- COMIC-PTERO:BEGIN -->'
END = '<!-- COMIC-PTERO:END -->'
ROUTE_START = '// COMIC-PTERO-ROUTES:BEGIN'
ROUTE_END = '// COMIC-PTERO-ROUTES:END'
CLIENT_ROUTE_START = '// COMIC-PTERO-CLIENT-ROUTES:BEGIN'
CLIENT_ROUTE_END = '// COMIC-PTERO-CLIENT-ROUTES:END'
TARGETS = ['resources/views/templates/wrapper.blade.php', 'resources/views/layouts/admin.blade.php']
MODULES = {
    'ComicThemeSettings.php': 'app/Support/ComicThemeSettings.php',
    'ComicThemeController.php': 'app/Http/Controllers/Admin/ComicThemeController.php',
    'comic-routes.php': 'routes/comic-theme.php',
    'comic-links.blade.php': 'resources/views/admin/settings/comic-links.blade.php',
    'ComicSecuritySettings.php': 'app/Support/ComicSecuritySettings.php',
    'ComicSecurityController.php': 'app/Http/Controllers/Admin/ComicSecurityController.php',
    'ComicSecurityGuard.php': 'app/Http/Middleware/ComicSecurityGuard.php',
    'comic-security.blade.php': 'resources/views/admin/settings/comic-security.blade.php',
    'ComicEggChangerController.php': 'app/Http/Controllers/Admin/ComicEggChangerController.php',
    'comic-egg-changer.blade.php': 'resources/views/admin/settings/comic-egg-changer.blade.php',
    'ComicClientEggChangerController.php': 'app/Http/Controllers/Base/ComicClientEggChangerController.php',
    'comic-client-routes.php': 'routes/comic-client.php',
}


def strip_block(text, start=START, end=END):
    return re.sub(r'\n?' + re.escape(start) + r'.*?' + re.escape(end) + r'\n?', '', text, flags=re.S)


def write(path, data, owner):
    missing = []
    parent = path.parent
    while not parent.exists():
        missing.append(parent)
        parent = parent.parent
    path.parent.mkdir(parents=True, exist_ok=True)
    for directory in missing: os.chmod(directory, 0o755)
    stat = path.stat() if path.exists() else owner.stat()
    tmp = path.with_name(path.name + '.comic-tmp')
    tmp.write_bytes(data)
    os.chmod(tmp, (stat.st_mode & 0o777) if path.exists() else 0o644)
    if os.geteuid() == 0: os.chown(tmp, stat.st_uid, stat.st_gid)
    tmp.replace(path)


def install(panel, remove=False):
    panel = Path(panel).resolve()
    if not (panel / 'artisan').is_file(): raise ValueError('Folder ini bukan instalasi Pterodactyl.')
    routes = panel / 'routes/admin.php'
    base_routes = panel / 'routes/base.php'
    targets = [panel / t for t in TARGETS]
    for p in targets:
        if not p.is_file() or '</head>' not in p.read_text(): raise ValueError('Template tidak didukung: ' + str(p))
    if not routes.is_file() or not routes.read_text().startswith('<?php') or '?>' in routes.read_text():
        raise ValueError('routes/admin.php tidak didukung; tidak ada file yang diubah.')
    if not base_routes.is_file() or not base_routes.read_text().startswith('<?php') or '?>' in base_routes.read_text() or "Route::get('/'," not in base_routes.read_text():
        raise ValueError('routes/base.php tidak didukung; tidak ada file yang diubah.')
    changes = {p: strip_block(p.read_text()) for p in targets}
    route_text = strip_block(routes.read_text(), ROUTE_START, ROUTE_END)
    base_route_text = strip_block(base_routes.read_text(), CLIENT_ROUTE_START, CLIENT_ROUTE_END)
    if not remove:
        assets = {name: (BASE / 'theme' / name).read_bytes() for name in ['comic.css', 'comic.js']}
        assets.update({name: (BASE / 'web/assets' / name).read_bytes() for name in ['BarlowCondensed-Bold.ttf', 'Inter.ttf', 'OFL-Barlow.txt', 'OFL-Inter.txt']})
        digest = hashlib.sha256(assets['comic.css'] + assets['comic.js']).hexdigest()[:12]
        A = '\\Illuminate\\Support\\Facades\\Auth'
        owner_meta = '<meta name="comic-security-owner" content="{{ (' + A + '::check() && (int) ' + A + '::user()->id === 1) ? 1 : 0 }}">'
        restrict_meta = ('<meta name="comic-admin-restrict" content="{{ (' + A + '::check() && ' + A + '::user()->root_admin && (int) ' + A + "::user()->id !== 1 && \\Pterodactyl\\Support\\ComicSecuritySettings::read()['restrict_menu']) ? 1 : 0 }}\">")
        cfg_meta = '<meta name="comic-theme-config" content="{{ json_encode(\\Pterodactyl\\Support\\ComicThemeSettings::read()) }}">'
        user_meta = '<meta name="comic-user" content="{{ ' + A + "::check() ? " + A + "::user()->username : '' }}\">"
        csrf_meta = '<meta name="comic-csrf" content="{{ csrf_token() }}">'
        block = ('\n' + START + '\n' + cfg_meta + '\n' + user_meta + '\n' + csrf_meta + '\n' + owner_meta + '\n' + restrict_meta + '\n'
                 + f'<link rel="stylesheet" href="/comic-theme/comic.css?v={digest}">\n<script defer src="/comic-theme/comic.js?v={digest}"></script>\n' + END + '\n')
        for p in targets: changes[p] = changes[p].replace('</head>', block + '</head>', 1)
        route_text = route_text.rstrip() + '\n\n' + ROUTE_START + "\nrequire __DIR__ . '/comic-theme.php';\n" + ROUTE_END + '\n'
        client_block = CLIENT_ROUTE_START + "\nrequire __DIR__ . '/comic-client.php';\n" + CLIENT_ROUTE_END + '\n\n'
        base_route_text = base_route_text.replace("Route::get('/',", client_block + "Route::get('/',", 1)
        # Install dependencies before templates/routes reference them.
        extra = {panel / dest: (BASE / 'theme/backend' / src).read_bytes() for src, dest in MODULES.items()}
        extra.update({panel / 'public/comic-theme' / name: data for name, data in assets.items()})
        changes = {**extra, **changes}
    # Uninstall keeps the isolated module and DB settings but removes all entry points.
    changes[routes] = route_text
    changes[base_routes] = base_route_text
    if not remove and shutil.which('php'):
        for src in MODULES:
            if src.endswith('.php') and not src.endswith('.blade.php'):
                r = subprocess.run(['php', '-l', str(BASE / 'theme/backend' / src)], capture_output=True, text=True)
                if r.returncode != 0: raise ValueError('Syntax PHP error pada ' + src + ': ' + r.stdout + r.stderr)
    snapshot = {p: p.read_bytes() if p.exists() else None for p in changes}
    backup = panel / 'storage/comic-theme-backups' / (time.strftime('%Y%m%d-%H%M%S') + '-' + str(time.time_ns())[-8:])
    backup.mkdir(parents=True, exist_ok=False)
    for p, data in snapshot.items():
        if data is not None:
            dest = backup / p.relative_to(panel)
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, dest)
    try:
        for p, data in changes.items(): write(p, data.encode() if isinstance(data, str) else data, routes)
    except Exception:
        for p, data in snapshot.items():
            if data is None: p.unlink(missing_ok=True)
            else: write(p, data, routes)
        raise
    if not remove:
        # Folder unggahan banner harus bisa ditulis oleh user web server (pemilik file panel).
        uploads = panel / 'public/comic-theme/uploads'
        uploads.mkdir(parents=True, exist_ok=True)
        os.chmod(uploads, 0o755)
        if os.geteuid() == 0:
            st = routes.stat()
            os.chown(uploads, st.st_uid, st.st_gid)
    print('Theme removed; settings retained.' if remove else 'Comic theme installed. Admin ID 1 → Settings → Eggs Changer untuk memilih Nest; user server yang cocok akan melihat menu Changer Eggs.')
    print('Backup:', backup)
    print('Clear caches: php artisan route:clear && php artisan view:clear')


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--panel', default='/var/www/pterodactyl')
    p.add_argument('--remove', action='store_true')
    p.add_argument('--license-stdin', action='store_true', help='Baca license dari stdin untuk otomasi')
    a = p.parse_args()
    if not a.remove:
        try:
            require_license(sys.stdin.readline().rstrip('\n')) if a.license_stdin else prompt_license()
        except ValueError as e:
            p.exit(1, str(e)+'\n')
    install(a.panel, a.remove)
