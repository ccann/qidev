#!/usr/bin/env python

import os
import qi
import zipfile
import argparse
import paramiko
from scp import SCPClient
import xml.etree.ElementTree as ET
import clio


class Connection():

    install_path = os.path.join('/home/nao/.local/share/PackageManager/apps')

    def __init__(self, ip, port='9559', username='nao', password='nao'):
        self.ip = str(ip)
        # self.port = int(port)
        self.user = username
        self.pw = password
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # auto-accept unknown keys
        self.ssh.connect(self.ip,
                         # port=self.port,
                         username=self.user,
                         password=self.pw,
                         allow_agent=False,
                         look_for_keys=False)  # already have pw, don't look for private keys
        self.scp = SCPClient(self.ssh.get_transport())

    def transfer(self, pkg_absolute_path):
        """Transfer the package file at pkg_absolute_path onto the remote filesystem.
        :param pkg_absolute_path: absolute path to the package file.

        """
        pkg_name = pkg_absolute_path.split(os.sep)[-1]
        remote_path = os.path.join(Connection.install_path, pkg_name)
        self.scp.put(pkg_absolute_path, remote_path)
        return pkg_name

    def delete_pkg_file(self, pkg_name):
        """Remove pkg_name from apps/ on robot.
        :param pkg_name: the name of the package, e.g. my-package.pkg

        """
        self.sftp = self.ssh.open_sftp()
        self.sftp.remove(os.path.join(Connection.install_path, pkg_name))
        self.sftp.close()

    def get_package_uid(self, path):
        with open(os.path.join(path, 'manifest.xml'), 'r') as manifest:
            xml = ET.fromstring(manifest.read())
            try:
                uid = xml.attrib['uuid']
                return uid
            except KeyError:
                print 'no UUID found'
                return None

    def zip_dir(self, path, zipfile):
        """Create a zip of contents of path by traversing it."""
        for root, dirs, files in os.walk(path):
            for io in files:
                zipfile.write(os.path.join(root, io),
                              arcname=os.path.relpath(os.path.join(root, io), path))

    def create_package(self, pkg_path=None):
        """Create a package out of the contents of the current directory."""
        if not pkg_path:
            pkg_path = os.getcwd()
        pkg = self.get_package_uid(pkg_path) + '.pkg'
        path = os.path.join(pkg_path, '..', pkg)
        zipf = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)
        self.zip_dir(pkg_path, zipf)
        zipf.close()
        return path

    def get_installed_package_data(self, session):
        pacman = session.service('PackageManager')
        return pacman.packages()

    def get_running_behaviors(self, session):
        behman = session.service('ALBehaviorManager')
        return behman.getRunningBehaviors()

    def get_installed_behaviors(self, session):
        behman = session.service('ALBehaviorManager')
        return behman.getInstalledBehaviors()

    def get_running_services(self, session):
        servman = session.service('ALServiceManager')
        return servman.services()

    def start_behavior(self, session, behavior):
        behman = session.service('ALBehaviorManager')
        behman.startBehavior(behavior)

    def stop_behavior(self, session, behavior):
        behman = session.service('ALBehaviorManager')
        behman.stopBehavior(behavior)


def main():
    parser = argparse.ArgumentParser(description='qidev')
    subparsers = parser.add_subparsers(help='command')

    # connect_parser = subparsers.add_parser('connect', help='Connect to a remote robot')
    # connect_parser.add_argument('ip', help='IP address of the robot', action=ConnectAction)

    install_parser = subparsers.add_parser('install', help='Install a package on a robot')
    install_parser.add_argument('-p', help='Absolute path of the package directory')
    install_parser.add_argument('ip', help='IP address of the robot', action=InstallAction)

    args = parser.parse_args()

    # qidev connect ip (create a connection, zip up a package, transfer it to robot at IP)


# class ConnectAction(argparse.Action):

#     def __init__(self, option_strings, dest, nargs=None, **kwargs):
#         argparse.Action.__init__(self, option_strings, dest, **kwargs)

#     def __call__(self, parser, namespace, values, option_string=None):
#         print 'connect to {}'.format(values)
#         conn = Connection(str(values))


class InstallAction(argparse.Action):

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        argparse.Action.__init__(self, option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        print 'install to {}'.format(values)
        conn = Connection(str(values))
        print namespace
        if namespace.p:
            abs_path = conn.create_package(namespace.p)
        else:
            abs_path = conn.create_package()
        pkg_name = conn.transfer(abs_path)
        session = qi.Session(values)
        pacman = session.service('PackageManager')
        pacman.install(os.path.join(Connection.install_path, pkg_name))
        conn.delete_pkg_file(pkg_name)


# class ShowAction(argparse.Action):

#     def __init__(self, option_strings, dest, nargs=None, **kwargs):
#         argparse.Action.__init__(self, option_strings, dest, **kwargs)

#     def __call__(self, parser, namespace, values, option_string=None):
#         # qidev show (print installed packages)
#         io = clio.IO()
#         session = qi.Session(values)
#         pkg_data = conn.get_installed_package_data(session)
#         io.show_installed_packages(pkg_data)




    # # qidev show -s
    # io.show_installed_services(pkg_data)

    # # qidev show -i
    # # qidev inspect
    # # io.prompt_for_package(pkg_data)

    # # qidev info (show running behaviors, services)
    # io.show_running(conn.get_running_behaviors(session),
    #                 conn.get_running_services(session),
    #                 pkg_data)

    # # qidev start
    # b = io.prompt_for_behavior(conn.get_installed_behaviors(session))
    # conn.start_behavior(session, b)

    # # qidev stop
    # b = io.prompt_for_behavior(conn.get_running_behaviors(session))
    # conn.stop_behavior(session, b)



if __name__ == '__main__':
    main()
