#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import BaseHTTPServer
import sys
import subprocess
import json
import re
import os

class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(open('w3270.html').read())

    def do_POST(self):
        length = int(self.headers.getheader('Content-Length'))
        request = json.loads(self.rfile.read(length))
        terminal = self.server.terminal
        terminal.stdin.write(request['command'])
        data = []
        while True:
            line = terminal.stdout.readline()
            match = re.match(r'data: ?(?P<data>[^\r]*)', line)
            if not match:
                break
            data.append(match.group('data'))
        status = line.rstrip()
        result = terminal.stdout.readline().rstrip()
        response = {}
        response['result'] = result
        response['status'] = status
        response['data'] = data
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response))

class Application:
    def run(self):
        argumentParser = argparse.ArgumentParser(description='s3270 HTTP server')
        argumentParser.add_argument('-i', '--interface', default='localhost', help='server address')
        argumentParser.add_argument('-p', '--port', type=int, default=8080, help='server port')
        arguments, parameters = argumentParser.parse_known_args()
        server = BaseHTTPServer.HTTPServer((arguments.interface, arguments.port), RequestHandler)
        if sys.platform == 'linux2':
            program = 's3270'
        elif sys.platform in ['win32', 'cygwin']:
            program = 'ws3270.exe'
        parameters = ['./' + program, '-utf8', '-xrm', 's3270.m3279: True'] + parameters
        pipe=subprocess.PIPE
        server.terminal = subprocess.Popen(parameters, stdin=pipe, stdout=pipe, stderr=pipe)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.socket.close()

if __name__ == '__main__':
    Application().run()