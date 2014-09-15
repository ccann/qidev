import os
import paramiko
from scp import SCPClient
import xml.etree.ElementTree as ET
import zipfile


class Connection():

    def __init__(self, hostname, port='9559', username='nao',
                 password='nao', ssh=True, virtual=False):
        self.hostname = str(hostname)
        # self.port = int(port)
        self.user = username
        self.pw = password
        self.virtual = virtual
        if self.virtual:
            self.install_path = os.path.expanduser('~')
        else:
            self.install_path = os.path.join('/home', 'nao')
        self.install_path = os.path.join(self.install_path,
                                         '.local', 'share', 'PackageManager', 'apps')
        if ssh:
            self.ssh = paramiko.SSHClient()
            self.ssh.load_system_host_keys()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())  # accept unknown keys
            if not self.virtual:
                self.ssh.connect(self.hostname,
                                 # port=self.port,
                                 username=self.user,
                                 password=self.pw,
                                 allow_agent=False,
                                 look_for_keys=False)  # have pw, don't look for private keys
                self.scp = SCPClient(self.ssh.get_transport())

    def transfer(self, pkg_absolute_path):
        """Transfer the package file at pkg_absolute_path onto the remote filesystem.
        :param pkg_absolute_path: absolute path to the package file.

        """
        pkg_name = pkg_absolute_path.split(os.sep)[-1]
        if not self.virtual:
            remote_path = os.path.join(self.install_path, pkg_name)
            # os.system('rsync -a --ignore-existing "{}" nao@{}:{}'.format(pkg_absolute_path,
            #                                                              self.hostname,
            #                                                              remote_path))
            self.scp.put(pkg_absolute_path, remote_path)
        return pkg_name

    def delete_pkg_file(self, abs_path):
        """Remove pkg_name from apps/ on robot or abs_path on local machine.
        :param pkg_name: the name of the package, e.g. my-package.pkg
        :param abs_path: the absolute path of the package on the local machine.

        """
        pkg_name = abs_path.split(os.sep)[-1]
        if self.virtual:  # delete the file from the local machine
            os.remove(abs_path)
        else:  # delete the file on teh remote machine
            remote_path_to_pkg = os.path.join(self.install_path, pkg_name)
            self.sftp = self.ssh.open_sftp()
            self.sftp.remove(remote_path_to_pkg)
            self.sftp.close()

    def get_package_uid(self, path):
        """Get the UUID of the package locatated at path by parsing the manifest.
        :params path: absolute path to the package directory.
        :return: the UUID of package.
        """
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
        """Create a package out of the contents of the current directory.
        :return: the absolute path to the package on the local machine.
        """
        if not pkg_path:
            pkg_path = os.getcwd()
        pkg = self.get_package_uid(pkg_path) + '.pkg'
        path = os.path.join(pkg_path, '..', pkg)
        zipf = zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED)
        self.zip_dir(pkg_path, zipf)
        zipf.close()
        return path

    def install_package(self, session, abs_path):
        """Install package on system.
        :param abs_path: absolute path to the package.
        :param session: qi session
        """
        pacman = session.service('PackageManager')
        pkg_name = abs_path.split(os.sep)[-1]
        if self.virtual:
            pacman.install(os.path.join(abs_path))
        else:
            pacman.install(os.path.join(self.install_path, pkg_name))

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
        services = [s['name'] for s in servman.services()]
        return [s for s in services if servman.isServiceRunning(s)]

    def get_declared_services(self, session):
        servman = session.service('ALServiceManager')
        return [s['name'] for s in servman.services()]

    def start_behavior(self, session, behavior):
        behman = session.service('ALBehaviorManager')
        behman.startBehavior(behavior)

    def stop_behavior(self, session, behavior):
        behman = session.service('ALBehaviorManager')
        behman.stopBehavior(behavior)

    def life_switch_focus(self, session, activity):
        life = session.service('ALAutonomousLife')
        life.switchFocus(activity)

    def life_stop_focus(self, session):
        life = session.service('ALAutonomousLife')
        life.stopFocus()

    def start_service(self, session, service):
        servman = session.service('ALServiceManager')
        if servman.isServiceRunning(service):
            servman.restartService(service)
        else:
            servman.startService(service)

    def stop_service(self, session, service):
        servman = session.service('ALServiceManager')
        servman.stopService(service)

    def life_off(self, session):
        life = session.service('ALAutonomousLife')
        life.setState('disabled')

    def life_on(self, session):
        life = session.service('ALAutonomousLife')
        life.setState('solitary')

    def robot_reboot(self, session):
        print('Rebooting ...')
        system = session.service('ALSystem')
        system.reboot()

    def robot_shutdown(self, session):
        print('Shutting down ...')
        system = session.service('ALSystem')
        system.shutdown()

    def set_volume(self, session, level):
        audio = session.service('ALAudioDevice')
        curr_level = int(audio.getOutputVolume())
        if level == 'up':
            target = min(curr_level + 10, 100)
        elif level == 'down':
            target = max(curr_level - 10, 0)
        elif '+' in level:
            target = min(curr_level + int(level.replace('+', '')), 100)
        elif '-' in level:
            target = max(curr_level - int(level.replace('-', '')), 0)
        else:
            target = min(max(int(level), 0), 100)
        audio.setOutputVolume(target)
        return target
