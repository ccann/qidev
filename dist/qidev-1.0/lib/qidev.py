#!/usr/bin/env python

"""qidev.py

Instantiate the parser, all subparsers, and their arguments. Execute the
handler associated with the subparser.
"""

import sys
import argparse

running = True


def main():
    try:
        import handlers as hs
    except ImportError as e:
        print('Missing Dependency: {}'.format(e))
        sys.exit()

    parser = argparse.ArgumentParser(description='qidev')
    parser.add_argument('--verbose', help='be verbose', dest='verbose',
                        action='store_true', default=False)
    subs = parser.add_subparsers(help='commands', dest='command')

    config_parser = subs.add_parser('config', help='configure defaults for qidev')
    config_parser.add_argument('field', help='the field to configure', type=str)
    config_parser.add_argument('value', help='set field to value', type=str)

    # ########################################################
    connect_parser = subs.add_parser('connect', help='connect to a robot (ip/hostname)')
    connect_parser.add_argument('hostname', help='hostname or IP address of the robot', type=str)

    # ########################################################
    subs.add_parser('info', help="what's up?")

    # ########################################################
    install_parser = subs.add_parser('install',
                                     help='package and install a project directory on a robot')
    install_parser.add_argument('path',
                                help='path to the project directory (containing manifest.xml',
                                type=str)
    install_parser.add_argument('--ip', nargs='*', type=str, dest='ip',
                                help='specify hostname(es)/IP address(es)')

    # ########################################################
    remove_parser = subs.add_parser('remove', help='remove a package from a robot')
    remove_parser.add_argument('--ip', nargs='*', type=str, dest='ip',
                               help='specify hostname(es)/IP address(es)')

    # ########################################################
    show_parser = subs.add_parser('show', help='show the packages installed on a robot')
    mutex = show_parser.add_mutually_exclusive_group()
    mutex.add_argument('-s', '--services', help='show the services installed on the robot',
                       action='store_true', dest='services')
    mutex.add_argument('-i', '--inspect',
                       help='inspect package, prompts for package name',
                       action='store_true', dest='inspect')
    mutex.add_argument('-a', '--active',
                       help='show active content (behaviors and services)',
                       action='store_true', dest='active')

    # ########################################################
    start_parser = subs.add_parser('start',
                                   help='start an activity, behavior, or service; prompts for ' +
                                   'name on return')
    start_parser.add_argument('--ip', nargs='*', type=str, dest='ip',
                              help='specify hostname(es)/IP address(es)')
    start_parser.add_argument('--id', '--name',
                              help='specify the name of the behavior/service/activity to start',
                              dest='name', type=str)
    start_parser.add_argument('-b', '--bm', '--behavior',
                              help='use ALBehaviorManager to start an installed behavior',
                              dest='behavior', action='store_true')
    start_parser.add_argument('-s', '--sm', '--service',
                              help='use ALServiceManager to start a declared service',
                              dest='service', action='store_true')

    # ########################################################
    stop_parser = subs.add_parser('stop',
                                  help='stop an activity, behavior, or service; prompts for ' +
                                  'name on return')
    stop_parser.add_argument('--ip', nargs='*', type=str, dest='ip',
                             help='specify hostname(es)/IP address(es)')
    stop_parser.add_argument('--id', '--name',
                             help='specify the name of the behavior/service/activity to stop',
                             dest='name', type=str)
    stop_parser.add_argument('-b', '--bm', '--behavior',
                             help='use ALBehaviorManager to stop a behavior',
                             dest='behavior', action='store_true')
    stop_parser.add_argument('-s', '--sm', '--service',
                             help='use ALServiceManager to stop a running service',
                             dest='service', action='store_true')

    # ########################################################
    life_parser = subs.add_parser('life', help='toggle Autonomous Life state')
    life_parser.add_argument('state', help='turn Autonomous Life on or off', type=str)

    # ########################################################
    nao_parser = subs.add_parser('nao', help='naoqi restart, start, stop')
    nao_parser.add_argument('action', help='restart, start, stop naoqi on remote host',
                            type=str)
    nao_parser.add_argument('--ip', nargs='*', type=str, dest='ip',
                            help='specify hostname(es)/IP address(es)')

    # ########################################################
    reboot_parser = subs.add_parser('reboot', help='reboot the robot')
    reboot_parser.add_argument('--ip', nargs='*', type=str, dest='ip',
                               help='specify hostname(es)/IP address(es)')

    # ########################################################
    shutdown_parser = subs.add_parser('shutdown', help='shutdown the robot')
    shutdown_parser.add_argument('--ip', nargs='*', type=str, dest='ip',
                                 help='specify hostname(es)/IP address(es)')

    subs.add_parser('rest', help='put the robot to rest')
    subs.add_parser('wake', help='wake up the robot')

    # #########################################################
    volume_parser = subs.add_parser('vol', help='adjust the volume on the robot')
    volume_parser.add_argument('level',
                               help='int from 0 to 100 with optional + or - prefix to modify ' +
                               'current level; use "up" and "down" to increase or decrease ' +
                               'volume by 10.', type=str)
    volume_parser.add_argument('--ip', nargs='*', type=str, dest='ip',
                               help='specify hostname(es)/IP address(es)')

    # #########################################################
    subs.add_parser('dialog', help='interactive dialog window')

    # #########################################################
    log_parser = subs.add_parser('log', help='view or copy naoqi logs')
    log_parser.add_argument('--cp', '--copy',
                            help='copy tail-naoqi.log to local machine; configure log_path to ' +
                            'change where this file is written.', action='store_true', dest='cp')

    args = parser.parse_args()
    handler = args.command + '_handler'
    if not args.verbose:
        sys.tracebacklimit = 0
    getattr(hs, handler)(args)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()

    except RuntimeError as e:
        print(e)
        sys.exit()
