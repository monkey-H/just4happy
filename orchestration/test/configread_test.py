import sys

from orchestration.config import parse_yml

if __name__ == '__main__':
    print sys.path[0]
    data = parse_yml.read(sys.path[0])

    for item in data:
        print item
        for key in item:
            print key, 'correspond to', item[key]
