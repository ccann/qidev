#!/usr/bin/env python

import os
import zipfile
import argparse
import paramiko
from scp import SCPClient
import qi
import xml.etree.ElementTree as ET


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

    def install(self, pkg_absolute_path):
        """Install the package file at pkg_absolute_path onto the remote filesystem.
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


def get_package_uid(path):
    with open(os.path.join(path, 'manifest.xml'), 'r') as manifest:
        xml = ET.fromstring(manifest.read())
        try:
            uid = xml.attrib['uuid']
            return uid
        except KeyError:
            print 'no UUID found'
            return None


def zip_dir(path, zipfile):
    """Create a zip of contents of path by traversing it."""
    for root, dirs, files in os.walk(path):
        for f in files:
            zipfile.write(os.path.join(root, f),
                          arcname=os.path.relpath(os.path.join(root, f), path))


def create_package(package_path=None):
    """Create a package out of the contents of the current directory."""
    if not package_path:
        package_path = os.getcwd()
    pkg = get_package_uid(package_path) + '.pkg'
    path = os.path.join(package_path, '..', pkg)
    zipf = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)
    zip_dir(package_path, zipf)
    zipf.close()
    return path


def main():
    ip = 'Michelangelo.local'  # '10.1.42.21'
    pkg_abs_path = create_package('/home/ccanning/dev/robot-control/RobotControl')
    c = Connection(ip)
    pkg_name = c.install(pkg_abs_path)
    session = qi.Session(ip)
    pacman = session.service('PackageManager')
    pacman.install(os.path.join(Connection.install_path, pkg_name))
    c.delete_pkg_file(pkg_name)
    # parser = argparse.ArgumentParser(description='qidev')
    # parser.add_argument('--ip', default='localhost', type=str, help='IP address of the robot')
    # args = parser.parse_args()


if __name__ == '__main__':
    main()
