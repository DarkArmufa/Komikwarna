<?php
// Loaded inside Pterodactyl's authenticated, CSRF-protected admin route group.
\Illuminate\Support\Facades\Route::get('/settings/comic-links', [\Pterodactyl\Http\Controllers\Admin\ComicThemeController::class, 'index'])->name('admin.settings.comic-links');
\Illuminate\Support\Facades\Route::post('/settings/comic-links', [\Pterodactyl\Http\Controllers\Admin\ComicThemeController::class, 'update'])->name('admin.settings.comic-links.update');

// Setting Admin (anti delete / anti API / anti intip) — hanya admin ID 1 (dicek lagi di controller).
\Illuminate\Support\Facades\Route::get('/settings/comic-security', [\Pterodactyl\Http\Controllers\Admin\ComicSecurityController::class, 'index'])->name('admin.settings.comic-security');
\Illuminate\Support\Facades\Route::post('/settings/comic-security', [\Pterodactyl\Http\Controllers\Admin\ComicSecurityController::class, 'update'])->name('admin.settings.comic-security.update');

// Setting Egg Changer user — hanya admin utama ID 1.
\Illuminate\Support\Facades\Route::get('/settings/egg-changer', [\Pterodactyl\Http\Controllers\Admin\ComicEggChangerController::class, 'index'])->name('admin.settings.egg-changer');
\Illuminate\Support\Facades\Route::post('/settings/egg-changer', [\Pterodactyl\Http\Controllers\Admin\ComicEggChangerController::class, 'update'])->name('admin.settings.egg-changer.update');

// Pasang ComicSecurityGuard otomatis di route admin/API yang rentan, tanpa mengubah file inti Pterodactyl.
\Illuminate\Support\Facades\Event::listen(\Illuminate\Routing\Events\RouteMatched::class, function ($event) {
    if (!class_exists(\Pterodactyl\Http\Middleware\ComicSecurityGuard::class)) {
        return;
    }
    $uri = $event->route->uri();
    foreach (['admin', 'api/application', 'api/client'] as $prefix) {
        if (str_starts_with($uri, $prefix)) {
            $event->route->middleware(\Pterodactyl\Http\Middleware\ComicSecurityGuard::class);
            return;
        }
    }
});
