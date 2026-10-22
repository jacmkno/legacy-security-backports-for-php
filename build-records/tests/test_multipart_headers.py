"""Multipart header retention regressions against real private FPM workers.

Run with FPM_UNDER_TEST=/path/to/php-fpm python3 tests/test_multipart_headers.py.
The flood cases detect removal of filtering and deduplication independently;
ordinary upload success alone is only compatibility evidence.
"""
import unittest

import test_fpm


class MultipartHeadersTest(test_fpm.FpmIntegrationTest):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        with open(cls.script, 'w') as target:
            target.write('''<?php
                header('Content-Type: application/json');
                $files = array();
                foreach ($_FILES as $key => $file) {
                    $files[$key] = array('name' => $file['name'],
                        'type' => $file['type'], 'size' => $file['size'],
                        'error' => $file['error']);
                }
                echo json_encode(array('pid' => getmypid(), 'post' => $_POST,
                    'files' => $files, 'session' => array(),
                    'peak' => memory_get_peak_usage(true)));
            ''')

    # These inherited cases use the original probe's response contract.
    test_nested_post_values_survive_worker_reuse = None
    test_uploads_work_without_session_upload_progress_state = None

    def upload(self, extra=b'', leading=b''):
        body = (b'--headers-probe\r\n' + leading +
                b'Content-Disposition: form-data; name="attachment"; '
                b'filename="first.txt"\r\nContent-Type: text/plain\r\n' +
                extra + b'\r\nabc\r\n--headers-probe--\r\n')
        response = self.request(body, 'multipart/form-data; boundary=headers-probe')
        self.assertEqual(response['post'], [])
        self.assertEqual(response['files'], {'attachment': {
            'name': 'first.txt', 'type': 'text/plain', 'size': 3, 'error': 0}})
        return response

    def test_ignored_headers_and_their_continuations(self):
        self.upload(
            leading=b'X-Ignored: before\r\n continuation-before\r\n',
            extra=b'X-Ignored: after\r\n ; filename="poison.txt"\r\n'
                  b'\tcontinuation-after\r\n')

    def test_mixed_case_duplicates_preserve_first_headers(self):
        self.upload(extra=
                    b'cOnTeNt-dIsPoSiTiOn: form-data; name="poison"; '
                    b'filename="second.txt"\r\n'
                    b' ; filename="third.txt"\r\n'
                    b'cOnTeNt-tYpE: application/poison\r\n'
                    b' ignored-continuation\r\n')

    def assert_bounded_retention(self, header):
        small = self.upload(extra=header % 0)
        large = self.upload(extra=b''.join(header % i for i in range(20000)))
        self.assertEqual(small['pid'], large['pid'])
        # The wire input grows by >3 MB; retained header allocations must not.
        self.assertLessEqual(large['peak'] - small['peak'], 1024 * 1024,
                             'multipart headers retained proportional memory: '
                             'small=%d large=%d' % (small['peak'], large['peak']))

    def test_ignored_header_memory_is_bounded(self):
        # Unique names keep deduplication from masking a missing header filter.
        self.assert_bounded_retention(b'X-Ignored-%08d: ' + b'x' * 160 + b'\r\n')

    def test_duplicate_disposition_memory_is_bounded(self):
        self.assert_bounded_retention(
            b'cOnTeNt-dIsPoSiTiOn: form-data; name="poison"; filename="' +
            b'x' * 160 + b'%08d"\r\n')

    def test_duplicate_type_memory_is_bounded(self):
        self.assert_bounded_retention(b'cOnTeNt-tYpE: application/' +
                                      b'x' * 160 + b'%08d\r\n')


if __name__ == '__main__':
    unittest.main(verbosity=2)
