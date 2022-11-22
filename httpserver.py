from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import os

address = "0.0.0.0"
serverPort = 8080


class RequestHandler(BaseHTTPRequestHandler):
    def render(self, filename):
        try:
            dir_path = os.path.dirname(os.path.realpath(__file__))
            fin = open('%s/web/views/%s.html' % (dir_path, filename))
            contents = fin.read()
            fin.close()

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(contents, "utf-8"))
        except FileNotFoundError as e:
            self.render("404")
        except Exception as e:
            self.render("500")

    def do_GET(self):
        if (self.path == "/"):
            self.render("index")
        elif (self.path == "/preview"):
            self.render("preview")
        elif (self.path.startswith("/api/")):
            self.handleAPIRequest()
        else:
            self.render("404")

    def handleAPIRequest(self):
        (_, api, endpoint, type) = self.path.split("/")
        if self.path == '/api/control/disable':
            self.server.led_system.setStripEnabled(False)
            self.apiResponse(200, {"enabled": False})
        elif self.path == '/api/control/enable':
            self.server.led_system.setStripEnabled(True)
            self.apiResponse(200, {"enabled": True})
        elif (endpoint == 'components'):
            self.handleComponentRequest(type)
        elif (endpoint == 'presets'):
            self.handlePresetRequest(type)
        else:
            self.apiResponse(404, {"error": "endpoint not found"})

    def apiResponse(self, response_code, data: dict):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps(data), "utf-8"))

    def handleComponentRequest(self, animationType):
        if (self.path == '/api/components/'):
            self.apiResponse(200, {
                "components": list(map(lambda c: c.toJSON(), self.server.led_system.components))
            })

    def handlePresetRequest(self, preset):
        if preset == None:
            self.apiResponse(200, {
                "presets": ["TODO"]
            })
        else:
            self.server.led_system.usePreset(preset)
            self.apiResponse(200, {"status": "ok"})


class HTTPServerWrapper:
    internalServer = None

    def start(self, led_system):
        self.internalServer = HTTPServer((address, serverPort), RequestHandler)
        print("Webserver started http://%s:%s" % (address, serverPort))
        self.internalServer.led_system = led_system

        try:
            self.internalServer.serve_forever()
        except KeyboardInterrupt:
            pass

        self.internalServer.server_close()
        print("Server stopped.")
