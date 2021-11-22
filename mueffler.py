#!/usr/bin/python3

import json
import http.server
import subprocess

class MuefflerHandler(http.server.BaseHTTPRequestHandler):
    def echo(**args):
        return args
    
    def mueval(expression):
        assert expression != None

        completed_proc = subprocess.run(
            [ "mueval", "--expression", expression ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT
        )

        return {
            "returncode": completed_proc.returncode,
            "output": completed_proc.stdout.decode('utf-8')
        }

    procedures = {
        'echo': echo,
        'mueval': mueval
    }
    
    # http stuff (ugly)

    def do_POST(self):
        if self.path != '/rpc':
            self.send_error(400, explain = "invalid endpoint (only /rpc is allowed)")
            return
        
        if self.headers.get('content-type') != 'application/json':
            self.send_error(400, explain = 'invalid content type (only application/json is allowed')
            return
        
        try:
            content_length = int(self.headers.get('content-length'))
        except:
            self.send_error(400, explain = "invalid content-length")
            return

        body = json.loads(self.rfile.read(content_length))
        
        if not 'proc' in body or not body['proc'] in self.procedures:
            self.send_error(400, explain = "missing or invalid proc, use {}".format("|".join(self.procedures.keys())))
            return
        
        if not 'args' in body:
            self.send_error(400, explain = "missing args")
            return

        try:
            result = self.procedures[body['proc']](**body['args'])
        except Exception as err:
            self.send_error(500, explain = str(err))
            return

        print(body)
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(result).encode('utf-8'))

if __name__ == '__main__':
    hostname = '0.0.0.0'
    port = 8080

    server = http.server.HTTPServer((hostname, port), MuefflerHandler)
    server.serve_forever()