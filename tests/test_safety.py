"""Tests are non-destructive; no package or service commands are executed."""
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'installer'))
import deploy
import license_gate
import hashlib
license_gate.LICENSE_DIGEST = hashlib.sha256(b"test-only-license").hexdigest()

BASE=Path(__file__).resolve().parents[1]
VALID={'license_key':'test-only-license','domain':'panel.example.com','email':'admin@example.com','username':'admin','password':'AbCd1234!EFgh5678','db_password':'DbSecret1234567890AbCd!','location':'Jakarta-01','brand':'BOLT HOST','acme_agree':True}
class Safety(unittest.TestCase):
    def test_license_rejection(self):
        for mode in license_gate.LICENSE_MODES:
            for key in [None, "", "WRONG", 123]:
                with self.subTest(mode=mode, key=key), self.assertRaises(ValueError):
                    deploy.validate(mode, dict(VALID, license_key=key))
        self.assertEqual(deploy.validate("update", VALID)["license_key"], "test-only-license")

    def test_validation(self):
        self.assertEqual(deploy.validate('both',VALID)['domain'],'panel.example.com')
        for field,payload in [('domain','a.com; touch /tmp/no'),('domain','../../root'),('email','x@x.com\nAPP_KEY=oops'),('username','$(id)'),('password',"Password1234567'--"),('location','x\nfoo'),('brand','<script>')]:
            with self.subTest(field=field,payload=payload):
                with self.assertRaises(ValueError):deploy.validate('both',dict(VALID,**{field:payload}))
        with self.assertRaises(ValueError):deploy.validate('both',dict(VALID,acme_agree=False))
        with self.assertRaises(ValueError):deploy.validate('restore',{'backup':'../../etc/passwd'})
        with self.assertRaises(ValueError):deploy.validate('execute',{})
    def test_tar_traversal(self):
        with tempfile.TemporaryDirectory() as t:
            t=Path(t)
            for name in ['../escape','/absolute']:
                a=t/'bad.tar.gz'
                with tarfile.open(a,'w:gz') as tf:
                    info=tarfile.TarInfo(name);info.size=1;tf.addfile(info,io.BytesIO(b'x'))
                with self.assertRaises(ValueError):deploy.safe_extract(a,t/'out')
            a=t/'links.tar.gz'
            with tarfile.open(a,'w:gz') as tf:
                info=tarfile.TarInfo('link');info.type=tarfile.SYMTYPE;info.linkname='/etc/passwd';tf.addfile(info)
            with self.assertRaises(tarfile.FilterError):deploy.safe_extract(a,t/'out')
    def test_secret_redaction_and_argv(self):
        events=[];w=deploy.Deployment('panel',VALID,lambda k,v:events.append((k,v)))
        w.run([sys.executable,'-c',"import sys; print(sys.stdin.read()); print('APP_KEY=base64:secret')"],input_text=VALID['password'])
        log=json.dumps(events)
        self.assertNotIn(VALID['password'],log);self.assertNotIn('base64:secret',log);self.assertIn('REDACTED',log)
        with self.assertRaises(RuntimeError):w.run([sys.executable,'-c','raise SystemExit(7)'])
        with self.assertRaises(TimeoutError):w.run([sys.executable,'-c','import time;time.sleep(4)'],timeout=.2)
    def test_worker_failure_stops_remaining_steps(self):
        events=[];called=[];w=deploy.Deployment('panel',VALID,lambda k,v:events.append((k,v)))
        def fail():raise RuntimeError('expected')
        w.plan=lambda:[('first',1,lambda:called.append(1)),('fail',2,fail),('never',3,lambda:called.append(3))]
        with self.assertRaises(RuntimeError):w.execute()
        self.assertEqual(called,[1]);self.assertFalse(any(k=='done' and v['index']==2 for k,v in events))
    def test_theme_idempotent_and_reversible(self):
        spec=importlib.util.spec_from_file_location('theme',BASE/'theme/install-theme.py');theme=importlib.util.module_from_spec(spec);spec.loader.exec_module(theme)
        with tempfile.TemporaryDirectory() as t:
            panel=Path(t);(panel/'artisan').write_text('test');(panel/'public').mkdir();(panel/'routes').mkdir();(panel/'routes/admin.php').write_text('<?php\n// existing admin routes\n');(panel/'routes/base.php').write_text("<?php\nuse Illuminate\\Support\\Facades\\Route;\nRoute::get('/', fn()=>null);\n")
            for f in theme.TARGETS:
                p=panel/f;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('<html><head>original</head><body>retain core</body></html>')
            mask=os.umask(0o077)
            try:theme.install(panel);theme.install(panel)
            finally:os.umask(mask)
            self.assertEqual((panel/'public/comic-theme').stat().st_mode&0o777,0o755)
            self.assertEqual((panel/'public/comic-theme/comic.css').stat().st_mode&0o777,0o644)
            for f in theme.TARGETS:
                text=(panel/f).read_text();self.assertEqual(text.count(theme.START),1);self.assertIn('retain core',text)
            self.assertEqual((panel/'routes/admin.php').read_text().count(theme.ROUTE_START),1)
            self.assertEqual((panel/'routes/base.php').read_text().count(theme.CLIENT_ROUTE_START),1)
            self.assertIn("require __DIR__ . '/comic-client.php';",(panel/'routes/base.php').read_text())
            self.assertIn('comic-csrf',(panel/theme.TARGETS[0]).read_text())
            self.assertIn('comic-theme-config',(panel/theme.TARGETS[0]).read_text())
            self.assertIn('comic-user',(panel/theme.TARGETS[0]).read_text())
            for dest in theme.MODULES.values():self.assertTrue((panel/dest).is_file())
            before={f:(panel/f).read_text() for f in theme.TARGETS}
            (panel/'routes/admin.php').unlink()
            with self.assertRaises(ValueError):theme.install(panel)
            self.assertEqual(before,{f:(panel/f).read_text() for f in theme.TARGETS})
            (panel/'routes/admin.php').write_text('<?php\n// existing admin routes\n'+theme.ROUTE_START+"\nrequire __DIR__ . '/comic-theme.php';\n"+theme.ROUTE_END+'\n')
            theme.install(panel,True)
            self.assertNotIn(theme.START,(panel/theme.TARGETS[0]).read_text())
            self.assertNotIn(theme.ROUTE_START,(panel/'routes/admin.php').read_text())
            self.assertNotIn(theme.CLIENT_ROUTE_START,(panel/'routes/base.php').read_text())
            self.assertIn('// existing admin routes',(panel/'routes/admin.php').read_text())
            self.assertTrue((panel/'app/Support/ComicThemeSettings.php').is_file())
    def test_requested_theme_features_present(self):
        js=(BASE/'theme/comic.js').read_text()
        settings=(BASE/'theme/backend/ComicThemeSettings.php').read_text()
        blade=(BASE/'theme/backend/comic-links.blade.php').read_text()
        self.assertNotIn('API PTLC (Client)',js)
        self.assertNotIn('API PTLA (Application)',js)
        self.assertIn('comic-notice-board',js)
        self.assertIn("location.pathname.startsWith('/admin/')",js)
        self.assertNotIn("location.pathname!=='/'||!n.enabled",js)
        self.assertIn('comic-user',js)
        self.assertIn("'notice' => [",settings)
        self.assertIn('notice_button_label',blade)
        self.assertIn('notice_url',blade)
        self.assertIn('{user}',blade)
        self.assertIn("'background' => [",settings)
        self.assertIn('background_image',blade)
        self.assertIn('background_overlay',blade)
        self.assertIn('applyPanelBackground',js)
        self.assertIn('background-[0-9a-f]{16}',(BASE/'theme/backend/ComicThemeController.php').read_text())
        routes=(BASE/'theme/backend/comic-routes.php').read_text()
        client_routes=(BASE/'theme/backend/comic-client-routes.php').read_text()
        egg_controller=(BASE/'theme/backend/ComicEggChangerController.php').read_text()
        client_controller=(BASE/'theme/backend/ComicClientEggChangerController.php').read_text()
        egg_blade=(BASE/'theme/backend/comic-egg-changer.blade.php').read_text()
        self.assertIn('admin.settings.egg-changer',routes)
        self.assertNotIn('admin.servers.egg-changer',routes)
        self.assertIn('ComicSecuritySettings::isOwner',egg_controller)
        self.assertIn("'nest_ids'",egg_controller)
        self.assertIn('/comic-theme/client/servers/{identifier}/egg-changer',client_routes)
        self.assertIn('StartupModificationService',client_controller)
        self.assertIn('ServerVariable::query()->where',client_controller)
        self.assertIn('lockForUpdate()',client_controller)
        self.assertIn('(int) $egg->nest_id !== (int) $server->nest_id',client_controller)
        self.assertIn('(int) $server->owner_id === (int) $user->id',client_controller)
        self.assertIn('DaemonServerRepository',client_controller)
        self.assertIn('Pilih ID Nest',egg_blade)
        self.assertNotIn('Pilih Server',egg_blade)
        self.assertIn('data-comic-client-egg',js)
        self.assertNotIn('data-comic-server-egg-tab',js)

    def test_wrong_system_refused_without_commands(self):
        w=deploy.Deployment('panel',VALID,lambda *a:None)
        with patch.object(deploy,'system_info',return_value={'errors':['Unsupported OS']}),patch.object(w,'run') as run:
            with self.assertRaises(RuntimeError):w.check()
            run.assert_not_called()
    def test_backups_require_digest(self):
        with tempfile.TemporaryDirectory() as t,patch.object(deploy,'BACKUPS',Path(t)):
            p=Path(t)/'backup-2026-10-04T01-00-00-abcdef01.tar.gz';p.write_bytes(b'backup')
            self.assertEqual(deploy.list_backups(),[])
            Path(str(p)+'.sha256').write_text(deploy.sha256(p))
            w=deploy.Deployment('backup',{},lambda *a:None);self.assertEqual(w.verify_backup(p.name),p)
            p.write_bytes(b'tampered')
            with self.assertRaises(RuntimeError):w.verify_backup(p.name)
if __name__=='__main__':unittest.main(verbosity=2)


def test_egg_changer_mobile_switch_and_nest_touch_safe():
    blade = (BASE / "theme/backend/comic-egg-changer.blade.php").read_text()
    css = (BASE / "theme/comic.css").read_text()
    assert 'id="comic-user-egg-enabled"' in blade
    assert 'for="comic-user-egg-enabled"' in blade
    assert 'comic-egg-switch-input' in blade
    assert 'comic-egg-switch-ui' in blade
    assert 'comic-egg-native-check' in blade
    assert '.comic-egg-switch-input:checked + .comic-egg-switch-ui' in css
    assert 'touch-action:manipulation!important' in css
    assert '-webkit-appearance:auto!important' in css
    assert 'pointer-events:auto!important' in css
