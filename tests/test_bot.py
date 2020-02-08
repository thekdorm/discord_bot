import unittest
from .. import linker

link = linker.Linker.link_post()


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(len(link('aww', 'top')), 1)


if __name__ == '__main__':
    unittest.main()
