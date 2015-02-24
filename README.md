# qidev

test

## Installation

```sh
$ cd qidev/
$ sudo pip install -r requirements.txt
$ cd dist/qidev-X.X  # where X.X is the version number
$ sudo python setup.py install
```

You're going to need qi (in choregraphe/lib) in your PYTHONPATH. If you use fish shell you can
add the following to your config.fish: 

```sh
$ set -x PYTHONPATH $HOME/path/to/choregraphe-suite-x.x.x.xx/lib $PYTHONPATH
```

to test, open a terminal and type:
```sh
$ qidev --help
``` 

## Connect to your robot
Set the 'hostname' field in ~/.qidev to the IP address or hostname of the robot. Doing so points all future qidev commands to that address.
```sh
$ qidev config hostname Michelangelo.local

# shortcut...
$ qidev connect Michelangelo.local
```

## Install a package
Point qidev to your application folder (containing the manifest.xml), package your project (create a .pkg), push it to the robot (via SCP), and install it (via PackageManager).
```sh
$ cd /path/to/my/project
$ qidev install .

# alternatively...
$ qidev install /path/to/my/project

# install on multiple robots
$ qidev install /path/to/my/project --ip Michelangelo.local Donatello.local Raphael.local Leonardo.local
```

## Remove a package
Remove an installed package from the robot.
```sh
$ qidev remove

# from multiple robots...
$ qidev remove --ip Michelangelo.local Donatello.local Raphael.local Leonardo.local
```
Return key prompts for package name or UUID with tab-completion. The set of eligible packages is the union of packages installed on all targeted robots. If the package selected for removal is not installed on one of the specified targets, it's just skipped.

## Show content
```sh
$ qidev show     # table of installed packages
$ qidev show -s  # table of installed services (-s, --services)
$ qidev show -a  # table of active content (-a, --active)
$ qidev show -i  # inspect a package for details (-i, -p, --inspect, --package)
```
Return key prompts for package name with tab-completion for package inpection.

## Starting and stopping behaviors and services
```sh
$ qidev start     # switch focus to an activity (with AutonomousLife)
$ qidev stop      # stop focused activity (with AutonomousLife)
$ qidev start -b  # (re)start a behavior or service (-b, --bm)
$ qidev stop -b   # stop a behavior or service (-b, --bm)
$ qidev start --id my-package-uuid  # specify package id, skip prompt
```
Return key prompts for behavior/service name with tab-completion in all cases

## Autonomous Life management
```sh
$ qidev life on
$ qidev life off
```

## NAOqi management
```sh
$ qidev nao restart
$ qidev nao stop
$ qidev nao start
```

## Power management
```sh
$ qidev reboot  
$ qidev shutdown  
```

## Stiffness
```sh
$ qidev rest  # put robot to rest
$ qidev wake  # wake up robot
```

## Volume
```sh
$ qidev vol n     # set volume to 0 <= n <= 100
$ qidev vol +n    # increase current volume by n
$ qidev vol -n    # decrease current volume by n
$ qidev vol up    # increase volume by 10
$ qidev vol down  # decrease volume by 10
```

## NAOqi logs
```sh
$ qidev log       # follow tail-naoqi.log on remote host
$ qidev log --cp  # copy tail-naoqi.log to local machine (--cp, --copy)
$ qidev config log_path /where/I/want/tail-naoqi.log/written  # $HOME by default
```

## Dialog (WIP)
```sh
$ qidev dialog  # interactive dialog window
```
Type to force input to the robot.  
