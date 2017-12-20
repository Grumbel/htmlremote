#!/usr/bin/env python3

# HTML-based remote control
# Copyright (C) 2017 Ingo Ruhnke <grumbel@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import argparse
import base64
import os
import ssl
import sys
import socketserver
import subprocess
import xdg.BaseDirectory
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from pkg_resources import Requirement, resource_filename


class Service:
    pass


class ExecService:

    def do(self, handler, data):
        self.execute(data[b'action'][0].decode())

    def execute(self, cmdline):
        subprocess.Popen(cmdline, shell=True)


class VolumeService:

    def __init__(self):
        pass

    def do(self, handler, data):
        print(data)
        if data[b'action'][0] == b"mute":
            self.mute()
        else:
            self.adjust(data[b'action'][0].decode())

    def mute(self):
        subprocess.call(["amixer", "-D", "pulse", "set", "Master",  "1+", "toggle"])

    def adjust(self, value):
        subprocess.call(["amixer", "-D", "pulse", "set", "Master", value])


class GammaService:

    def do(self, handler, data):
        self.gamma(data[b'action'][0].decode())

    def gamma(self, value):
        subprocess.call(["xgamma", "-gamma", value])


class WebService:

    def do(self, handler, data):
        self.open_url(data[b'action'][0].decode())

    def open_url(self, url):
        subprocess.Popen(["firefox", url])


class ScreenshotService:

    def do(self, handler, data):
        return self.screenshot(handler)

    def screenshot(self, handler):
        cmd = 'DISPLAY=:0 xwd -silent -root | convert "XWD:-" "PNG:-"'
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        pngdata = result.stdout
        print(len(pngdata))

        def result_callback(pngdata, handler):
            handler.send_response(200)
            handler.send_header('Content-type', 'image/png')
            handler.end_headers()
            handler.wfile.write(pngdata)

        return lambda handler, pngdata=pngdata: result_callback(pngdata, handler)


class KeyboardService:

    def do(self, handler, data):
        if (data[b'action'][0] == b'press'):
            self.press(data[b'key'][0].decode())
        else:
            print("Unknown action: {}".format(data[b'action'][0]))

    def press(self, key):
        print("Pressing:", key)
        subprocess.call(['xdotool', 'key', key])


class MyHandler(BaseHTTPRequestHandler):

    def __init__(self, services, auth_token, *args):
        self.services = services
        self.auth_token = auth_token
        super().__init__(*args)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

    def do_GET(self):
        if self.auth_token:
            if self.headers['Authorization'] == ("Basic " + self.auth_token):
                self.do_GET_authorized()
            else:
                self.do_GET_rejected()
                print("Authorization failed:", self.headers['Authorization'], "!=", self.auth_token)
        else:
            self.do_GET_authorized()

    def do_GET_rejected(self):
        self.send_response(401)
        self.send_header('WWW-Authenticate', 'Basic realm="htmlremote"')
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET_authorized(self):
        print("-> '{}'".format(self.path))
        self.send_response(200)

        if self.path == "/default.css":
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            print("Sending CSS")

            filename = resource_filename(Requirement.parse("htmlremote"), "default.css")

            content = ""
            with open(filename) as fin:
                content = fin.read()
            self.wfile.write(bytes(content, 'UTF-8'))
        else:
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            filename = resource_filename(Requirement.parse("htmlremote"), "index.html")

            content = ""
            with open(filename) as fin:
                content = fin.read()
            self.wfile.write(bytes(content, 'UTF-8'))

    def do_POST(self):
        if self.auth_token:
            if self.headers['Authorization'] == ("Basic " + self.auth_token):
                self.do_POST_authorized()
            else:
                self.do_GET_rejected()
                print("Authorization failed:", self.headers['Authorization'], "!=", self.auth_token)
        else:
            self.do_POST_authorized()

    def do_POST_authorized(self):
        service = self.services[self.path]

        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(content_length, post_data)
        data = parse_qs(post_data)

        result = service.do(self, data)

        if result is not None:
            result(self)
        else:
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes("Success", 'UTF-8'))


def parse_args(argv):
    parser = argparse.ArgumentParser(description="HTML-based remote control")
    parser.add_argument("-p", "--port", type=int, default=9999,
                        help="Port to run the http server on")
    parser.add_argument("--no-ssl", action='store_true', default=False,
                        help="Disable SSL support")

    auth = parser.add_mutually_exclusive_group(required=True)
    auth.add_argument("--no-auth", action='store_true', default=False,
                        help="Disable authentification")
    auth.add_argument("-a", "--auth", metavar="USER:PASSWORD", type=str, default=None,
                        help="Require USER and PASSWORD to access the htmlremote website")

    return parser.parse_args(argv)


def main(argv):
    args = parse_args(argv[1:])

    hostname = ''
    port = args.port

    cfg_path = os.path.join(xdg.BaseDirectory.xdg_config_home, "htmlremote")
    if not os.path.exists(cfg_path):
        os.makedirs(cfg_path)

    services = {
        "/service/volume": VolumeService(),
        "/service/gamma": GammaService(),
        "/service/web": WebService(),
        "/service/screenshot": ScreenshotService(),
        "/service/keyboard": KeyboardService(),
        "/service/exec": ExecService()
    }

    print("Server listening on {}:{}".format(hostname, port))
    for key, value in services.items():
        print("  {}".format(key))

    httpd = HTTPServer((hostname, port), lambda *args: MyHandler(services, auth_token, *args))

    if args.no_auth:
        auth_token = None
    else:
        auth_token = base64.b64encode(args.auth.encode()).decode()

    if not args.no_ssl:
        certfile = os.path.join(cfg_path, "cert.pem")
        if not os.path.exists(certfile):
            print("Generating SSL certificate...")
            subprocess.check_call(["openssl", "req",
                                   "-new", "-x509",
                                   "-nodes",
                                   "-days", "9999",
                                   "-subj", "/CN=localdomain/O=HTMLRemote/C=US",
                                   "-keyout", certfile,
                                   "-out", certfile])
        httpd.socket = ssl.wrap_socket(httpd.socket, server_side=True, certfile=certfile)

    print("Launching server")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass

    httpd.server_close()


def main_entrypoint():
    main(sys.argv)


if __name__ == '__main__':
    main_entrypoint()


# EOF #
