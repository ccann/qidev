def get_pack_name(p):
    try:
        name = p['elems']['names']['en_US']
    except KeyError:
        try:
            name = p['langToName']['en_US']
        except KeyError:
            name = p['uuid']
    return name


def get_beh_name(b):
    try:
        name = b['langToName']['en_US']
    except KeyError:
        name = b['path']
    return name


def get_serv_name(s):
    return s['name']


def get_naoqi_reqs(p):
    try:
        print p['elems']['requirements']
        nr = p['elems']['requirements'][1][0]
    except (KeyError, IndexError):
        try:
            nr = p['naoqiRequirements'][0]
        except (KeyError, IndexError):
            return 'unspecified', ''
    mn = nr['minVersion']
    mx = ' to {}'.format(nr['maxVersion']) if nr['maxVersion'] else ' +'
    return mn, mx


def get_supported_languages(p):
    try:
        return p['elems']['supportedLanguages']
    except KeyError:
        return p['supportedLanguages']


def get_description(p):
    try:
        return p['elems']['descriptions']['en_US']
    except KeyError:
        return p['langToDesc']['en_US']


def get_pack_behs(p):
    try:
        return p['elems']['contents']['behaviors']
    except KeyError:
        return p['behaviors']


def get_pack_servs(p):
    try:
        elems = p['elems']
        try:
            return elems['services']
        except KeyError:
            return list()
    except KeyError:
        return p['services']
