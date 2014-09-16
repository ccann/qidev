import os
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


def install_handler(ns):
    """Install a package to a remote host or locally."""
    verb = verbose_print(ns.verbose)
    conn = Connection(verb)
    try:
        verb('Create package from directory: {}'.format(ns.path))
        abs_path = conn.create_package(ns.path)
        verb('Transfer package to {}'.format(conn.hostname))
        pkg_name = conn.transfer(abs_path)
        verb('Install package: {}'.format(pkg_name))
        conn.install_package(abs_path)
        verb('Clean up: {}'.format(pkg_name))
        conn.delete_pkg_file(abs_path)
    except IOError:
        if ns.path:
            print('%s: %s is not a project directory (does not contain manifest.xml)' %
                  (col.red('ERROR'), col.blue(ns.path)))
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
    conn = Connection(verb, ssh=False)
    pkg_data = conn.get_installed_package_data()
    if ns.s:
        io.show_installed_services(pkg_data)
    elif ns.i:
        io.prompt_for_package(pkg_data)
    elif ns.active:
        io.show_running(conn.get_running_behaviors(),
                        conn.get_running_services(),
                        pkg_data)
    else:
        io.show_installed_packages(pkg_data)


def start_handler(ns):
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    behaviors = conn.get_installed_behaviors()
    if ns.life:
        inp = io.prompt_for_behavior(behaviors)
        try:
            verb('Switch focus to: {}'.format(inp))
            conn.life_switch_focus(inp)
        except RuntimeError:  # this is a huge hack but its not my fault
            verb('Couldnt find behavior {} so appending "/.": {}'.format(inp, inp+'/.'))
            inp = inp+'/.'
            verb('switch focus to: {}'.format(inp))
            conn.life_switch_focus(inp)
    else:
        services = conn.get_declared_services()
        inp = io.prompt_for_behavior(services + behaviors)
        if inp in services:
            verb('Start service: {}'.format(inp))
            conn.start_service(inp)
        elif inp in behaviors:
            verb('Start behavior: {}'.format(inp))
            conn.start_behavior(inp)
        else:
            print('{}: {} is not an eligible behavior or service'.format(col.red('ERROR'),
                                                                         inp))


def stop_handler(ns):
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    if ns.life:
        conn.life_stop_focus()  # stop focused activity
    else:  # stop behavior/service
        services = conn.get_running_services()
        behaviors = conn.get_running_behaviors()
        inp = io.prompt_for_behavior(services + behaviors)
        if inp in services:
            conn.stop_service(inp)
        elif inp in behaviors:
            conn.stop_behavior(inp)
        else:
            print('{}: {} is not an eligible behavior or service'.format(col.red('ERROR'),
                                                                         inp))


def life_handler(ns):
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    if ns.state == 'on':
        conn.life_on()
    elif ns.state == 'off':
        conn.life_off()
    else:
        print('life state can only be on or off')


def nao_handler(ns):
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, qi_session=False)
    verb('nao action: {}'.format(ns.action))
    sshin, sshout, ssherr = conn.ssh.exec_command('sudo /etc/init.d/naoqi %s' % ns.action)
    io.format_nao_output(sshout, ns.action)


def reboot_handler(ns):
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    print('Rebooting ...')
    conn.robot_reboot()


def shutdown_handler(ns):
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    print('Shutting down ...')
    conn.robot_shutdown()


def vol_handler(ns):
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    verb('volume level: {}'.format(ns.level))
    target = conn.set_volume(ns.level)
    print('Setting volume to {}'.format(col.magenta(target)))


def wake_handler(ns):
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    print('Waking up {}'.format(conn.hostname))
    conn.wake_up()


def rest_handler(ns):
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    print('Put {} to rest'.format(conn.hostname))
    conn.rest()


def dialog_handler(ns):
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    verb('show dialog window')
    conn.init_dialog_window()
