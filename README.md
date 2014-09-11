# qidev
    
    # see help
    $ qidev --help

## Connecting to a robot
   
    $ qidev config hostname Michelangelo.local
    # shortcut to do the same thing
    $ qidev connect Michelangelo.local

## Installing a package
    
    $ cd /path/to/my/project/ 
    $ qidev install

    # alternatively
    qidev install -p /path/to/my/project/

## Showing content
    # see all packages installed
    $ qidev show
    # see all services installed
    $ qidev show -s
    # see all active content
    $ qidev show -a
    # inspect a package for details
    $ qidev show -i 

