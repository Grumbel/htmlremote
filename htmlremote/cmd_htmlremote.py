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
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from pkg_resources import resource_stream

import xdg.BaseDirectory
import yattag


class Service:

    def do(self, handler, data):
        pass

    def html(self, doc):
        pass


class ExecService(Service):

    def do(self, handler, data):
        self.execute(data[b'action'][0].decode())

    def execute(self, cmdline):
        subprocess.Popen(cmdline, shell=True)

    def html(self, doc):
        doc.asis("""  <section>
    <h2>Exec</h2>
    <form action="/service/exec" method="post" target="frame" style="width: 100%;">
      <!-- <label for="action">Command:</label> -->
      <input type="text" name="action" style="width: 100%;" />
    </form>
  </section>""")


class VolumeService(Service):

    def __init__(self):
        pass

    def do(self, handler, data):
        if data[b'action'][0] == b"mute":
            self.mute()
        else:
            self.adjust(data[b'action'][0].decode())

    def mute(self):
        subprocess.call(["amixer", "-D", "pulse", "set", "Master", "1+", "toggle"])

    def adjust(self, value):
        subprocess.call(["amixer", "-D", "pulse", "set", "Master", value])

    def html(self, doc):
        doc.asis("""  <section>
    <h2>Volume</h2>

    <div class="controls">
      <form action="/service/volume" method="post" target="frame">
        <button class="button" type="submit" name="action" value="mute">🔇</button>
      </form>

      <form>
        <button class="button" type="button" name="action" value="5%-" id="volumedown">🔉</button>
      </form>

      <form>
        <button class="button" type="button" name="action" value="5%+" id="volumeup">🔊</button>
      </form>

      <form action="/service/volume" method="post" target="frame" style="width: 45%;">
        <input type="range" min="0" max="100" value="50" class="slider" id="volumeslider" style="width: 100%;" />
      </form>
    </div>
  </section>""")


class GammaService(Service):

    def do(self, handler, data):
        self.gamma(data[b'action'][0].decode())

    def gamma(self, value):
        subprocess.call(["xgamma", "-gamma", value])

    def html(self, doc):
        doc.asis("""  <section>
    <h2>Gamma</h2>
    <div class="controls">
      <form action="/service/gamma" method="post" target="frame">
        <button type="submit" name="action" value="1.75" class="button">1.75</button>
      </form>

      <form action="/service/gamma" method="post" target="frame">
        <button type="submit" name="action" value="1.5" class="button">1.5</button>
      </form>

      <form action="/service/gamma" method="post" target="frame">
        <button type="submit" name="action" value="1.25" class="button">1.25</button>
      </form>

      <form action="/service/gamma" method="post" target="frame">
        <button type="submit" name="action" value="1.00" class="button">1.00</button>
      </form>

      <form action="/service/gamma" method="post" target="frame">
        <button type="submit" name="action" value="0.9" class="button">0.9</button>
      </form>

      <form action="/service/gamma" method="post" target="frame">
        <button type="submit" name="action" value="0.9" class="button">0.75</button>
      </form>
    </div>

    <form action="/service/gamma" method="post" target="frame">
      <label for="action">Gamma:</label>
      <input type="text" name="action" />
    </form>
  </section>""")


class WebService(Service):

    def do(self, handler, data):
        self.open_url(data[b'action'][0].decode())

    def open_url(self, url):
        subprocess.Popen(["firefox", url])

    def html(self, doc):
        doc.asis("""  <section>
    <h2>Web</h2>
    <form action="/service/web" method="post" target="frame" style="width: 100%;">
      <!-- <label for="action">URL:</label><br/> -->
      <input type="text" name="action" style="width: 100%;" />
    </form>
  </section>""")


class ScreenshotService(Service):

    def do(self, handler, data):
        return self.screenshot(handler)

    def screenshot(self, handler):
        cmd = 'DISPLAY=:0 xwd -silent -root | convert "XWD:-" "PNG:-"'
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)

        def result_callback(pngdata, handler):
            handler.send_response(200)
            handler.send_header('Content-type', 'image/png')
            handler.end_headers()
            handler.wfile.write(pngdata)

        return lambda handler, pngdata=result.stdout: result_callback(pngdata, handler)

    def html(self, doc):
        doc.asis("""<section>
    <h2>Screenshot</h2>
    <form action="/service/screenshot" method="post">
      <button type="submit" name="action" value="screenshot">Screenshot</button>
    </form>
  </section>""")


