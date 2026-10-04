<?php

namespace Pterodactyl\Http\Controllers\Admin;

use Illuminate\Http\Request;
use Illuminate\Validation\ValidationException;
use Pterodactyl\Http\Controllers\Controller;
use Pterodactyl\Contracts\Repository\SettingsRepositoryInterface;
use Pterodactyl\Support\ComicThemeSettings;

class ComicThemeController extends Controller
{
    private const IMAGE_MIMES = [
        'image/jpeg' => 'jpg', 'image/png' => 'png', 'image/webp' => 'webp', 'image/gif' => 'gif',
    ];

    private const MIMES = [
        'image/jpeg' => 'jpg', 'image/png' => 'png', 'image/webp' => 'webp', 'image/gif' => 'gif',
        'video/mp4' => 'mp4', 'video/webm' => 'webm',
    ];

    public function index(Request $request)
    {
        abort_unless($request->user() && $request->user()->root_admin, 403);
        return view('admin.settings.comic-links', ['comic' => ComicThemeSettings::read()]);
    }

    public function update(Request $request, SettingsRepositoryInterface $settings)
    {
        abort_unless($request->user() && $request->user()->root_admin, 403);
        $color = ['required', 'regex:/^#[0-9a-fA-F]{6}$/'];
        $data = $request->validate([
            'brand' => ['nullable', 'string', 'max:48'],
            'heading' => ['required', 'string', 'max:64'],
            'links' => ['nullable', 'array', 'max:' . ComicThemeSettings::MAX_LINKS],
            'links.*' => ['array'],
            'links.*.label' => ['nullable', 'string', 'max:64'],
            'links.*.url' => ['nullable', 'string', 'max:2048'],
            'links.*.tone' => ['required', 'in:green,yellow,dark'],
            'links.*.enabled' => ['sometimes', 'boolean'],
            'background_image' => ['nullable', 'file', 'mimetypes:' . implode(',', array_keys(self::IMAGE_MIMES)), 'max:20480'],
            'background_remove' => ['sometimes', 'boolean'],
            'background_overlay' => ['required', 'integer', 'min:0', 'max:90'],
            'welcome_enabled' => ['sometimes', 'boolean'],
            'welcome_title' => ['required', 'string', 'max:64'],
            'welcome_name' => ['nullable', 'string', 'max:64'],
            'welcome_text' => ['nullable', 'string', 'max:240'],
            'title_color' => $color, 'name_color' => $color, 'text_color' => $color, 'accent_color' => $color,
            'overlay' => ['required', 'integer', 'min:0', 'max:90'],
            'banner' => ['nullable', 'file', 'mimetypes:' . implode(',', array_keys(self::MIMES)), 'max:30720'],
            'banner_url' => ['nullable', 'string', 'max:2048'],
            'banner_remove' => ['sometimes', 'boolean'],
            'notice_enabled' => ['sometimes', 'boolean'],
            'notice_title' => ['required', 'string', 'max:64'],
            'notice_text' => ['nullable', 'string', 'max:280'],
            'notice_button_label' => ['nullable', 'string', 'max:40'],
            'notice_url' => ['nullable', 'string', 'max:2048'],
            'notice_show_once' => ['sometimes', 'boolean'],
            'notice_reset' => ['sometimes', 'boolean'],
            'gate_enabled' => ['sometimes', 'boolean'],
            'gate_title' => ['required', 'string', 'max:48'],
            'gate_text' => ['nullable', 'string', 'max:240'],
            'gate_done_label' => ['required', 'string', 'max:32'],
            'gate_require_click' => ['sometimes', 'boolean'],
            'gate_reset' => ['sometimes', 'boolean'],
            'gate_links' => ['nullable', 'array', 'max:' . ComicThemeSettings::MAX_GATE_LINKS],
            'gate_links.*' => ['array'],
            'gate_links.*.label' => ['nullable', 'string', 'max:48'],
            'gate_links.*.url' => ['nullable', 'string', 'max:2048'],
        ]);

        $links = [];
        foreach (($data['links'] ?? []) as $i => $link) {
            $url = trim($link['url'] ?? '');
            $label = trim($link['label'] ?? '');
            $enabled = !empty($link['enabled']);
            if ($url === '' && $label === '' && !$enabled) {
                continue;
            }
            if ($url !== '' && !ComicThemeSettings::safeUrl($url)) {
                throw ValidationException::withMessages(["links.$i.url" => 'Gunakan URL lengkap http:// atau https:// tanpa username/password.']);
            }
            if ($enabled && ($url === '' || $label === '')) {
                throw ValidationException::withMessages(["links.$i.label" => 'Tombol aktif wajib memiliki nama dan URL.']);
            }
            $links[] = ['label' => $label, 'url' => $url, 'tone' => $link['tone'], 'enabled' => $enabled];
        }

        $gateLinks = [];
        foreach (($data['gate_links'] ?? []) as $i => $link) {
            $url = trim($link['url'] ?? '');
            $label = trim($link['label'] ?? '');
            if ($url === '' && $label === '') {
                continue;
            }
            if ($label === '' || !ComicThemeSettings::safeUrl($url)) {
                throw ValidationException::withMessages(["gate_links.$i.url" => 'Link gerbang butuh nama dan URL http(s) yang valid.']);
            }
            $gateLinks[] = ['label' => $label, 'url' => $url];
        }

        $noticeUrl = trim($data['notice_url'] ?? '');
        $noticeButton = trim($data['notice_button_label'] ?? '');
        if ($noticeUrl !== '' && !ComicThemeSettings::safeUrl($noticeUrl)) {
            throw ValidationException::withMessages(['notice_url' => 'Link notifikasi harus URL lengkap http:// atau https://.']);
        }
        if ($noticeUrl !== '' && $noticeButton === '') {
            throw ValidationException::withMessages(['notice_button_label' => 'Nama tombol wajib diisi jika link notifikasi digunakan.']);
        }

        $current = ComicThemeSettings::read();
        $background = (string) ($current['background']['image'] ?? '');
        if ($request->hasFile('background_image')) {
            $file = $request->file('background_image');
            $ext = self::IMAGE_MIMES[$file->getMimeType()] ?? null;
            if (!$ext) {
                throw ValidationException::withMessages(['background_image' => 'Format background tidak didukung. Gunakan JPG, PNG, WEBP, atau GIF.']);
            }
            $dir = public_path('comic-theme/uploads');
            if (!is_dir($dir)) {
                @mkdir($dir, 0755, true);
            }
            if (!is_dir($dir) || !is_writable($dir)) {
                throw ValidationException::withMessages(['background_image' => 'Folder public/comic-theme/uploads tidak bisa ditulis. Jalankan ulang UPDATE-THEME.sh atau chown folder itu ke user web server.']);
            }
            $name = 'background-' . bin2hex(random_bytes(8)) . '.' . $ext;
            $file->move($dir, $name);
            $this->forgetOldBackground($background);
            $background = '/comic-theme/uploads/' . $name;
        } elseif (!empty($data['background_remove'])) {
            $this->forgetOldBackground($background);
            $background = '';
        }

        [$banner, $bannerType] = [$current['welcome']['banner'], $current['welcome']['banner_type']];
        $remove = !empty($data['banner_remove']);
        $bannerUrl = trim($data['banner_url'] ?? '');

        if ($request->hasFile('banner')) {
            $file = $request->file('banner');
            $ext = self::MIMES[$file->getMimeType()] ?? null;
            if (!$ext) {
                throw ValidationException::withMessages(['banner' => 'Format banner tidak didukung.']);
            }
            $dir = public_path('comic-theme/uploads');
            if (!is_dir($dir)) {
                @mkdir($dir, 0755, true);
            }
            if (!is_dir($dir) || !is_writable($dir)) {
                throw ValidationException::withMessages(['banner' => 'Folder public/comic-theme/uploads tidak bisa ditulis. Jalankan ulang UPDATE-THEME.sh atau chown folder itu ke user web server.']);
            }
            $name = 'banner-' . bin2hex(random_bytes(8)) . '.' . $ext;
            $file->move($dir, $name); // nama file dibuat sendiri; ekstensi dari mime sebenarnya, bukan dari nama asli
            $this->forgetOldBanner($banner);
            $banner = '/comic-theme/uploads/' . $name;
            $bannerType = in_array($ext, ['mp4', 'webm'], true) ? 'video' : 'image';
        } elseif ($bannerUrl !== '') {
            if (!ComicThemeSettings::safeUrl($bannerUrl)) {
                throw ValidationException::withMessages(['banner_url' => 'URL banner harus http:// atau https://.']);
            }
            if ($bannerUrl !== $banner) {
                $this->forgetOldBanner($banner);
            }
            $banner = $bannerUrl;
            $bannerType = preg_match('/\.(mp4|webm)(\?.*)?$/i', $bannerUrl) ? 'video' : 'image';
        } elseif ($remove) {
            $this->forgetOldBanner($banner);
            [$banner, $bannerType] = ['', 'none'];
        }

        $gateVersion = (int) $current['gate']['version'] + (!empty($data['gate_reset']) ? 1 : 0);
        $noticeVersion = (int) $current['notice']['version'] + (!empty($data['notice_reset']) ? 1 : 0);

        $settings->set(ComicThemeSettings::KEY, json_encode([
            'brand' => trim($data['brand'] ?? ''),
            'heading' => trim($data['heading']),
            'links' => $links,
            'background' => [
                'image' => $background,
                'overlay' => (int) $data['background_overlay'],
            ],
            'welcome' => [
                'enabled' => !empty($data['welcome_enabled']),
                'title' => trim($data['welcome_title']),
                'name' => trim($data['welcome_name'] ?? ''),
                'text' => trim($data['welcome_text'] ?? ''),
                'title_color' => $data['title_color'],
                'name_color' => $data['name_color'],
                'text_color' => $data['text_color'],
                'accent_color' => $data['accent_color'],
                'overlay' => (int) $data['overlay'],
                'banner' => $banner,
                'banner_type' => $bannerType,
            ],
            'notice' => [
                'enabled' => !empty($data['notice_enabled']),
                'title' => trim($data['notice_title']),
                'text' => trim($data['notice_text'] ?? ''),
                'button_label' => $noticeButton,
                'url' => $noticeUrl,
                'show_once' => !empty($data['notice_show_once']),
                'version' => $noticeVersion,
            ],
            'egg_changer' => $current['egg_changer'],
            'gate' => [
                'enabled' => !empty($data['gate_enabled']),
                'title' => trim($data['gate_title']),
                'text' => trim($data['gate_text'] ?? ''),
                'done_label' => trim($data['gate_done_label']),
                'require_click' => !empty($data['gate_require_click']),
                'version' => $gateVersion,
                'links' => $gateLinks,
            ],
        ], JSON_THROW_ON_ERROR));
        return redirect()->route('admin.settings.comic-links')->with('comic_saved', true);
    }

    /** Hanya menghapus background yang diunggah lewat panel ini (di folder uploads). */
    private function forgetOldBackground(string $path): void
    {
        if (preg_match('#^/comic-theme/uploads/background-[0-9a-f]{16}\.(jpg|png|webp|gif)$#', $path)) {
            @unlink(public_path(ltrim($path, '/')));
        }
    }

    /** Hanya menghapus file yang diunggah lewat panel ini (di folder uploads). */
    private function forgetOldBanner(string $path): void
    {
        if (preg_match('#^/comic-theme/uploads/banner-[0-9a-f]{16}\.(jpg|png|webp|gif|mp4|webm)$#', $path)) {
            @unlink(public_path(ltrim($path, '/')));
        }
    }
}
