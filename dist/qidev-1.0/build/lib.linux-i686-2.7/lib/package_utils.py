"""
Utilities for working with ALPackageManager.

This script provides functions to extract elements from the packages list
returned by PackageManager.packages(). It is intended to allow the developer to
be agnostic to the version of the PackageManager API (i.e. packages() and
packages2())

"""
import re
import os
import qi

# Example PACKAGE_2
PACKAGE_2 = {
    "uuid": "robot-control",
    "version": "0.0.3",
    "author": "",
    "channel": "",
    "organization": "",
    "date": "",
    "typeVersion": "",
    "installer": "cloud.aldebaran-robotics.com",
    "path": "/home/nao/.local/share/PackageManager/apps/robot-control",
    "elems": {
        "names": {"en_US": "Robot Control"},
        "contents": {
            "behaviors": [
                {
                    "path": "animations/head_leds",
                    "nature": "interactive",
                    "langToName": {},
                    "langToDesc": {},
                    "categories": "",
                    "langToTags": {},
                    "langToTriggerSentences": {},
                    "langToLoadingResponses": {},
                    "purposeToCondition": {},
                    "permissions": []
                }
            ]
        },  # closes contents
        "services": [
            {
                "execStart": "/usr/bin/python2 lib/robot_control.py",
                "name": "RobotControl-serv",
                "autoRun": True
            }
        ],
        "descriptions": {"en_US": "Allow ..."},
        "requirements": [
            [
                {"model": "", "minHeadVersion": "", "maxHeadVersion": "",
                 "minBodyVersion": "", "maxBodyVersion": ""}
            ],
            [
                {"minVersion": "2.1.0.19", "maxVersion": ""}
            ]
        ],
        "supportedLanguages": ["en_US"]
    }  # closes elems
}  # closes entire package

# Example PACKAGE_1
PACKAGE_1 = {
    "uuid": "robot-control",
    "path": "/home/nao/.local/share/PackageManager/apps/robot-control",
    "version": "0.0.4",
    "channel": "",
    "author": "",
    "organization": "",
    "date": "",
    "typeVersion": "",
    "langToName": {"en_US": "Robot Control"},
    "langToDesc": {"en_US": "Allow the use of tactiles gestures ..."},
    "supportedLanguages": ["en_US"],
    "behaviors": [
        {
            "path": "animations/head_leds",
            "nature": "",
            "langToName": {},
            "langToDesc": {},
            "categories": "",
            "langToTags": {},
            "langToTriggerSentences": {},
            "langToLoadingResponses": {},
            "purposeToCondition": {},
            "permissions": []
        }
    ],
    "languages": [],
    "installer": "user",
    "robotRequirements": [
        {
            "model": "", "minHeadVersion": "", "maxHeadVersion": "",
            "minBodyVersion": "", "maxBodyVersion": ""
        }
    ],
    "naoqiRequirements": [
        {"minVersion": "2.1.0.19", "maxVersion": ""}
    ],
    "services": [
        {
            "execStart": "/usr/bin/python2 lib/robot_control.py",
            "name": "RobotControl-serv",
            "autoRun": True
        }
    ],
    "executableFiles": [],
    "dialogs": [],
    "descriptionLanguages": ["en_US"]
}


class Package(object):

    def __init__(self, pdict, lang):
        """Create an instance of a Package based on a dict of manifest data.
        :param pdict: dict of the package's manifest data
        :param lang: the language to use e.g. en_US
        """
        self.uuid = pdict['uuid']
        self.name = self.get_name(pdict, lang)
        self.utterable_name = make_utterable(self.name)
        self.path = pdict['path']
        self.version = pdict['version']
        self.author = pdict['author']
        self.channel = pdict['channel']
        self.organization = pdict['organization']
        self.date = pdict['date']
        self.type_version = pdict['typeVersion']
        self.installer = pdict['installer']
        self.naoqi_min, self.naoqi_max = self.get_naoqi_reqs(pdict)
        self.supported_langs = self.get_supported_languages(pdict)
        self.description = self.get_description(pdict, lang)
        self.behaviors = self.get_behs(pdict, lang)
        self.services = self.get_servs(pdict)

    def __eq__(self, other):
        return self.uuid == other.uuid

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.uuid < other.uuid

    @staticmethod
    def get_name(pack, lang):
        """Return the localized name of the package or UUID as last resort."""
        try:
            name = pack['elems']['names'][lang]
        except KeyError:
            try:
                name = pack['langToName'][lang]
            except KeyError:
                name = pack['uuid']
        return name

    @staticmethod
    def get_naoqi_reqs(pack):
        """Get naoqi requirements."""
        try:
            naoqi_reqs = pack['elems']['requirements'][1][0]
        except (KeyError, IndexError):
            try:
                naoqi_reqs = pack['naoqiRequirements'][0]
            except (KeyError, IndexError):
                return '', ''
        return naoqi_reqs['minVersion'], naoqi_reqs['maxVersion']

    @staticmethod
    def get_supported_languages(pack):
        """Get list of languages supported by package."""
        try:
            return pack['elems']['supportedLanguages']
        except KeyError:
            try:
                return pack['supportedLanguages']
            except KeyError:
                return list()

    @staticmethod
    def get_description(pack, lang):
        """Get package description"""
        try:
            return pack['elems']['descriptions'][lang]
        except KeyError:
            try:
                return pack['langToDesc'][lang]
            except KeyError:
                return ''

    def get_behs(self, pack, lang):
        """Get behaviors in a package."""
        try:
            return [Behavior(self, d, lang) for d in
                    pack['elems']['contents']['behaviors']]
        except KeyError:
            try:
                return [Behavior(self, d, lang) for d in pack['behaviors']]
            except KeyError:
                return list()

    @staticmethod
    def get_servs(pack):
        """Get services in a package."""
        try:
            elems = pack['elems']
            try:
                return [Service(d) for d in elems['services']]
            except KeyError:
                return list()
        except KeyError:
            return [Service(d) for d in pack['services']]


