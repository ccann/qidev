import os

path = os.path.join(os.path.expanduser('~'), '.qidev')


def write_hostname(hostname):
    with open(path, 'w+') as f:
        f.write('hostname: {}'.format(hostname))


def read_hostname():
    with open(path, 'r') as f:
        for line in f:
            if line.startswith('hostname:'):
                try:
                    return line.split('hostname:')[1].strip()
                except IndexError:
                    pass
    return None
