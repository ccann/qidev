"""
handlers.py

A handler is a function assigned to handle all the functionality associated
with a particular command line subparser.
"""


import os
import clio as io
import config
from connection import Connection
from clint.textui import colored as col
import sys
import select
import re
from threading import Thread


def verbose_print(flag):
    """Print function for --verbose flag."""
    def func(text):
        if flag:
            print(text)
    return func


def install_handler(ns):
    """Install a package to a remote host or locally."""
    verb = verbose_print(ns.verbose)

    def install(conn):
        try:
            verb('Create package from directory: {}'.format(ns.path))
            abs_path = conn.create_package(ns.path)
            verb('Transfer package to {}'.format(conn.hostname))
            pkg_name = conn.transfer(abs_path)
            verb('Install package: {}'.format(pkg_name))
            conn.install_package(abs_path)
            verb('Clean up: {}'.format(pkg_name))
            conn.delete_pkg_file(abs_path)
            local_pkg = os.path.join(ns.path, '..', pkg_name)
            verb('Remove locally: {}'.format(local_pkg))
            os.remove(local_pkg)
            print('installed {} on {}'.
                  format(col.blue(pkg_name).replace('.pkg', ''),
                         col.magenta(conn.get_robot_name())))
        except IOError:
            if ns.path:
                print('%log: %log is not a project directory (does not contain manifest.xml)' %
                      (col.red('error'), col.blue(ns.path)))
            else:
                print('%log: %log is not a project directory (does not contain manifest.xml)' %
                      (col.red('error'), col.blue(os.getcwd())))

    if ns.multi:
        for conn in [Connection(verb, hostname=ip) for ip in ns.multi]:
            install(conn)
    else:
        install(Connection(verb))


def remove_handler(ns):
    """Remove a package from the robot."""
    verb = verbose_print(ns.verbose)

    def get_completions(conn):
        pkg_data = conn.get_installed_package_data()
        completions = [p.uuid for p in pkg_data] + [p.name for p in pkg_data]
        return completions

    def remove(conn, inp):
        # if we matched a package name, replace it with the pkg uuid
        pkg_data = conn.get_installed_package_data()
        if inp in [p.name for p in pkg_data]:
            for pkg in pkg_data:
                if pkg.name == inp:
                    verb('replace {} with {}'.format(inp, pkg.uuid))
                    inp = pkg.uuid
                    break
        # if package removal fails or specified package is not installed on the robot
        if not conn.remove_package(inp) or inp not in completions:
            print('{}: package {} not installed on {}'.format(col.red('error'),
                                                              col.blue(inp),
                                                              col.magenta(conn.get_robot_name())))
        else:  # package successfully removed
            print('removed {} from {}'.format(col.blue(inp),
                                              col.magenta(conn.get_robot_name())))

    if ns.multi:
        conns = [Connection(verb, ssh=False, hostname=ip) for ip in ns.multi]
        completions = set()
        for conn in conns:
            completions.update(get_completions(conn))
        inp = io.prompt_for_package(list(completions))
        for conn in conns:
            remove(conn, inp)
    else:
        conn = Connection(verb, ssh=False)
        completions = get_completions(conn)
        inp = io.prompt_for_package(completions)
        remove(conn, inp)


def config_handler(ns):
    """Configure fields of the ~/.qidev file."""
    config.write_field(ns.field.strip(), ns.value.strip())
    print('set {} to {}'.format(col.blue(ns.field.strip()),
                                col.blue(ns.value.strip())))


def connect_handler(ns):
    """Change hostname field of the .qidev file."""
    verb = verbose_print(ns.verbose)
    verb('Set hostname to {}'.format(ns.hostname))
    config.write_field('hostname', ns.hostname)
    print('set {} to {}'.format(col.blue('hostname'),
                                col.magenta(ns.hostname)))


def show_handler(ns):
    """Display information about a package, service, active content, etc."""
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    verb('Check installed packages...')
    pkg_data = conn.get_installed_package_data()
    if ns.services:
        verb('Show installed services')
        io.show_installed_services(verb, pkg_data)
    elif ns.inspect:
        completions = [p.uuid for p in pkg_data] + [p.name for p in pkg_data]
        inp = io.prompt_for_package(completions)
        io.show_package_details(inp, pkg_data)
    elif ns.active:
        verb('Show active content')
        io.show_running(conn.get_running_behaviors(),
                        conn.get_running_services(),
                        pkg_data)
    else:
        io.show_installed_packages(verb, pkg_data)


def start_handler(ns):
    """Focus an activity or start a behavior or service."""
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    behaviors = conn.get_installed_behaviors()
    if ns.bm:  # use behavior manager
        services = conn.get_declared_services()
        inp = ns.name if ns.name else io.prompt_for_behavior(services + behaviors)
        if inp in services:
            verb('Start service: {}'.format(inp))
            conn.start_service(inp)
        elif inp in behaviors:
            verb('Start behavior: {}'.format(inp))
            conn.start_behavior(inp)
        else:
            print('{}: {} is not an eligible behavior or service'.
                  format(col.red('error'), inp))
    else:  # use autonomous life
        inp = ns.name if ns.name else io.prompt_for_behavior(behaviors)
        try:
            verb('Switch focus to: {}'.format(inp))
            conn.life_switch_focus(inp)
        except RuntimeError:  # this is a wart but it'log not my fault
            verb('Couldnt find behavior {} so appending "/.": {}'.format(inp, inp + '/.'))
            inp = inp+'/.'
            verb('switch focus to: {}'.format(inp))
            conn.life_switch_focus(inp)


