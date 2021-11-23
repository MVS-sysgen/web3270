import tornado.web
from tornado.ioloop import IOLoop
from terminado import TermSocket, TermManagerBase, UniqueTermManager
import os, sys
import signal
import configparser
import argparse
import shutil

class TerminalPageHandler(tornado.web.RequestHandler):
    def initialize(self, width=80,height=45):
        self.width = width
        self.height = height

    def get(self):
        return self.render(
                           "index.html", 
                           width=self.width,
                           height=self.height,
                           ws_url_path="/websocket"
                          )

class Unique3270Manager(TermManagerBase):
    """Give each websocket a unique terminal to use."""

    def __init__(self, max_terminals=None, theight=45,twidth=80, **kwargs):
        super(Unique3270Manager, self).__init__(**kwargs)
        self.max_terminals = max_terminals
        self.height = theight
        self.width = twidth

    def get_terminal(self, url_component=None):
        if self.max_terminals and len(self.ptys_by_fd) >= self.max_terminals:
            raise MaxTerminalsReached(self.max_terminals)

        term = self.new_terminal(height=self.height, width=self.width)
        self.start_reading(term)
        return term

    def client_disconnected(self, websocket):
        """Send terminal SIGHUP when client disconnects."""
        self.log.info("Websocket closed, sending SIGHUP to terminal.")
        if websocket.terminal:
            if os.name == 'nt':
                websocket.terminal.kill()
                # Immediately call the pty reader to process
                # the eof and free up space
                self.pty_read(websocket.terminal.ptyproc.fd)
                return
            websocket.terminal.killpg(signal.SIGHUP)


parser = argparse.ArgumentParser(description='web3270 - Web based front end to c3270')
parser.add_argument('--config',help='web3270 Config folder',default=os.path.dirname(os.path.realpath(__file__)))
parser.add_argument('--certs',help='web3270 TLS Certificates folder',default=os.path.dirname(os.path.realpath(__file__)))
args = parser.parse_args()

if __name__ == '__main__':
    print("[+] Starting Web server")
    # defaults
    height = 45
    width = 80
    c3270 = ['c3270', '-secure', '-defaultfgbg']

    if not os.path.exists("{}/web3270.ini".format(args.config)):
        shutil.copy2("{}/web3270.ini".format(os.path.dirname(os.path.realpath(__file__))), args.config)
   
    print("[+] Using config: {}/web3270.ini".format(args.config))
    config = configparser.ConfigParser()
    config.read("{}/web3270.ini".format(args.config))
    if config['tn3270'].getboolean('selfsignedcert'):
        c3270.append('-noverifycert')

    if config['tn3270'].getboolean('useproxy'):
        c3270.append('-proxy')
        c3270.append(config['proxystring'])
    # build connection string

    c3270.append("-model")
    c3270.append(config['tn3270']['model'])

    if config['tn3270']['model'] == 2:
        height = 24 + 2
    elif config['tn3270']['model'] == 3:
        height = 32 + 2
    elif config['tn3270']['model'] == 4:
        height = 43 + 2
    elif config['tn3270']['model'] == 5:
        height = 27 + 2
        width = 132

    connect_string = ""

    if config['tn3270'].getboolean('encrypted'):
        connect_string = "L:"
    
    connect_string += config['tn3270']['server_ip'] + ":" + config['tn3270']['server_port']

    c3270.append(connect_string)

    #c3270 = ['c3270', '-secure', '-noverifycert','L:192.168.0.102:2323']
    print("[+] c3270 connect string: '{}'".format(' '.join(c3270)))


    term_manager = Unique3270Manager(theight=height,twidth=width,shell_command=c3270)
    handlers = [
                (r"/websocket", TermSocket, {'term_manager': term_manager}),
                (r"/", TerminalPageHandler),
                (r"/(.*)", tornado.web.StaticFileHandler, {'path':'.'}),
               ]
    # (r"/()", tornado.web.StaticFileHandler, {'path':'index.html'}),               
    app = tornado.web.Application(handlers)
    if config['web'].getboolean('tls'):
        csr = "{}/ca.csr".format(args.certs)
        key = "{}/ca.key".format(args.certs)
        if not os.path.exists(csr):
            print("[!] Could not find {} trying local cert ca.csr".format(csr))
            csr = "{}/ca.csr".format(os.path.dirname(os.path.realpath(__file__)))
            if not os.path.exists(csr):
                print("[!] Could not find {}".format(csr))
                sys.exit(-1)
        if not os.path.exists(key):
            print("[!] Could not find {} trying local cert ca.key".format(key))
            key = "{}/ca.key".format(os.path.dirname(os.path.realpath(__file__)))
            if not os.path.exists(key):
                print("[!] Could not find {}".format(key))
                sys.exit(-1)

        print("[+] Using cert files {} and {}".format(csr,key))

        http_server = tornado.httpserver.HTTPServer(app, ssl_options={
            "certfile": csr,
            "keyfile": key,
            })
        http_server.listen(config['web']['webport'])
        print("[+] Secure web server Listening on port {}".format(config['web']['webport']))
    else:
        app.listen(config['web']['webport'])
        print("[+] Web server Listening on port {}".format(config['web']['webport']))
    IOLoop.current().start()