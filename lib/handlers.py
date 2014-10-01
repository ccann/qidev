import os
import clio as io
import config
from connection import Connection
from clint.textui import colored as col
# import curses
# import functools
# import urwid


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
        local_pkg = os.path.join(ns.path, '..', pkg_name)
        verb('Remove locally: {}'.format(local_pkg))
        os.remove(local_pkg)
    except IOError:
        if ns.path:
            print('%s: %s is not a project directory (does not contain manifest.xml)' %
                  (col.red('ERROR'), col.blue(ns.path)))
        else:
            print('%s: %s is not a project directory (does not contain manifest.xml)' %
                  (col.red('ERROR'), col.blue(os.getcwd())))


def remove_handler(ns):
    verb = verbose_print(ns.verbose)
    conn = Connection(verb)
    pkg_data = conn.get_installed_package_data()
    inp = io.prompt_for_package(pkg_data)
    conn.remove_package(inp)


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
    verb('Check installed packages...')
    pkg_data = conn.get_installed_package_data()
    if ns.s:
        verb('Show installed services')
        io.show_installed_services(verb, pkg_data)
    elif ns.i:
        inp = io.prompt_for_package(pkg_data)
        io.show_package_details(inp, pkg_data)
    elif ns.active:
        verb('Show active content')
        io.show_running(conn.get_running_behaviors(),
                        conn.get_running_services(),
                        pkg_data)

        # def refresh_content(value, *args):
        #     behaviors = conn.get_running_behaviors()
        #     services = conn.get_running_services()
        #     choices = behaviors + services
        #     os.write(io.pipe, ';'.join(choices))

        # behman = conn.session.service('ALBehaviorManager')
        # servman = conn.session.service('ALServiceManager')
        # beh_started_id = behman.behaviorStarted.connect(refresh_content)
        # beh_stopped_id = behman.behaviorStopped.connect(refresh_content)
        # serv_started_id = servman.serviceStarted.connect(refresh_content)
        # serv_stopped_id = servman.serviceStopped.connect(refresh_content)

        # io.show_running(conn)
        # stdscr = ready_screen()

        # def refresh_content(value, *args):
        #     if not value == 'first':
        #         # curses.flash()
        #         stdscr.clear()
        #     io.show_running(stdscr,
        #                     conn,
        #                     value,
        #                     pkg_data)
        #     stdscr.refresh()
        # refresh_content('first')

        # def disconnect():
        #     behman.behaviorStarted.disconnect(beh_started_id)
        #     behman.behaviorStopped.disconnect(beh_stopped_id)
        #     servman.serviceStarted.disconnect(serv_started_id)
        #     servman.serviceStopped.disconnect(serv_stopped_id)
        #     close_screen(stdscr)

        # while(True):
        #     try:
        #         c = stdscr.getch()
        #         if c == ord('q'):
        #             disconnect()
        #             break
        #     except KeyboardInterrupt:
        #         disconnect()
        #     break
    else:
        io.show_installed_packages(verb, pkg_data)


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
        print('Life state can only be "on" or "off"')


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
    verb('Volume level: {}'.format(ns.level))
    target = conn.set_volume(ns.level)
    print('Setting volume to {}'.format(col.magenta(target)))


def wake_handler(ns):
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    print('Waking up {}'.format(conn.get_robot_name()))
    conn.wake_up()


def rest_handler(ns):
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    print('Put {} to rest'.format(conn.get_robot_name()))
    conn.rest()


def dialog_handler(ns):
    verb = verbose_print(ns.verbose)
    conn = Connection(verb, ssh=False)
    verb('Show dialog window')
    io.show_dialog_header(conn)
    conn.init_dialog_window()


# def ready_screen():
#     stdscr = curses.initscr()
#     curses.start_color()
#     curses.use_default_colors()
#     curses.noecho()
#     curses.curs_set(0)
#     curses.cbreak()  # react instantly to 'q' for example
#     return stdscr


# def close_screen(stdscr):
#     curses.nocbreak()
#     stdscr.keypad(0)
#     curses.curs_set(1)
#     curses.echo()  # undo everything
#     curses.endwin()
