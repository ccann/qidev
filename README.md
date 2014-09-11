# qidev

see help
```sh    
$ qidev --help
```
## Connecting to a robot
two methods accomplish the same thing
```sh   
$ qidev config hostname Michelangelo.local
$ qidev connect Michelangelo.local
```
## Installing a package
    
```sh
$ cd /path/to/my/project/ 
$ qidev install
```
alternatively
```sh
$ qidev install -p /path/to/my/project/
```

## Showing content
```sh
# see all packages installed
$ qidev show
# see all services installed
$ qidev show -s
# see all active content
$ qidev show -a
# inspect a package for details
$ qidev show -i 
```
