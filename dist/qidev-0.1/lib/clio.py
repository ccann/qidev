"""
clio.py

functions for command line input/output.
"""

from clint.textui import colored as col
from clint.textui import puts, indent
from tabulate import tabulate
import readline
import sys


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


def show_installed_packages(verb, pkgs):
    """Pretty-print a table of installed packages."""
    table = list()
    for p in pkgs:
        n_behaviors = str(len(p.behaviors)) if p.behaviors else None
        n_services = str(len(p.services)) if p.services else None
        table.append([bold(p.name),
                      p.version,
                      n_behaviors,
                      n_services])
    print ''
    print tabulate(table,
                   headers=['Package Name', 'Version', 'Behaviors', 'Services'],
                   tablefmt="orgtbl")
    print ''


def show_installed_services(verb, pkgs):
    """Pretty-print a table of installed services."""
    table = list()
    for p in pkgs:
        for s in p.services:
            table.append([bold(p.name),
                          s.name,
                          col.green('True') if s.auto_run else col.red('False')])
    print('')
    print tabulate(table,
                   headers=['Package Name', 'Service Name', 'Autorun?'],
                   tablefmt='orgtbl')
    print('')


def prompt_for_package(completions):
    """Prompt the user to specify the package name."""
    readline.set_completer_delims('')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(create_completer(completions))
    try:
        inp = raw_input('Enter package name or UUID (tab to complete)\n> ')
    except KeyboardInterrupt:
        sys.exit()
    return inp


def prompt_for_behavior(behaviors, completions=None):
    """Prompt the user to specify behavior name."""
    readline.set_completer_delims('')
    readline.parse_and_bind("tab: complete")
    if not completions:
        readline.set_completer(create_completer(behaviors))
    else:
        readline.set_completer(create_completer(completions))
    try:
        inp = raw_input('Enter package-uuid/behavior-name (tab to complete)\n> ')
    except KeyboardInterrupt:
        sys.exit()
    return inp


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
    puts(bold('* {} (behavior)'.format(bold(b.name))))
    with indent(4):
        nat = b.nature
        nature = col.red(nat) if nat == 'interactive' else col.blue(nat)
        puts(pretty('Nature') + nature)


def put_service_string(s):
    """Print information about a service."""
    try:
        puts(bold('* {} (service)'.format(bold(s.name))))
        with indent(4):
            puts(pretty('AutoRun') + 'True' if s.auto_run else 'False')
    except KeyError:
        pass


def show_package_details(package, pkgs):
    """Pretty-print the details of an installed package."""
    print('')
    for p in pkgs:
        if p.name == package or p.uuid == package:
            print('* {} ({})'.format(bold(p.name),
                                     col.cyan('v' + p.version)))
            with indent(4):
                puts(pretty('UUID') + p.uuid)
                try:
                    mn, mx = p.naoqi_min, p.naoqi_max
                    if not mn and not mx:
                        mn = 'unspecified'
                        mx = ''
                    puts(pretty('NaoQi Requirements') + mn + mx)
                except IndexError:
                    pass
                puts(pretty('Supported Languages') +
                     pretty(p.supported_langs))
                try:
                    puts(pretty('Desciption') + p.description)
                except KeyError:
                    pass
                for b in p.behaviors:
                    put_behavior_string(b)
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
