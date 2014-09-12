# qidev
```sh
$ qidev --help  # see help
```

## Installation
Navigate to the root level of the qidev package, then:
```sh
$ pip install -r requirements.txt
```

## Connecting to a robot
```sh
$ qidev config hostname Michelangelo.local
# shortcut...
$ qidev connect Michelangelo.local
```

## Installing a package
```sh
$ cd /path/to/my/project/ 
$ qidev install
# alternatively, specify a path
$ qidev install -p /path/to/my/project/
```

## Showing content
```sh
$ qidev show  # see all packages installed
$ qidev show -s  # see all services installed
$ qidev show -a  # see all active content
$ qidev show -i  # inspect a package for details
```
RET prompts for package name with tab completion for package inpection

## Starting and stopping behaviors and services
```sh
$ qidev start  # (re)start a behavior/service  
$ qidev stop  # stop a behavior/service
```
RET prompts for behavior/service name with tab-completion
