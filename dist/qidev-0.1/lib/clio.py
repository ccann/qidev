"""
clio.py

functions for command line input/output.
"""

from clint.textui import colored as col
from clint.textui import puts, indent
from tabulate import tabulate
import readline
readline.set_completer_delims('')
if 'libedit' in readline.__doc__:
    # see: http://stackoverflow.com/questions/7116038/python-tab-completion-mac-osx-10-7-lion
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")
import sys
import socket


def bold(text):
    return '\033[1m' + text + '\033[0m'


def underlined(text):
    return '\033[4m' + text + '\033[0m'


def create_completer(completions):
    def completer(text, state):
        options = [i for i in completions if i.startswith(text)]
        if state < len(options):
            return options[state]
        else:
            return None
    return completer


def show_info(conn):
    socket.setdefaulttimeout(3)
    (hn, _, ips) = socket.gethostbyname_ex(conn.hostname)
    ip = ips[0]
    print('')
    print('{}: {}'.format(bold('Robot'),
                          col.magenta(conn.get_robot_name())))
    if '.local' in hn:
        print('{}: {}'.format(bold('Hostname'),
                              col.blue(hn)))
    print('{}: {}'.format(bold('IP'),
                          col.blue(ip)))
    system = conn.session.service('ALSystem')
    print('{}: {}'.format(bold('NaoQi Version'),
                          system.systemVersion()))
    tts = conn.session.service('ALTextToSpeech')
    lang = tts.getLanguage()
    # print('{}: {}'.format(bold('Language'),
    #                       lang))
    al = tts.getAvailableLanguages()
    al = ['{}'.format(col.green(l.upper())) if l == lang else l for l in al]
    available_langs = ', '.join(al)
    print('{}: {}'.format(bold('Languages'),
                          available_langs))
    audio = conn.session.service('ALAudioDevice')
    print('{}: {}'.format(bold('Volume'),
                          audio.getOutputVolume()))
    posture = conn.session.service('ALRobotPosture')
    post = posture.getPosture()
    fam = posture.getPostureFamily()
    print('{}: {} ({})'.format(bold('Posture'),
                               post,
                               fam))
    life = conn.session.service('ALAutonomousLife')
    fact = life.focusedActivity()
    if not fact:
        fact = 'none'
    else:
        fact = col.red(fact)
    print('{}: {}'.format(bold('Focused Activity'),
                          fact))
    state = life.getState().upper()
    if state == 'SOLITARY':
        state = col.green(state)
    elif state == 'DISABLED':
        state = col.yellow(state)
    else:
        state = col.red(state)
    print('{}: {}'.format(bold('ALife State'),
                          state))

    print('')


def show_installed_packages(verb, pkgs):
    """Pretty-print a table of installed packages."""
    table = list()
    for p in pkgs:
        n_behaviors = len(p.behaviors) if p.behaviors else None
        n_services = len(p.services) if p.services else None
        table.append([bold(p.name),
                      p.uuid,
                      p.version,
                      n_behaviors,
                      n_services])
    print ''
    print tabulate(table,
                   headers=['Package Name', 'Unique ID', 'Version', 'Behaviors', 'Services'],
                   tablefmt="orgtbl")
    print ''


def show_installed_services(verb, pkgs):
    """Pretty-print a table of installed services."""
    table = list()
    for p in pkgs:
        for s in p.services:
            table.append([bold(p.name),
                          p.uuid,
                          s.name,
                          col.green('True') if s.auto_run else col.red('False')])
    print('')
    print tabulate(table,
                   headers=['Package Name', 'Unique ID', 'Service Name', 'Autorun?'],
                   tablefmt='orgtbl')
    print('')


def _prompt(prompt_text, completions):
    """Prompt the user with tab completions."""
    readline.set_completer(create_completer(completions))
    try:
        inp = raw_input(prompt_text + ' (tab to complete) \n> ')
        return inp
    except KeyboardInterrupt:
        sys.exit()


def prompt_for_service(service_names):
    """Prompt the user for the name of a service, provide tab-completions"""
    return _prompt('Enter service name', service_names)


