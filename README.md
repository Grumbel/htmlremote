HTMLRemote
==========

htmlremote is a simple Python based webserver that provides remote
access to a Linux machine via the web.

Usage
-----

    $ htmlremote --help
    usage: htmlremote [-h] [-p PORT] [--no-ssl] [--no-auth] [-a USER:PASSWORD]
    
    HTML-based remote control
    
    optional arguments:
      -h, --help            show this help message and exit
      -p PORT, --port PORT  Port to run the http server on
      --no-ssl              Disable SSL support
      --no-auth             Disable authentification
      -a USER:PASSWORD, --auth USER:PASSWORD
                            Require USER and PASSWORD to access the htmlremote
                            website

Requirements
------------

htmlremote makes use of numerous command line applications to accive
it's functionality.

* OpenSSL
* yattag
* xdotool
* xwd
* covert
* amixer

Features
--------

* screenshot
* keyboard input
* gamma setting
* volume control

Screenshot
----------
![ScreenShot](https://raw.github.com/Grumbel/htmlremote/master/screenshot.png)

Bugs
----

The webrowser will report the SSL certificates as invalid, as it is
self-signed.