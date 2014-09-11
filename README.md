# qidev

```sh    
# see help
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
$ cd /path/to/my/project/ 
$ qidev install
# alternatively
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
