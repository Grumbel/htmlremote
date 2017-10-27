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
import ssl
import sys
import socketserver
import subprocess
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer

# Web frameworks:
# Flask


class Service:
    pass


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

    def __init__(self, services, *args):
        self.services = services
        super().__init__(*args)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()

    def do_GET(self):
        print("-> '{}'".format(self.path))
        self.send_response(200)

        if self.path == "/default.css":
            self.send_header('Content-type', 'text/css')
            self.end_headers()
            print("Sending CSS")
            content = ""
            with open("default.css") as fin:
                content = fin.read()
            self.wfile.write(bytes(content, 'UTF-8'))
        else:
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            content = ""
            with open("index.html") as fin:
                content = fin.read()
            self.wfile.write(bytes(content, 'UTF-8'))

    def do_POST(self):
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


def parse_args(args):
    parser = argparse.ArgumentParser(description="HTML-based remote control")
    parser.add_argument("-p", "--port", type=int, default=9999,
                        help="Port to run the http server on")
    return parser.parse_args(args)


def main(argv):
    args = parse_args(argv[1:])

    hostname = ''
    port = args.port

    services = {
        "/service/volume": VolumeService(),
        "/service/gamma": GammaService(),
        "/service/web": WebService(),
        "/service/screenshot": ScreenshotService(),
        "/service/keyboard": KeyboardService()
    }

    print("Server listening on {}:{}".format(hostname, port))
    for key, value in services.items():
        print("  {}".format(key))

    httpd = HTTPServer((hostname, port), lambda *args: MyHandler(services, *args))
    # httpd.socket = ssl.wrap_socket (httpd.socket, certfile='server.pem', server_side=True)
    # openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes
    # https://gist.github.com/fxsjy/5465353
    # https://github.com/tianhuil/SimpleHTTPAuthServer/blob/master/SimpleHTTPAuthServer/__main__.py

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
