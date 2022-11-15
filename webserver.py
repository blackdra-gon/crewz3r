# Python 3 server example
from http.server import SimpleHTTPRequestHandler, HTTPServer
import time

hostName = "localhost"
serverPort = 8080

if __name__ == "__main__":
    webServer = HTTPServer((hostName, serverPort), SimpleHTTPRequestHandler)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")