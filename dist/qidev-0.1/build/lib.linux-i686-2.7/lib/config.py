import os
import json

path = os.path.join(os.path.expanduser('~'), '.qidev')


def read_field(field):
    """Read .qidev json file."""
    if not os.path.exists(path):
        return None
    else:
        with open(path, 'r') as json_file:
            try:
                data = json.load(json_file)
                return data[field]
            except:
                return None


def write_field(field, value):
    """Write field value pair to .qidev json file."""
    if not os.path.exists(path):
        with open(path, 'w+') as json_file:
            data = {field: value}
            json.dump(data, json_file)
    else:
        with open(path, 'r') as json_file:
            data = json.load(json_file)
        with open(path, 'w+') as json_file:
            data[field] = value
            json.dump(data, json_file)
