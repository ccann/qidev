from clint.textui import colored as col
from clint.textui import puts, indent
from tabulate import tabulate
import readline

completions = list()


def bold(text):
    return '\033[1m' + text + '\033[0m'


def underlined(text):
    return '\033[4m' + text + '\033[0m'


def completer(text, state):
    options = [i for i in completions if i.startswith(text)]
    if state < len(options):
        return options[state]
    else:
        return None


def show_installed_packages(pkg_data):
    """Pretty-print a table of installed packages."""
    table = list()
    for d in pkg_data:
        n_behaviors = len(d['behaviors'])
        n_behaviors = str(n_behaviors) if not n_behaviors == 0 else None
        n_services = len(d['services'])
        n_services = str(n_services) if not n_services == 0 else None
        table.append([bold(d['langToName']['en_US']),
                      d['version'],
                      n_behaviors,
                      n_services])
    print ''
    print tabulate(table,
                   headers=['Package Name', 'Version', 'Behaviors', 'Services'],
                   tablefmt="orgtbl")
    print ''


def show_installed_services(pkg_data):
    """Pretty-print a table of installed services."""
    table = list()
    for d in pkg_data:
        for s in d['services']:
            table.append([bold(d['langToName']['en_US']),
                          (s['name']),
                          col.green('True') if s['autoRun'] else col.red('False')])
    print ''
    print tabulate(table,
                   headers=['Package Name', 'Service Name', 'Autorun?'],
                   tablefmt='orgtbl')
    print ''


def prompt_for_package(pkg_data):
    """Prompt the user to specify the package name."""
    global completions
    pkg_uuids = [p['uuid'] for p in pkg_data]
    pkg_names = [p['langToName']['en_US'] for p in pkg_data]
    completions = pkg_uuids + pkg_names
    readline.set_completer_delims('')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)
    inp = raw_input('Enter package name or UUID (tab to complete)\n> ')
    show_package_details(inp, pkg_data)


def prompt_for_behavior(behaviors):
    """Prompt the user to specify behavior name."""
    global completions
    completions = behaviors
    readline.set_completer_delims('')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)
    inp = raw_input('Enter package-uuid/behavior-name (tab to complete)\n> ')
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
    try:
        name = b['langToName']['en_US']
        puts(bold('* {} (behavior)'.format(bold(name))))
        with indent(4):
            nat = b['nature']
            nature = col.red(nat) if nat == 'interactive' else col.blue(nat)
            puts(pretty('Nature') + nature)
    except KeyError:
        pass


def put_service_string(s):
    """Print information about a service."""
    try:
        name = s['name']
        puts(bold('* {} (service)'.format(bold(name))))
        with indent(4):
            puts(pretty('AutoRun') + 'True' if s['autoRun'] else 'False')
    except KeyError:
        pass


def show_package_details(package, pkg_data):
    """Pretty-print the details of an installed package."""
    print('')
    for p in pkg_data:
        if p['langToName']['en_US'] == package or p['uuid'] == package:
            print('* {} ({})'.format(bold(p['langToName']['en_US']),
                                     col.cyan('v' + p['version'])))
            with indent(4):
                puts(pretty('UUID') + p['uuid'])
                try:
                    nr = p['naoqiRequirements'][0]
                    mn = nr['minVersion']
                    mx = ' to {}'.format(nr['maxVersion']) if nr['maxVersion'] else ' +'
                    puts(pretty('NaoQi Requirements') + mn + mx)
                except IndexError:
                    pass
                puts(pretty('Supported Languages') +
                     pretty(p['supportedLanguages']))
                try:
                    puts(pretty('Desciption') + p['langToDesc']['en_US'])
                except KeyError:
                    pass
                for b in p['behaviors']:
                    put_behavior_string(b)
                for s in p['services']:
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
