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
                content = f.read().strip()
                return content

    return datadir()


def do_csvless(filepath, extra_args=None):
    """
    :return: stdout
    :rtype: string for both python 2 and 3
    """
    args = ['csvless', '--cat', '-w', '12']
    if extra_args is not None:
        args.extend(extra_args)
    args.append(filepath)
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    out, err = p.communicate()
    assert p.returncode == 0, '{} failed: {}, {}'.format(args, out, err)
    out = out.strip()
    if PY2:
        return out
    return out.decode()


testdata = [
    ('generic', ['-s', 'box']),
]


@pytest.mark.parametrize('name,extra_args', testdata)
def test_csvless(name, extra_args, datadir):
    csv_filename = name + '.csv'
    txt_filename = name + '.txt'
    assert do_csvless(datadir.path(csv_filename), extra_args) == datadir.content(txt_filename)
