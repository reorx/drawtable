# -*- coding: utf-8 -*-

import sys
import pytest
import subprocess


PY2 = sys.version_info.major == 2


@pytest.fixture
def datadir():
    import os

    class datadir:
        base_dir = os.path.dirname(__file__)
        csv_dir_name = os.path.basename(__file__).split('.')[0]
        csv_dir = os.path.join(base_dir, csv_dir_name)

        def path(self, filename):
            return os.path.join(self.csv_dir, filename)

        def content(self, filename):
            with open(self.path(filename), 'r') as f:
                content = f.read()
                return content

    return datadir()


def do_csvless(filepath, extra_args=None, with_coverage=True):
    """
    :return: stdout
    :rtype: string for both python 2 and 3
    """
    # NOTE cwd must be root of the project to run this test
    args = ['-m', 'drawtable.csvless', '-w', '12']
    if with_coverage:
        args = ['coverage', 'run', '-a'] + args
    if extra_args is not None:
        args.extend(extra_args)
    args.append(filepath)
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    assert p.returncode == 0, '{} failed: {}, {}'.format(args, out, err)
    if PY2:
        return out
    return out.decode()


testdata = [
    ('generic', ['-s', 'base']),
    ('generic', ['-s', 'base', '-n']),
    ('generic', ['-s', 'box']),
    ('generic', ['-s', 'box', '-n']),
    ('generic', ['-s', 'markdown']),
    ('generic', ['-s', 'markdown', '-n']),
    ('generic', ['-s', 'rst-grid']),
    ('generic', ['-s', 'rst-grid', '-n']),
]


@pytest.mark.parametrize('name,extra_args', testdata)
def test_csvless(name, extra_args, datadir):
    """
    In subprocess, `less` behaves exactly as `cat` does
    """
    csv_filename = name + '.csv'

    fragments = []
    for i in extra_args:
        fragments.append(i.replace('-', ''))
    txt_filename = name + '_' + '_'.join(fragments) + '.txt'

    print('txt_filename={}'.format(txt_filename))
    get = do_csvless(datadir.path(csv_filename), extra_args)
    want = datadir.content(txt_filename)
    assert get == want


def test_csvless_cat(datadir):
    """
    test if `--cat` makes any difference
    """
    assert do_csvless(datadir.path('generic.csv'), ['--cat', '-s', 'markdown', '-n']) == datadir.content('generic_s_markdown_n.txt')
