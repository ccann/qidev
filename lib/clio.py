from clint.textui import colored as col
from clint.textui import puts, indent
from tabulate import tabulate
import readline
import package_utils as pu
import sys
# import curses
# import urwid
# import threading
# import time

completions = list()
# palette = [
#     ('name', 'bold', 'default'),
#     ('reversed', 'standout', ''),
#     ('title', 'dark green', 'default'),
# ]


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


def show_installed_packages(verb, pkg_data):
    """Pretty-print a table of installed packages."""
    table = list()
    for d in pkg_data:
        behaviors = d.behaviors
        n_behaviors = str(len(behaviors)) if behaviors else None
        services = d.services
        n_services = str(len(services)) if services else None
        name = d.name
        table.append([bold(name),
                      d.version,
                      n_behaviors,
                      n_services])
    print ''
    print tabulate(table,
                   headers=['Package Name', 'Version', 'Behaviors', 'Services'],
                   tablefmt="orgtbl")
    print ''


def show_installed_services(verb, pkg_data):
    """Pretty-print a table of installed services."""
    table = list()
    for d in pkg_data:
        services = pu.get_servs(d)
        for s in services:
            name = pu.get_serv_name(s)
            table.append([bold(name),
                          (name),
                          col.green('True') if s['autoRun'] else col.red('False')])
    print ''
    print tabulate(table,
                   headers=['Package Name', 'Service Name', 'Autorun?'],
                   tablefmt='orgtbl')
    print ''


def prompt_for_package(pkg_data):
    """Prompt the user to specify the package name."""
    global completions
    pkg_uuids = [p.uuid for p in pkg_data]
    pkg_names = [p.name for p in pkg_data]
    completions = pkg_uuids + pkg_names
    readline.set_completer_delims('')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)
    try:
        inp = raw_input('Enter package name or UUID (tab to complete)\n> ')
    except KeyboardInterrupt:
        sys.exit()
    return inp


def prompt_for_behavior(behaviors):
    """Prompt the user to specify behavior name."""
    global completions
    completions = behaviors
    readline.set_completer_delims('')
    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)
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
    name = pu.get_beh_name(b, 'en_US')
    puts(bold('* {} (behavior)'.format(bold(name))))
    with indent(4):
        nat = b['nature']
        nature = col.red(nat) if nat == 'interactive' else col.blue(nat)
        puts(pretty('Nature') + nature)


def put_service_string(s):
    """Print information about a service."""
    try:
        name = pu.get_serv_name(s)
        puts(bold('* {} (service)'.format(bold(name))))
        with indent(4):
            puts(pretty('AutoRun') + 'True' if s['autoRun'] else 'False')
    except KeyError:
        pass


def show_package_details(package, pkg_data):
    """Pretty-print the details of an installed package."""
    print('')
    for p in pkg_data:
        name = p.name
        if name == package or p.uuid == package:
            print('* {} ({})'.format(bold(name),
                                     col.cyan('v' + p.version)))
            with indent(4):
                puts(pretty('UUID') + p.uuid)
                try:
                    mn, mx = p.naoqi_reqs
                    if not mn and not mx:
                        mn = 'unspecified'
                        mx = ''
                    puts(pretty('NaoQi Requirements') + mn + mx)
                except IndexError:
                    pass
                puts(pretty('Supported Languages') +
                     pretty(p.supported_languages))
                try:
                    puts(pretty('Desciption') + p.description)
                except KeyError:
                    pass
                for b in pu.get_behs(p):
                    put_behavior_string(b)
                for s in pu.get_servs(p):
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


# def show_running(stdscr, conn, recent, pkg_data):
#     """Print running behaviors and services."""
#     behaviors = conn.get_running_behaviors()
#     services = conn.get_running_services()
#     curses.init_pair(1, curses.COLOR_MAGENTA, -1)
#     curses.init_pair(2, curses.COLOR_BLUE, -1)
#     curses.init_pair(3, curses.COLOR_GREEN, -1)
#     curses.init_pair(4, curses.COLOR_RED, -1)
#     stdscr.addstr('Active Content', curses.color_pair(3))
#     stdscr.addstr(' on ')
#     stdscr.addstr(conn.get_robot_name(), curses.A_BOLD)
#     stdscr.addstr(':\n\n')
#     if not behaviors and not services:
#         stdscr.addstr('None')
#     if behaviors:
#         for b in behaviors:
#             nature = conn.get_behavior_nature(b)
#             nature = 'no nature' if not nature else nature
#             stdscr.addstr('    * ')
#             stdscr.addstr(b + '  ', curses.A_BOLD)
#             stdscr.addch('(')
#             stdscr.addstr('behavior', curses.color_pair(1))
#             stdscr.addstr(') ({})\n'.format(nature))
#         stdscr.addstr('\n')
#     if services:
#         for serv in services:
#             stdscr.addstr('    * ')
#             stdscr.addstr(serv + '  ', curses.A_BOLD)
#             stdscr.addch('(')
#             stdscr.addstr('service', curses.color_pair(2))
#             stdscr.addstr(')\n')
#     if recent != 'first':
#         stdscr.addstr('\nMost recent activity: ')
#         if recent in behaviors + services:
#             stdscr.addstr('Started ', curses.color_pair(3))
#         else:
#             stdscr.addstr('Stopped ', curses.color_pair(4))
#         stdscr.addstr(recent + '\n\n', curses.A_BOLD)

    # title = [('title', 'Active Content'), ' on ', ('name', conn.get_robot_name())]

    # def create_menu(choices):
    #     global menu
    #     if isinstance(choices, str):
    #         choices = choices.split(';')
    #         # print choices
    #     body = [urwid.Text(title), urwid.Divider()]
    #     for c in choices:
    #         button = urwid.Button(c)
    #         urwid.connect_signal(button, 'click', stop, c)
    #         body.append(urwid.AttrMap(button, None, focus_map='reversed'))
    #         menu = urwid.SimpleFocusListWalker(body)

    # conn.verb('get running behaviors...')
    # behaviors = conn.get_running_behaviors()
    # conn.verb('get running services...')
    # services = conn.get_running_services()
    # choices = behaviors + services
    # create_menu(choices)
    # main = urwid.Padding(urwid.ListBox(menu), left=2, right=2)
    # top = urwid.Overlay(main, urwid.SolidFill(u'\N{MEDIUM SHADE}'),
    #                     align='center', width=('relative', 60),
    #                     valign='middle', height=('relative', 60),
    #                     min_width=20, min_height=9)
    # loop = urwid.MainLoop(top, palette=palette)
    # pipe = loop.watch_pipe(create_menu)
    # loop.run()


def show_dialog_header(conn):
    print('')
    print('{:^60}'.format(' %s ------------------------------------------------- %s ') %
          (col.blue('Human'), col.red((conn.get_robot_name()))))


# def dialog_separator(value):
    # if value == 'ListenOn':
    #     def newline():
    #         time.sleep(1)
    #         print('')
    #     t = threading.Thread(target=newline)
    #     t.start()


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
