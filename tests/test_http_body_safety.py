"""Real loopback HTTP: incomplete/slow bodies do not create login sessions."""
import http.client
import json
import socket
import threading
import unittest
from http.server import ThreadingHTTPServer
from unittest.mock import patch

from hibe.server import App, handler
from hibe.service import Service
from hibe.store import MemoryStore


class HTTPBodySafetyTests(unittest.TestCase):
    def setUp(self):
        self.app = object.__new__(App)
        self.app.demo = True
        self.app.sessions = {}
        self.app.lock = threading.Lock()
        self.app.service = Service(MemoryStore(), 'demo-admin', demo=True)
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), handler(self.app))
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def raw_request(self, length, body, half_close=False):
        with socket.create_connection(self.server.server_address, timeout=2) as client:
            client.sendall(('POST /api/demo-login HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/json\r\nContent-Length: '+str(length)+'\r\n\r\n').encode() + body)
            if half_close:
                client.shutdown(socket.SHUT_WR)
            response = http.client.HTTPResponse(client)
            response.begin()
            payload = json.loads(response.read())
            return response.status, payload

    def test_stalled_body_times_out_and_normal_request_still_works(self):
        with patch('hibe.server.POST_BODY_TIMEOUT', 0.1):
            code, payload = self.raw_request(100, b'')
        self.assertEqual(code, 408)
        self.assertIn('zamanında', payload['error'])
        self.assertEqual(self.app.sessions, {})
        body = b'{"role":"user"}'
        self.assertEqual(self.raw_request(len(body), body)[0], 200)

    def test_partial_body_rejected_before_creating_session(self):
        code, payload = self.raw_request(100, b'{}', half_close=True)
        self.assertEqual(code, 400)
        self.assertEqual(payload['error'], 'İstek gövdesi eksik')
        self.assertEqual(self.app.sessions, {})

    def test_json_array_scalar_and_null_are_client_errors(self):
        for body in (b'[]', b'null', b'1', b'"text"'):
            with self.subTest(body=body):
                code, payload = self.raw_request(len(body), body)
                self.assertEqual(code, 400)
                self.assertEqual(payload['error'], 'JSON nesnesi gerekli')
        self.assertEqual(self.app.sessions, {})
