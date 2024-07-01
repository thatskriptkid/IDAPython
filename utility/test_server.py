

from http.server import HTTPServer, BaseHTTPRequestHandler

class Serv(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "gzip")
        self.end_headers()
        self.wfile.write(bytes("base64str", 'utf-8'))

httpd = HTTPServer(('localhost',80),Serv)
httpd.serve_forever()