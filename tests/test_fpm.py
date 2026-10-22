"""Exercise real FPM workers over a private Unix FastCGI socket."""
import json
import os
import socket
import struct
import subprocess
import tempfile
import time
import unittest
from php_runtime import isolated_options


def record(kind, content):
    return struct.pack('!BBHHBB', 1, kind, 1, len(content), 0, 0) + content


def encoded_length(value):
    if value < 128:
        return bytes([value])
    return struct.pack('!I', value | 0x80000000)


def receive(connection, size):
    data = b''
    while len(data) < size:
        chunk = connection.recv(size - len(data))
        if not chunk:
            raise RuntimeError('FPM closed the connection before END_REQUEST')
        data += chunk
    return data


class FpmIntegrationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory(prefix='php-backport-fpm-')
        cls.root = cls.directory.name
        os.chmod(cls.root, 0o755)
        cls.address = os.path.join(cls.root, 'fpm.sock')
        cls.script = os.path.join(cls.root, 'probe.php')
        session_path = os.path.join(cls.root, 'sessions')
        os.mkdir(session_path)
        os.chmod(session_path, 0o777)
        with open(cls.script, 'w') as target:
            target.write('''<?php
                session_start();
                header('Content-Type: application/json');
                $files = array();
                foreach ($_FILES as $key => $file) {
                    $files[$key] = array('name' => $file['name'],
                        'size' => $file['size'], 'error' => $file['error']);
                }
                echo json_encode(array('pid' => getmypid(), 'post' => $_POST,
                    'files' => $files, 'session' => $_SESSION));
            ''')
        configuration = os.path.join(cls.root, 'fpm.conf')
        with open(configuration, 'w') as target:
            target.write('''[global]
error_log = {root}/fpm.log
daemonize = no
[probe]
user = nobody
group = nogroup
listen = {socket}
pm = static
pm.max_children = 1
pm.max_requests = 0
catch_workers_output = yes
request_terminate_timeout = 10s
php_admin_value[session.save_path] = {sessions}
php_admin_flag[session.upload_progress.enabled] = on
php_admin_flag[session.upload_progress.cleanup] = off
'''.format(root=cls.root, socket=cls.address, sessions=session_path))
        cls.log = open(os.path.join(cls.root, 'process.log'), 'wb')
        cls.process = subprocess.Popen(
            [os.environ['FPM_UNDER_TEST']] + isolated_options() + ['-F', '-y', configuration],
            stdout=cls.log, stderr=cls.log)
        for _ in range(100):
            if os.path.exists(cls.address):
                return
            if cls.process.poll() is not None:
                break
            time.sleep(0.05)
        cls.log.close()
        with open(os.path.join(cls.root, 'process.log'), 'r') as source:
            detail = source.read()
        cls.tearDownClass()
        raise RuntimeError('FPM did not start: ' + detail)

    @classmethod
    def tearDownClass(cls):
        if cls.process.poll() is None:
            cls.process.terminate()
            try:
                cls.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                cls.process.kill()
                cls.process.wait(timeout=5)
        cls.log.close()
        # Worker-owned session files need parent/root cleanup inside the container.
        cls.directory.cleanup()

    def request(self, body, content_type, cookie=''):
        params = {
            'GATEWAY_INTERFACE': 'CGI/1.1', 'SERVER_PROTOCOL': 'HTTP/1.1',
            'REQUEST_METHOD': 'POST', 'SCRIPT_FILENAME': self.script,
            'SCRIPT_NAME': '/probe.php', 'REQUEST_URI': '/probe.php',
            'DOCUMENT_ROOT': self.root, 'SERVER_NAME': 'localhost',
            'REMOTE_ADDR': '127.0.0.1', 'SERVER_PORT': '80',
            'CONTENT_LENGTH': str(len(body)), 'CONTENT_TYPE': content_type,
            'HTTP_COOKIE': cookie}
        encoded = b''
        for key, value in params.items():
            key, value = key.encode(), value.encode()
            encoded += encoded_length(len(key)) + encoded_length(len(value))
            encoded += key + value
        output, errors = b'', b''
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
            connection.settimeout(15)
            connection.connect(self.address)
            connection.sendall(record(1, struct.pack('!HB5x', 1, 0)))
            connection.sendall(record(4, encoded) + record(4, b''))
            for offset in range(0, len(body), 65535):
                connection.sendall(record(5, body[offset:offset + 65535]))
            connection.sendall(record(5, b''))
            while True:
                version, kind, request_id, length, padding, reserved = struct.unpack(
                    '!BBHHBB', receive(connection, 8))
                self.assertEqual((version, request_id), (1, 1))
                content = receive(connection, length)
                receive(connection, padding)
                if kind == 6:
                    output += content
                elif kind == 7:
                    errors += content
                elif kind == 3:
                    self.assertEqual(struct.unpack('!IB3x', content), (0, 0))
                    break
        self.assertEqual(errors, b'')
        headers, body = output.split(b'\r\n\r\n', 1)
        self.assertNotIn(b'Status: 5', headers)
        return json.loads(body.decode())

    def test_nested_post_values_survive_worker_reuse(self):
        first = self.request(b'rows[0][name]=first&rows[1][name]=second',
                             'application/x-www-form-urlencoded')
        second = self.request(b'rows[0][name]=fresh',
                              'application/x-www-form-urlencoded')
        self.assertEqual(first['pid'], second['pid'])
        self.assertEqual(first['post']['rows'], [{'name': 'first'}, {'name': 'second'}])
        self.assertEqual(second['post']['rows'], [{'name': 'fresh'}])

    def test_uploads_work_without_session_upload_progress_state(self):
        body = (b'--boundary\r\nContent-Disposition: form-data; '
                b'name="PHP_SESSION_UPLOAD_PROGRESS"\r\n\r\nprobe\r\n'
                b'--boundary\r\nContent-Disposition: form-data; '
                b'name="attachment"; filename="sample.txt"\r\n'
                b'Content-Type: text/plain\r\n\r\nabc\r\n--boundary--\r\n')
        response = self.request(body, 'multipart/form-data; boundary=boundary',
                                'PHPSESSID=backportprobesession')
        self.assertEqual(response['files']['attachment'],
                         {'name': 'sample.txt', 'size': 3, 'error': 0})
        self.assertNotIn('upload_progress_probe', response['session'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
