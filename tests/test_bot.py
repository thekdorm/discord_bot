import unittest
<<<<<<< HEAD
from .. import linker

link = linker.Linker.link_post()


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(len(link('aww', 'top')), 1)
=======
from ..bot import linker

test = linker.Linker()

# Work in progress, not meant to be used yet


class LinkerTest(unittest.TestCase):
    def test_time_filter(self, mode, t):
        for t in ['yasdf', 0, '']:
            with self.assertRaises(ValueError):
                # test.link_post(sub='aww', mode=mode, time_filter=t)
                print(f'Testing {t} for mode top')
                test.link_post(sub='aww', mode='top', time_filter=t)
            with self.assertRaises(ValueError):
                print(f'Testing {t} for mode controversial')
                test.link_post(sub='aww', mode='controversial', time_filter=t)
>>>>>>> 4708207691370c5ee84f1b537bee9ebb0d914ef0


if __name__ == '__main__':
    unittest.main()