def prompt_for_behavior(behavior_names):
    """Prompt the user for the name of a behavior, provide tab-completions"""
    return _prompt('Enter package-uuid/behavior-name', behavior_names)


def prompt_for_package(package_names):
    """Prompt the user for the name of a behavior, provide tab-completions"""
    return _prompt('Enter package uuid or package name', package_names)


def pretty(o):
    """Format objects nicely."""
    if isinstance(o, list):
        return ', '.join(map(str, o))
    elif isinstance(o, str):
        return '{}: '.format(col.blue(o))
    else:
        return None


def put_behavior_string(b):
    """Print information about a behavior."""
    if not b.name:
        name = b.rel_path
    else:
        name = b.name
    nat = b.nature
    if nat == 'solitary':
        nature = col.yellow('solitary')
    if nat == 'interactive':
        nature = col.red('interactive')
    else:
        nature = 'no-nature'
    puts(bold('* {}'.format(name)) + ' ({})'.format(nature))


def put_service_string(s):
    """Print information about a service."""
    try:
        puts(bold('* {}'.format(s.name)) + ' (service)')
        with indent(4):
            puts(pretty('autoRun') + col.red('True') if s.auto_run else 'False')
            puts(pretty('execStart') + s.exec_start)
    except KeyError:
        pass


def show_package_details(package, pkgs):
    """Pretty-print the details of an installed package."""
    print('')
    for p in pkgs:
        if p.name == package or p.uuid == package:
            print('* {} ({})'.format(bold(p.name),
                                     col.cyan('v' + p.version)))
            with indent(2):
                puts(pretty('UUID') + p.uuid)
                try:
                    mn, mx = p.naoqi_min, p.naoqi_max
                    if not mn:
                        mn = '0.0.0'
                    if not mx:
                        mx = 'INF'
                    puts(pretty('NaoQi Requirements') + '{} <= version <= {}'.format(mn, mx))
                except IndexError:
                    pass
                try:
                    puts(pretty('Supported Languages') +
                         pretty(p.supported_langs))
                except AttributeError:
                    pass
                try:
                    max_len = 200
                    if len(p.description) > max_len:
                        puts(pretty('Desciption') + '{}...'.format(p.description[:max_len]))
                    else:
                        puts(pretty('Desciption') + '{}'.format(p.description))
                except KeyError:
                    pass
                if p.behaviors:
                    puts(pretty('Behaviors ({})'.format(len(p.behaviors))))
                    with indent(2):
                        for b in p.behaviors:
                            put_behavior_string(b)
                if p.services:
                    puts(pretty('Services ({})'.format(len(p.services))))
                    with indent(2):
                        for s in p.services:
                            put_service_string(s)
    print('')


def show_running(behaviors, services, pkg_data):
    """Print running behaviors and services."""
    print('\nActive Content:')
    if not behaviors and not services:
        print('No behaviors or services are active.')
    if behaviors:
        for b in behaviors:
            with indent(4):
                puts('* {}  ({})'.format(bold(b), col.magenta('behavior')))
    if services:
        for s in services:
            with indent(4):
                puts('* {}  ({})'.format(bold(s), col.blue('service')))
    print('')


def show_dialog_header(conn):
    print('')
    print('{:^60}'.format(' %s ------------------------------------------------- %s ') %
          (col.blue('Human'), col.red((conn.get_robot_name()))))


def show_dialog_input(value):
    strat = 'BNF' if 'BNF' in str(value[2]) else str(value[2])
    s = '{0} ({1:.0f}% {2})'.format(col.blue(value[0].strip()),
                                    round(value[1] * 100),
                                    strat)
    print(s.ljust(60))


def show_dialog_output(value):
    print(col.red(value.strip().rjust(60)))


def format_nao_output(file_like, command):
    done = False
    for line in file_like:
        if (command == 'restart' or command == 'start') and 'Starting naoqi' in line:
            done = True
        elif command == 'stop' and 'Naoqi stopped' in line:
            done = True
        line = line.replace('Stopping', str(col.red('Stopping')))
        line = line.replace('Starting', str(col.green('Starting')))
        line = line.replace('waiting', str(col.yellow('waiting')))
        print line.rstrip()
        if done:
            break
    file_like.close()
