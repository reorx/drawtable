import timeit


setup = '''
import os
import sys
from drawbox.csvless.__main__ import _main


def main():
    raw_args = list(sys.argv[1:])
    raw_args.extend([
        '--cat', '-n', '-s', 'markdown'
    ])

    null = open(os.devnull, 'w')

    def writer(s):
        null.write(s)

    box = _main(args=raw_args, writer=writer)
    print('  draw_result={}'.format(box.draw_result))
    null.close()
'''


if __name__ == '__main__':
    run_number = 10
    print('start running for {} times'.format(run_number))
    total_time = timeit.timeit('main()', setup=setup, number=10)
    avg_time = total_time / run_number
    print('average time: {:.3f}s'.format(avg_time))
