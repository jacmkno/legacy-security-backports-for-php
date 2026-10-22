"""Exercise the parser and VM paths changed by the legacy security patch."""
import json
import os
import subprocess
import unittest
from php_runtime import isolated_options


class CoreCompatibilityTest(unittest.TestCase):
    def run_php(self, source):
        process = subprocess.Popen(
            [os.environ.get('PHP_UNDER_TEST', 'php')] + isolated_options() + ['-r', source],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(timeout=15)
        self.assertEqual(process.returncode, 0, stderr.decode('utf-8', 'replace'))
        self.assertEqual(stderr, b'')
        return json.loads(stdout.decode('utf-8'))

    def test_nested_input_arrays_grow_and_preserve_values(self):
        result = self.run_php('''
            $pairs = array();
            for ($i = 0; $i < 100; $i++) {
                $pairs[] = 'records[' . $i . '][name]=item' . $i;
            }
            parse_str(implode('&', $pairs), $parsed);
            echo json_encode(array(count($parsed['records']),
                $parsed['records'][0]['name'], $parsed['records'][99]['name']));
        ''')
        self.assertEqual(result, [100, 'item0', 'item99'])

    def test_input_scalar_can_be_replaced_by_nested_arrays(self):
        result = self.run_php('''
            parse_str('field=old&field[nested][value]=new&list[]=a&list[]=b', $out);
            echo json_encode($out);
        ''')
        self.assertEqual(result, {'field': {'nested': {'value': 'new'}},
                                  'list': ['a', 'b']})

    def test_concatenation_preserves_all_operand_forms(self):
        result = self.run_php('''
            function temporary() { return 'ab'; }
            $a = 'ab'; $b = 'cd'; $empty = '';
            $out = array($a . $b, 'ab' . $b, $a . 'cd', temporary() . $b,
                $empty . $b, $a . $empty, $a . 12, $a . false);
            $a .= $b;
            $out[] = $a;
            echo json_encode($out);
        ''')
        self.assertEqual(result, ['abcd', 'abcd', 'abcd', 'abcd', 'cd',
                                  'ab', 'ab12', 'ab', 'abcd'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