class Behavior(object):

    def __init__(self, package, bdict, lang):
        """Create an instance of a Behavior based on a dictionary of manifest
        data.
        :param package: instance of the package class that contains the behavior
        :param bdict: dict of the behavior's manifest data
        :param lang: the language to use e.g. en_US
        """
        # Note: self.name will be the path if no name is provided
        self.package = package
        self.name = self.get_name(bdict, lang)
        self.rel_path = bdict['path']
        # e.g. tog-gun-4313f4/behavior_1 or tog-gun-4313f4/.
        self.launch_path = os.path.join(os.path.split(self.package.path)[1],
                                        self.rel_path)
        self.utterable_name = self.get_utterable_name(self.name)
        self.nature = bdict['nature']
        self.description = self.get_desciption(bdict, lang)
        self.tags = self.get_tags(bdict, lang)
        self.trigger_sentences = self.get_trigger_sentences(bdict, lang)
        self.loading_responses = self.get_loading_responses(bdict, lang)
        self.launch_triggers = self.get_launch_triggers(bdict)
        self.categories = bdict['categories']
        self.permisions = bdict['permissions']

    def __eq__(self, other):
        return self.launch_path == other.launch_path

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self, other):
        return self.launch_path < other.launch_path

    def __dict__(self):
        beh = dict()
        beh['name'] = self.utterable_name
        beh['id'] = self.launch_path
        beh['uuid'] = self.package.uuid
        beh['launch_path'] = self.launch_path
        return beh

    @staticmethod
    def get_name(beh, lang):
        """Get behaviour name."""
        try:
            return beh['langToName'][lang]
        except KeyError:
            return ''

    def get_utterable_name(self, name):
        """Return a name you can speak."""
        if self.rel_path == '.' and not name:
            return self.package.utterable_name
        elif not name:
            return make_utterable('%s-%s' %
                                  (self.package.name,
                                   self.rel_path.split('/')[-1]))
        else:
            return make_utterable('%s-%s' % (self.package.name, name))

    @staticmethod
    def get_desciption(beh, lang):
        """Get behavior description."""
        try:
            return beh['langToDesc'][lang]
        except KeyError:
            return ''

    @staticmethod
    def get_tags(beh, lang):
        """Get behaviour tags."""
        try:
            return set(beh['langToTags'][lang])
        except KeyError:
            return set()

    @staticmethod
    def get_trigger_sentences(beh, lang):
        """Get behaviour trigger sentences."""
        try:
            return set(beh['langToTriggerSentences'][lang])
        except KeyError:
            return set()

    @staticmethod
    def get_loading_responses(beh, lang):
        """Get behaviour loading responses."""
        try:
            return set(beh['langToLoadingResponses'][lang])
        except KeyError:
            return set()

    @staticmethod
    def get_launch_triggers(beh):
        """Get behaviour launch triggers."""
        try:
            return beh['purposeToCondition']['launchTrigger']
        except KeyError:
            return list()


class Service():
    def __init__(self, sdict):
        self.name = sdict['name']
        self.auto_run = bool(sdict['autoRun'])
        self.exec_start = sdict['execStart']


def get_packages(lang, verb, session=None):
    """Return the installed packages as a list of package dicts
    :param pacman: the PackageManager service
    :param lang: the language e.g. en_US
    """
    if not session:
        session = qi.Session()
        session.connect('localhost')
    pacman = session.service('PackageManager')
    try:
        packs = pacman.packages2()
        verb('Use pacman.packages2')
    except AttributeError:
        packs = pacman.packages()
        verb('Use pacman.packages')
    return [Package(d, lang) for d in packs]


def make_utterable(name):
    """Take an application or behavior name and make it utterable.
    e.g. make_utterable('robot-control-5fg3ed') => 'Robot Control'

    - split by / and map over each part:
      - Remove the uuid hash
      - Turn camelCase into whitespace separation
      - Replace separators with whitespace
    - join back together
    """
    def utterable(name):
        removed_uid = re.sub(r'(\w*)([-_][a-zA-Z0-9]{6}$)', r'\1', name)
        replaced_camelcase = re.sub(r'([A-Z 0-9])', r' \1', removed_uid)
        replaced_separators = re.sub(r'[\./_-]', ' ', replaced_camelcase)
        replaced_spaces = re.sub(r'[ ]+', ' ', replaced_separators)
        return replaced_spaces.strip().title()

    parts = name.split('/')
    return ' '.join(map(utterable, parts)).strip()


def main():
    """Main fucntion for testing the classes"""
    # for testing
    from pprint import pprint
    sess = qi.Session('Raphael.local')
    # packages = [PACKAGE_1, PACKAGE_2]
    for pack in get_packages('en_US', sess):
        pprint(vars(pack))
        print
        for beh in pack.behaviors:
            if beh.trigger_sentences:
                pprint(vars(beh))
                print
        for serv in pack.services:
            pprint(vars(serv))
            print

if __name__ == '__main__':
    main()
