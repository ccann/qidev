import os
import socket
import qi
import clio as io
import config
from connection import Connection
from clint.textui import colored as col


def verbose_print(flag):
    """Print function for --verbose flag."""
    def func(text):
        if flag:
            print(text)
    return func


def create_connection(ns, verb, ssh=True, create_session=True):
    """Establish a connection to hostname and a qi session."""
    hostname = config.read_hostname()
    if create_session:
        try:
            session = qi.Session(hostname)
        except RuntimeError:
            raise RuntimeError('%s: could not establish connection to %s' %
                               (col.red('ERROR'), col.blue(hostname)))
    else:
        session = None
    try:
        verb('connect to {}'.format(hostname))
        conn = Connection(hostname, ssh=ssh)
    except socket.gaierror as e:
        raise RuntimeError('{}: {} ... for hostname: {}'.format(col.red('ERROR'), e,
                                                                col.blue(hostname)))
    except socket.error as e:
        # assuming this is a virtual bot... kind of a hack
        conn = Connection(hostname, virtual=True, ssh=ssh)
    return conn, session


def install_handler(ns):
    """Install a package to a remote host or locally."""
    verb = verbose_print(ns.verbose)
    conn, session = create_connection(ns, verb)
    try:
        verb('Create package from directory: {}'.format(ns.p))
        abs_path = conn.create_package(ns.p)
        verb('Transfer package to {}'.format(conn.hostname))
        pkg_name = conn.transfer(abs_path)
        verb('Install package: {}'.format(pkg_name))
        conn.install_package(session, abs_path)
        verb('Clean up: {}'.format(pkg_name))
        conn.delete_pkg_file(abs_path)
    except IOError:
        if ns.p:
            print('%s: %s is not a project directory (does not contain manifest.xml)' %
                  (col.red('ERROR'), col.blue(ns.p)))
        else:
            print('%s: %s is not a project directory (does not contain manifest.xml)' %
                  (col.red('ERROR'), col.blue(os.getcwd())))


def config_handler(ns):
    """Configure fields of the .qidev file."""
    verb = verbose_print(ns.verbose)
    field = ns.field.strip()
    if field == 'hostname':
        verb('Set {} to {}'.format(field, ns.value))
        config.write_hostname(ns.value)
    else:
        print('ERROR: unsupported field {}'.format(field))


def connect_handler(ns):
    """Change hostname field of the .qidev file."""
    verb = verbose_print(ns.verbose)
    verb('Set hostname to {}'.format(ns.hostname))
    config.write_hostname(ns.hostname)


def show_handler(ns):
    """Show information about a package, service, active content, etc."""
    verb = verbose_print(ns.verbose)
    conn, session = create_connection(ns, verb, ssh=False)
    pkg_data = conn.get_installed_package_data(session)
    if ns.s:
        io.show_installed_services(pkg_data)
    elif ns.i:
        io.prompt_for_package(pkg_data)
    elif ns.active:
        io.show_running(conn.get_running_behaviors(session),
                        conn.get_running_services(session),
                        pkg_data)
    else:
        io.show_installed_packages(pkg_data)


def state_handler(state, ns):
    """Start or stop a behavior or service."""
    verb = verbose_print(ns.verbose)
    conn, session = create_connection(ns, verb, ssh=False)
    if state == 'start':
        behaviors = conn.get_installed_behaviors(session)
        if ns.life:
            inp = io.prompt_for_behavior(behaviors)
            try:
                verb('switch focus to: {}'.format(inp))
                conn.life_switch_focus(session, inp)
            except RuntimeError:  # this is a huge hack but its not my fault
                verb('couldnt find behavior {} so appending "/.": {}'.format(inp, inp+'/.'))
                inp = inp+'/.'
                verb('switch focus to: {}'.format(inp))
                conn.life_switch_focus(session, inp)
        else:
            services = conn.get_declared_services(session)
            inp = io.prompt_for_behavior(services + behaviors)
            if inp in services:
                verb('start service: {}'.format(inp))
                conn.start_service(session, inp)
            elif inp in behaviors:
                verb('start behavior: {}'.format(inp))
                conn.start_behavior(session, inp)
            else:
                print('{}: {} is not an eligible behavior or service'.format(col.red('ERROR'),
                                                                             inp))
    elif state == 'stop':
        if ns.life:
            conn.life_stop_focus(session)  # stop focused activity
        else:  # stop behavior/service
            services = conn.get_running_services(session)
            behaviors = conn.get_running_behaviors(session)
            inp = io.prompt_for_behavior(services + behaviors)
            if inp in services:
                conn.stop_service(session, inp)
            elif inp in behaviors:
                conn.stop_behavior(session, inp)
            else:
                print('{}: {} is not an eligible behavior or service'.format(col.red('ERROR'),
                                                                             inp))


def life_handler(ns):
    verb = verbose_print(ns.verbose)
    conn, session = create_connection(ns, verb, ssh=False)
    if ns.state == 'on':
        conn.life_on(session)
    elif ns.state == 'off':
        conn.life_off(session)
    else:
        print('life state can only be on or off')


def nao_handler(ns):
    verb = verbose_print(ns.verbose)
    conn, session = create_connection(ns, verb, create_session=False)
    verb('nao action: {}'.format(ns.action))
    sshin, sshout, ssherr = conn.ssh.exec_command('sudo /etc/init.d/naoqi %s' % ns.action)
    io.format_nao_output(sshout, ns.action)


def power_handler(command, ns):
    verb = verbose_print(ns.verbose)
    conn, session = create_connection(ns, verb, ssh=False)
    verb('robot: {}'.format(command))
    if command == 'reboot':
        conn.robot_reboot(session)
    if command == 'shutdown':
        conn.robot_shutdown(session)


def volume_handler(ns):
    verb = verbose_print(ns.verbose)
    conn, session = create_connection(ns, verb, ssh=False)
    verb('volume level: {}'.format(ns.level))
    target = conn.set_volume(session, ns.level)
    print('Setting volume to {}'.format(col.magenta(target)))
