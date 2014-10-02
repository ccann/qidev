"""Utilities for working with ALPackageManager.

This script provides functions to extract elements from the packages list
returned by PackageManager.packages(). It is intended to allow the developer to
be agnostic to the version of the PackageManager API (i.e. packages() and
packages2())

"""
import re
import os

__author__ = "Cody Canning"

# Example package2
package2 = {
    "uuid": "robot-control-c6d14c",
    "version": "0.0.3",
    "author": "",
    "channel": "",
    "organization": "",
    "date": "",
    "typeVersion": "",
    "installer": "cloud.aldebaran-robotics.com",
    "path": "/home/nao/.local/share/PackageManager/apps/robot-control-c6d14c",
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

# Example package1
package1 = {
    "uuid": "robot-control-c6d14c",
    "path": "/home/nao/.local/share/PackageManager/apps/robot-control-c6d14c",
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


class Package():

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

    def get_name(self, p, lang):
        """Return the localized name of the package or UUID as last resort."""
        try:
            name = p['elems']['names'][lang]
        except KeyError:
            try:
                name = p['langToName'][lang]
            except KeyError:
                name = p['uuid']
        return name

    def get_naoqi_reqs(self, p):
        try:
            nr = p['elems']['requirements'][1][0]
        except (KeyError, IndexError):
            try:
                nr = p['naoqiRequirements'][0]
            except (KeyError, IndexError):
                return '', ''
        return nr['minVersion'], nr['maxVersion']

    def get_supported_languages(self, p):
        try:
            return p['elems']['supportedLanguages']
        except KeyError:
            try:
                return p['supportedLanguages']
            except KeyError:
                return list()

    def get_description(self, p, lang):
        try:
            return p['elems']['descriptions'][lang]
        except KeyError:
            try:
                return p['langToDesc'][lang]
            except KeyError:
                return ''

    def get_behs(self, p, lang):
        try:
            return [Behavior(self, d, lang) for d in
                    p['elems']['contents']['behaviors']]
        except KeyError:
            try:
                return [Behavior(self, d, lang) for d in p['behaviors']]
            except KeyError:
                return list()

    def get_servs(self, p):
        try:
            elems = p['elems']
            try:
                return [Service(d) for d in elems['services']]
            except KeyError:
                return list()
        except KeyError:
            return [Service(d) for d in p['services']]


class Behavior():

    def __init__(self, package, bdict, lang):
        """Create an instance of a Behavior based on a dictionary of manifest data.
        :param package: instance of the package class that contains the behavior
        :param bdict: dict of the behavior's manifest data
        :param lang: the language to use e.g. en_US
        """
        # Note: self.name will be the path if no name is provided
        self.package = package
        self.name = self.get_name(bdict, lang)
        self.rel_path = bdict['path']
        # e.g. tog-gun-4313f4/behavior_1 or tog-gun-4313f4/.
        self.launch_path = os.path.join(os.path.split(self.package.path)[1], self.rel_path)
        self.utterable_name = self.get_utterable_name(self.name)
        self.nature = bdict['nature']
        self.description = self.get_desciption(bdict, lang)
        self.tags = self.get_tags(bdict, lang)
        self.trigger_sentences = self.get_trigger_sentences(bdict, lang)
        self.loading_responses = self.get_loading_responses(bdict, lang)
        self.launch_triggers = self.get_launch_triggers(bdict)
        self.categories = bdict['categories']
        self.permisions = bdict['permissions']

    def get_name(self, b, lang):
        try:
            return b['langToName'][lang]
        except KeyError:
            return ''

    def get_utterable_name(self, name):
        """Return a name you can speak."""
        if self.rel_path == '.':
            return self.package.utterable_name
        elif not name:
            return make_utterable('%s-%s' %
                                  (self.package.name,
                                   self.rel_path.split('/')[-1]))
        else:
            return make_utterable('%s-%s' % (self.package.name, name))

    def get_desciption(self, b, lang):
        try:
            return b['langToDesc'][lang]
        except KeyError:
            return ''

    def get_tags(self, b, lang):
        try:
            return b['langToTags'][lang]
        except KeyError:
            return list()

    def get_trigger_sentences(self, b, lang):
        try:
            return b['langToTriggerSentences'][lang]
        except KeyError:
            return list()

    def get_loading_responses(self, b, lang):
        try:
            return b['langToLoadingResponses'][lang]
        except KeyError:
            return list()

    def get_launch_triggers(self, b):
        try:
            return b['purposeToCondition']['launchTrigger']
        except KeyError:
            return list()


class Service():
    def __init__(self, sdict):
        self.name = sdict['name']
        self.auto_run = bool(sdict['autoRun'])
        self.exec_start = sdict['execStart']


def get_packages(pacman, lang):
    """Return the installed packages as a list of package dicts
    :param pacman: the PackageManager service
    :param lang: the language e.g. en_US
    """
    try:
        packs = pacman.packages2()
        print('Use pacman.packages2')
    except AttributeError:
        packs = pacman.packages()
        print('Use pacman.packages')
    return [Package(d, lang) for d in packs]


def make_utterable(name):
    """Take an application or behavior name and make it utterable.
    - Remove the uuid
    - Turn camelCase into whitespace separation
    - Replace separators with whitespace
    - e.g. make_utterable('robot-control-c6d14c') => 'Robot Control'
    """
    removed_uid = re.sub('(\w*)([-_][a-zA-Z0-9]{6}$)', r'\1', name)
    replaced_camelcase = re.sub(r'([A-Z 0-9])', r' \1', removed_uid)
    replaced_separators = re.sub('[\./_-]', ' ', replaced_camelcase)
    replaced_spaces = re.sub('[ ]+', ' ', replaced_separators)
    return replaced_spaces.strip().title()


def main():
    # for testing
    from pprint import pprint
    import qi
    sess = qi.Session('Michelangelo.local')
    pacman = sess.service('PackageManager')
    # packages = [package1, package2]
    for p in get_packages(pacman, 'en_US'):
        pprint(vars(p))
        print
        for b in p.behaviors:
            if b.trigger_sentences:
                pprint(vars(b))
                print
        for s in p.services:
            pprint(vars(s))
            print

if __name__ == '__main__':
    main()
