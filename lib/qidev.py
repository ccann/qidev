#!/usr/bin/env python

import os
import qi
import argparse
import clio
import config
from connection import Connection
import socket
from clint.textui import colored as col


def main():
    parser = argparse.ArgumentParser(description='qidev')
    parser.add_argument('--verbose', help='be verbose', dest='verbose',
                        action='store_true', default=False)

    subs = parser.add_subparsers(help='commands', dest='command')

    config_parser = subs.add_parser('config', help='configure defaults for qidev')
    config_parser.add_argument('field', help='the field to configure', type=str)
    config_parser.add_argument('value', help='set field to value', type=str)

    install_parser = subs.add_parser('install',
                                     help='package and install a project directory on a robot')
    install_parser.add_argument('-p', help='absolute to the directory to install as a package',
                                type=str)

    show_parser = subs.add_parser('show', help='show the packages installed on a robot')
    mutex = show_parser.add_mutually_exclusive_group()
    mutex.add_argument('-s', '--services', help='show the services installed on the robot',
                       action='store_true', dest='s')
    mutex.add_argument('-i', '--inspect', '--package',
                       help='inspect package, prompts for package name',
                       action='store_true', dest='i')
    mutex.add_argument('-a', '--active', '--running',
                       help='show active content (behaviors and services)',
                       action='store_true', dest='active')

    subs.add_parser('start', help='start a behavior, prompts for behavior name')
    subs.add_parser('stop', help='stop a behavior, prompts for behavior name')

    args = parser.parse_args()

    if args.command == 'install':
        install_handler(args)

    elif args.command == 'config':
        config_handler(args)

    elif args.command == 'show':
        show_handler(args)

    elif args.command == 'start' or args.command == 'stop':
        behavior_handler(args.command, args)


def install_handler(ns):
    verb = verbose_print(ns.verbose)
    conn, session = create_connection(ns, verb)
    verb('Create package from directory: {}'.format(ns.p))
    abs_path = conn.create_package(ns.p)
    verb('Transfer package to {}'.format(conn.hostname))
    pkg_name = conn.transfer(abs_path)
    verb('Install package: {}'.format(pkg_name))
    conn.install_package(session, abs_path)
    verb('Clean up: {}'.format(pkg_name))
    conn.delete_pkg_file(abs_path)


def config_handler(ns):
    verb = verbose_print(ns.verbose)
    field = ns.field.strip()
    if field == 'hostname':
        verb('Set {} to {}'.format(field, ns.value))
        config.write_hostname(ns.value)
    else:
        print('ERROR: unsupported field {}'.format(field))


def show_handler(ns):
    verb = verbose_print(ns.verbose)
    conn, session = create_connection(ns, verb)
    io = clio.IO()
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


def behavior_handler(state, ns):
    verb = verbose_print(ns.verbose)
    conn, session = create_connection(ns, verb)
    io = clio.IO()
    if state == 'start':
        b = io.prompt_for_behavior(conn.get_installed_behaviors(session))
        conn.start_behavior(session, b)
    else:
        b = io.prompt_for_behavior(conn.get_running_behaviors(session))
        conn.stop_behavior(session, b)


def verbose_print(flag):
    def func(text):
        if flag:
            print(text)
    return func


def create_connection(ns, verb):
    try:
        hostname = config.read_hostname()
        verb('Connect to {}'.format(hostname))
        session = qi.Session(hostname)
        conn = Connection(hostname)
    except socket.gaierror as e:
        raise RuntimeError('{}: {} ... for hostname: {}'.format(col.red('ERROR'),
                                                                e,
                                                                col.blue(hostname)))
    except socket.error as e:
        # assuming this is a virtual bot...
        conn = Connection(hostname, virtual=True)
    return conn, session

if __name__ == '__main__':
    main()