class KeyboardService(Service):

    def do(self, handler, data):
        if data[b'action'][0] == b'press':
            self.press(data[b'key'][0].decode())
        else:
            print("Unknown action: {}".format(data[b'action'][0]))

    def press(self, key):
        print("Pressing:", key)
        subprocess.call(['xdotool', 'key', key])

    def html(self, doc):
        _, tag, text = doc.tagtext()

        keys = [
            ["F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "F11", "F12"],
            ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ["minus", "-"], ["equal", "="]],
            ["q", "w", "e", "r", "t", "y", "u", "i", "o", "p", ["bracketleft", "["], ["bracketright", "]"]],
            ["a", "s", "d", "f", "g", "h", "j", "k", "l", ["semicolon", ";"], ["apostrophe", "'"]],
            ["z", "x", "c", "v", "b", "n", "m", ["comma", ","], ["period", "."], ["slash", "/"], ["backslash", "\\"]],
        ]

        def btn(label, key):
            with tag("form", action="/service/keyboard", method="post", target="frame"):
                with tag("button", klass="button", type="submit", name="action", value="press"):
                    text(label)
                doc.stag("input", klass="button", type="hidden", name="key", value=key)

        with tag('section'):
            with tag("h2"):
                text("Keyboard")
            # Frequently used buttons
            with tag('section'):
                btn("←", "Left")
                btn("↑", "Up")
                btn("↓", "Down")
                btn("→", "Right")
                btn("→", "Right")
                doc.stag("br")
                btn("Esc", "Esc")
                btn("Alt+Tab", "alt+Tab")
                btn("F", "f")
                btn("F11", "F11")
                btn("BackSpace", "BackSpace")

            # Full keyboard
            with tag('section'):
                def make_key(label, key):
                    with tag("form", action="/service/keyboard", method="post", target="frame"):
                        with tag("button", klass="keyboardbutton", type="submit", name="action", value="press"):
                            text(label)
                        with tag("input", type="hidden", name="key", value=key):
                            pass

                for row in keys:
                    for key in row:
                        if isinstance(key, str):
                            make_key(key, key)
                        else:
                            make_key(key[1], key[0])
                    doc.stag("br")

            btn("Space", "space")
            btn("Return", "Return")
            doc.stag("br")

            with tag("form", action="/service/keyboard", method="post", target="frame"):
                with tag("label"):
                    doc.attr(('for', 'action'))
                    text("Key: ")

                doc.stag("input", type="hidden", name="action", value="press")
                doc.stag("input", type="text", name="key", style="width: 20em;")


class MyHandler(BaseHTTPRequestHandler):

    def __init__(self, services, auth_token, *args):
        self.services = services
        self.auth_token = auth_token
        try:
            super().__init__(*args)
        except ssl.SSLError as err:
            if err.library == "SSL" and err.reason == "TLSV1_ALERT_UNKNOWN_CA":
                print("ignoring {}".format(err))
            else:
                raise

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

            with resource_stream("htmlremote", "default.css") as fin:
                content = fin.read()
                self.wfile.write(content)
        elif self.path == "/script.js":
            self.send_header('Content-type', 'application/javascript')
            self.end_headers()

            with resource_stream("htmlremote", "script.js") as fin:
                content = fin.read()
                self.wfile.write(content)
        else:
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            content = make_html(self.services).encode("UTF-8")
            self.wfile.write(content)

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


def make_html(services):
    doc, tag, text = yattag.Doc().tagtext()

    doc.asis("<!doctype html>")
    with tag("head"):
        with tag("title"):
            text("HTMLRemote")
        doc.stag("link", href="default.css", rel="stylesheet", type="text/css")
        doc.stag("meta", charset="utf-8")
        # prevent zoom on mobile devices, thus making it easier to press
        # buttons multiple times without accidentally triggering a zoom
        doc.stag("meta", name="viewport",
                 content="width=device-width, initial-scale=1.0, maximum-scale=1, user-scalable=0")
        with tag("script", type="text/javascript", src="script.js"):
            pass

    for _, service in services.items():
        service.html(doc)

    with tag("iframe", name="frame"):
        pass

    return doc.getvalue()


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
        "/service/keyboard": KeyboardService(),
        "/service/screenshot": ScreenshotService(),
        "/service/web": WebService(),
        "/service/exec": ExecService()
    }

    print("Server listening on {}:{}".format(hostname, port))
    for key, _ in services.items():
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
