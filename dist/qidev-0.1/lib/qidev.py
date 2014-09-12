#!/usr/bin/env python

import argparse
import handlers as hs


def main():
    parser = argparse.ArgumentParser(description='qidev')
    parser.add_argument('--verbose', help='be verbose', dest='verbose',
                        action='store_true', default=False)

    subs = parser.add_subparsers(help='commands', dest='command')

    config_parser = subs.add_parser('config', help='configure defaults for qidev')
    config_parser.add_argument('field', help='the field to configure', type=str)
    config_parser.add_argument('value', help='set field to value', type=str)

    connect_parser = subs.add_parser('connect', help='shortcut to config hostname')
    connect_parser.add_argument('hostname', help='hostname of the robot', type=str)

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

    start_parser = subs.add_parser('start', help='start a behavior, prompts for behavior name')
    start_parser.add_argument('-b', '--bm', help='use behavior manager to start behavior directly',
                              dest='bm', action='store_true')
    stop_parser = subs.add_parser('stop', help='stop a behavior, prompts for behavior name')
    stop_parser.add_argument('-b', '--bm', help='use behavior manager to stop behavior directly',
                             dest='bm', action='store_true')

    life_parser = subs.add_parser('life', help='toggle ALAutonomousLife')
    life_parser.add_argument('state', help='turn ALAutonomousLife on or off', type=str)

    nao_parser = subs.add_parser('nao', help='run nao commands on remote robot')
    nao_parser.add_argument('action', help='restart, start, stop naoqi on remote host',
                            type=str)

    power_parser = subs.add_parser('robot', help='shutdown or reboot the robot')
    power_parser.add_argument('action', help='shutdown or reboot', type=str)

    volume_parser = subs.add_parser('vol', help='adjust the volume on the robot')
    volume_parser.add_argument('level', help='int from 0 to 100', type=int)

    args = parser.parse_args()

    if args.command == 'install':
        hs.install_handler(args)

    elif args.command == 'config':
        hs.config_handler(args)

    elif args.command == 'connect':
        hs.connect_handler(args)

    elif args.command == 'show':
        hs.show_handler(args)

    elif args.command == 'start' or args.command == 'stop':
        hs.state_handler(args.command, args)

    elif args.command == 'life':
        hs.life_handler(args)

    elif args.command == 'nao':
        hs.nao_handler(args)

    elif args.command == 'robot':
        hs.power_handler(args)

    elif args.command == 'vol':
        hs.volume_handler(args)


if __name__ == '__main__':
    main()
