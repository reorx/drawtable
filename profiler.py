import os
import sys
from drawbox.csvless.__main__ import main


if __name__ == '__main__':
    raw_args = list(sys.argv[1:])
    raw_args.extend([
        '--cat', '-n', '-s', 'markdown'
    ])

    print(raw_args)
    null = open(os.devnull, 'w')

    def writer(s):
        null.write(s)

    print('--- csvless main start ---')
    box = main(args=raw_args, writer=writer)
    print('--- csvless main end ---')
    print('draw_result={}'.format(box.draw_result))
    null.close()