def stop_handler(ns):
    """Stop the focused activity or use behavior manager to stop a behavior or service."""
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    if ns.bm:  # stop behavior/service
        services = conn.get_running_services()
        behaviors = conn.get_running_behaviors()
        inp = io.prompt_for_behavior(services + behaviors)
        if inp in services:
            conn.stop_service(inp)
        elif inp in behaviors:
            conn.stop_behavior(inp)
        else:
            print('{}: {} is not an eligible behavior or service'.
                  format(col.red('error'), col.blue(inp)))
    else:  # stop the focused activity
        conn.life_stop_focus()


def life_handler(ns):
    """Toggle Autonomous Life ON or OFF."""
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    if ns.state == 'on':
        conn.life_on()
        print('started autonomous life service')
    elif ns.state == 'off' or ns.state == 'die':
        conn.life_off()
        print('stopped autonomous life service')
    else:
        print(col.red('error') + ': autonomous life state can only be "on" or "off"')


def nao_handler(ns):
    """Issue a nao command via SSH."""
    verb = verbose_print(ns.verbose)

    def nao_command(conn):
        verb('nao action: {}'.format(ns.action))
        print('{} naoqi on {}'.format(ns.action, col.magenta(conn.get_robot_name())))
        command = 'sudo /etc/init.d/naoqi {}'.format(ns.action)
        verb(command)
        sshin, sshout, ssherr = conn.ssh.exec_command(command)
        io.format_nao_output(sshout, ns.action)
        print('\n')

    if ns.multi:
        for ip in ns.multi:
            try:
                nao_command(Connection(verb, hostname=ip))
            except RuntimeError as e:
                print(e)
    else:
        nao_command(Connection(verb))


def reboot_handler(ns):
    """Reboot the robot."""
    verb = verbose_print(ns.verbose)

    def reboot(conn):
        print('Reboot {}'.format(col.magenta(conn.get_robot_name())))
        t = Thread(target=conn.robot_reboot)
        t.start()

    if ns.multi:
        for ip in ns.multi:
            try:
                reboot(Connection(verb, hostname=ip, ssh=False))
            except RuntimeError as e:
                print(e)
    else:
        reboot(Connection(verb, ssh=False))


def shutdown_handler(ns):
    """Shutdown the robot."""
    verb = verbose_print(ns.verbose)

    def shutdown(conn):
        print('{} shutting down'.format(col.magenta(conn.get_robot_name())))
        t = Thread(target=conn.robot_shutdown)
        t.start()

    if ns.multi:
        for ip in ns.multi:
            try:
                shutdown(Connection(verb, hostname=ip, ssh=False))
            except RuntimeError as e:
                print(e)
    else:
        shutdown(Connection(verb, ssh=False))


def vol_handler(ns):
    """Change the volume of the robot."""
    verb = verbose_print(ns.verbose)

    def set_vol(conn):
        verb('Volume level: {}'.format(ns.level))
        target = conn.set_volume(ns.level)
        print("Set {}'s volume to {}"
              .format(conn.get_robot_name(), col.magenta(target)))

    if ns.multi:
        for ip in ns.multi:
            try:
                set_vol(Connection(verb, hostname=ip, ssh=False))
            except RuntimeError as e:
                print(e)
    else:
        set_vol(Connection(verb, ssh=False))


def wake_handler(ns):
    """Wake up the robot."""
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    print('Waking up {}'.format(conn.get_robot_name()))
    conn.wake_up()


def rest_handler(ns):
    """Put the robot to rest."""
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    print('Put {} to rest'.format(conn.get_robot_name()))
    conn.rest()


def dialog_handler(ns):
    """Show the dialog window."""
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    verb('Show dialog window')
    io.show_dialog_header(conn)
    conn.init_dialog_window()


def log_handler(ns):
    """Display the naoqi tail logs to the terminal with colors."""
    verb = verbose_print(ns.verbose)
    conn = Connection(verb)
    p = '/var/log/naoqi/tail-naoqi.log'
    if ns.cp:
        try:
            lp = config.read_field('log_path')
            if not lp:
                lp = '~'
            log_path = os.path.expanduser(lp)
            conn.remote_get(p, log_path)
            print('secure copied logs to ' +
                  col.blue(os.path.join(log_path, 'tail-naoqi.log')))
        except RuntimeError:
            print(col.red('error') + ': tail-naoqi.log not found on ' +
                  col.magenta(conn.get_robot_name()))
    else:
        transport = conn.ssh.get_transport()
        channel = transport.open_session()
        remote_command = 'tail -f ' + p + ' & { read ; kill %1; }'
        channel.exec_command(remote_command)

        def print_log(log):
            log = re.sub(r'(\[E\].*)\n', r'\033[0;31m\1\033[0m\n', log)  # error red
            log = re.sub(r'(\[W\].*)\n', r'\033[0;33m\1\033[0m\n', log)  # warning yellow
            sys.stdout.write(log)

        while True:
            try:
                rl, wl, xl = select.select([channel], [], [], 0.0)
                if len(rl) > 0:  # Must be stdout
                    print_log(channel.recv(1024))
            except:
                try:
                    print('close the SSH Client')
                    conn.ssh.close()
                except Exception as e:
                    print('exception when closing SSH Client: {}'.format(e))
                finally:
                    break
