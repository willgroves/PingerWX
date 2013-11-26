PingerWX
========

## Description: 

PingerWX is a WX-based http graphical ping tool. It is 
a simple tool for checking network connectivity and http service
response. This is particularly useful when making network routing
or firewall configuration changes. This tool is cross platform and is
verified to work in Windows, Linux, and OSX (assuming python and the
prerequisite libraries are installed).

## Author: 

Will Groves 2013

## Usage Examples: (see also run_pinger.sh) 

python Pinger.py --hq 10.8.0.1 --hq www.yahoo.com

python Pinger.py --update-ms 100 --check-freq 50 --hq 10.8.0.1 --hq www.yahoo.com --fontsize 20

## Command Line Options: ##

```
  -h, --help            show this help message and exit
  --update-ms=TIMERMS   display update interval in ms (default 450)
  --check-freq=CHECKFREQUENCY
                        frequency that hosts are queried in terms of number of
                        display updates (default 7)
  --max-green=GREENSECS
                        number of seconds until green color dissipates
                        (default 4)
  --max-red=REDSECS     number of seconds until red color reaches full
                        strength (default 20)
  --hq=HTTPHOSTS, --httpquery=HTTPHOSTS
                        specify host and port to query via http (ip:port)
```