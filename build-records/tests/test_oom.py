"""Regression probe for the legacy vendor patch's hard-OOM behavior."""
import os
import subprocess
import unittest
from php_runtime import isolated_options


class OomShutdownTest(unittest.TestCase):
    def test_memory_exhaustion_terminates_before_shutdown_callbacks(self):
        executable = os.environ.get('PHP_UNDER_TEST', 'php')
        fixture = os.path.join(os.path.dirname(__file__), 'oom_shutdown.php')
        process = subprocess.Popen(
            [executable] + isolated_options() + ['-d', 'memory_limit=8M', fixture],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=15)
        self.assertIn(b'Allowed memory size', stdout + stderr)
        self.assertNotIn(b'UNSAFE_SHUTDOWN_CALLBACK', stdout + stderr)
        self.assertNotIn(b'UNEXPECTED_SUCCESS', stdout + stderr)
        self.assertEqual(process.returncode, 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
