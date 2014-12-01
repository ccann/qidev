# qidev


## Installation

```sh
$ cd qidev/
$ sudo pip install -r requirements.txt
$ cd dist/qidev-X.X  # where X.X is the version number
$ sudo python setup.py install
```

You're going to need naoqi (in choregraphe/lib) in your PYTHONPATH. If you use fish shell you can
add the following to your config.fish: 

```sh
$ set -x PYTHONPATH $HOME/path/to/choregraphe-suite-x.x.x.xx/lib $PYTHONPATH
```

to test, open a terminal and type:
```sh
$ qidev --help
``` 

## Configuring robot address
Set the 'hostname' field in ~/.qidev to the IP address or hostname of the robot. Doing so points all future qidev commands to that address.
```sh
$ qidev config hostname Michelangelo.local
# shortcut...
$ qidev connect Michelangelo.local
```

## Installing a package
Provide the path to a directory containing a project manifest.
```sh
$ cd /path/to/my/project
$ qidev install .
# alternatively...
$ qidev install /path/to/my/project
```

## Showing content
```sh
$ qidev show  # see all packages installed
$ qidev show -s  # see all services installed (-s, --services)
$ qidev show -a  # see all active content (-a, --active)
$ qidev show -i  # inspect a package for details (-i, -p, --inspect, --package)
```
Return key prompts for package name with tab completion for package inpection.

## Starting and stopping behaviors and services
```sh
$ qidev start  # switch focus to an activity
$ qidev stop  # stop focused activity
$ qidev start -b  # (re)start a behavior or service (-b, --bm)
$ qidev stop -b  # stop a behavior or service (-b, --bm)
$ qidev start --id my-package-uuid  # specify package id, skip prompt
```
Return key prompts for behavior/service name with tab-completion in all cases

## Autonomous Life Management
```sh
$ qidev life on
$ qidev life off
```

## NaoQi Management
```sh
$ qidev nao restart
$ qidev nao stop
$ qidev nao start
```

## Power Management
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
$ qidev vol n  # set volume to 0 <= n <= 100
$ qidev vol +n  # increase current volume by n
$ qidev vol -n  # decrease current volume by n
$ qidev vol up  # increase volume by 10
$ qidev vol down  # decrease volume by 10
```

## Log Viewing
```sh
$ qidev log  # follow tail-naoqi.log on remote host
$ qidev log --cp  # copy tail-naoqi.log to local machine (--cp, --copy)
$ qidev config log_path /where/I/want/tail-naoqi.log/written  # '~' by default
```

## Dialog (work in progress)
```sh
$ qidev dialog  # show dialog window
```
Type to force input to the robot.  
