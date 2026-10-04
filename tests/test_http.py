import json
import sys
import threading
import unittest
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'installer'))
import server

class HTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.http=server.ThreadingHTTPServer(('127.0.0.1',0),server.Handler);server.PORT=cls.http.server_address[1]
        cls.url=f'http://127.0.0.1:{server.PORT}';threading.Thread(target=cls.http.serve_forever,daemon=True).start()
    @classmethod
    def tearDownClass(cls):cls.http.shutdown();cls.http.server_close()
    def req(self,path,headers=None,data=None):
        try:r=urlopen(Request(self.url+path,headers=headers or {},data=data),timeout=3);return r.status,r.read(),r.headers
        except HTTPError as e:return e.code,e.read(),e.headers
    def test_private_api_and_source(self):
        self.assertEqual(self.req('/api/state')[0],401)
        self.assertEqual(self.req('/api/state',{'Authorization':'Bearer '+server.AUTH})[0],200)
        for path in ['/../installer/deploy.py','/installer/server.py','/../README-ID.md']:
            self.assertEqual(self.req(path)[0],404)
    def test_host_and_origin(self):
        self.assertEqual(self.req('/',{'Host':'evil.example'})[0],403)
        h={'Authorization':'Bearer '+server.AUTH,'Origin':'http://evil.example','Content-Type':'application/json'}
        self.assertEqual(self.req('/api/run',h,b'{}')[0],403)
        h['Origin']=self.url
        self.assertEqual(self.req('/api/run',h,b'{}')[0],403) # preview refuses mutations even with correct authentication
    def test_asset_headers(self):
        status,body,headers=self.req('/')
        self.assertEqual(status,200);self.assertIn(b'COMIC',body.upper());self.assertEqual(headers['X-Frame-Options'],'DENY');self.assertEqual(headers['Cache-Control'],'no-store')
if __name__=='__main__':unittest.main(verbosity=2)
