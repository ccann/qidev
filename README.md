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

## Connecting to a robot
```sh
$ qidev config hostname Michelangelo.local
# shortcut...
$ qidev connect Michelangelo.local
```

## Installing a package
```sh
$ qidev install --help
$ cd /path/to/my/project/ 
$ qidev install .
$ qidev install /path/to/my/project/  # alternatively
```

## Showing content
```sh
$ qidev show  # see all packages installed
$ qidev show -s  # see all services installed
$ qidev show -a  # see all active content
$ qidev show -i  # inspect a package for details
```
return prompts for package name with tab completion for package inpection

## Starting and stopping behaviors and services
```sh
$ qidev start  # (re)start a behavior or service
$ qidev stop  # stop a behavior or service
$ qidev start -l  # switch focus to an activity
$ qidev stop -l  # stop focused activity
```
return prompts for behavior/service name with tab-completion in all cases

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

## Dialog
```sh
$ qidev dialog  # show dialog window
```
Type to force input to the robot.
