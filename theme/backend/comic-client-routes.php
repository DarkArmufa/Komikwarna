<?php

use Illuminate\Support\Facades\Route;
use Pterodactyl\Http\Controllers\Base\ComicClientEggChangerController;

// Web-session routes: tetap berada di middleware auth.session + CSRF milik routes/base.php.
Route::get('/comic-theme/client/servers/{identifier}/egg-changer', [ComicClientEggChangerController::class, 'index'])
    ->where('identifier', '[A-Za-z0-9-]{8,36}')
    ->name('comic.client.egg-changer');
Route::post('/comic-theme/client/servers/{identifier}/egg-changer', [ComicClientEggChangerController::class, 'update'])
    ->where('identifier', '[A-Za-z0-9-]{8,36}')
    ->name('comic.client.egg-changer.update');
