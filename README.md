# web3270

A web based front end for c3270. Uses Xterm.js and terminado.

## How to Use

1) First install `c3270` (on Debian based systems you can install with `sudo apt install c3270`)
2) Install the required packages: `pip install -r requirements.txt`
3) Edit the config file `web3270.ini` customized to your system (see below)
4) Place your certifcate crt/key file in this folder (or any folder see arguments below)
4) Start the server: `python3 server.py`


## Config File

The config file allows you to specify multiple options:

* `server_ip` IP address of the tnN3270 server to connect to
* `server_port` TCP port of the tn3270 server to connect to
* `webport` TCP port for this webserver
* `tls` **yes**/**no** should this server use HTTPS. If yes this script will check in the folder denoted by the script argument `--certs`, the default is the folder used the run the script.
* `encrypted` **yes**/**no** when connecting to tn3270 use SSL or not
* `selfsignedcert` **yes**/**no** allow self signed certs when connecting to encrypted tn3270 server
* `model` tn3270 model type (2 through 5), default 4. See https://x3270.miraheze.org/wiki/3270_models for more details.
* `useproxy` **yes**/**no** should a proxy be used to connect to tn3270 server
* `proxystring` The proxy connection string *optional*.
* `password` If set a login page will be displayed and the password set here will be required to load web3270 *optional*
* `secret` The secret used to generate secure tokens. If not set the script will set a random one for you *optional*

## Script Arguments

* `--config` the folder where `web3270.ini` resides. If this file does not exist in the folder provided a default config will be created.
* `--certs` the folder where the web server TLS certificates reside. Files required are `ca.csr` and `ca.key`, use the commad below to generate self signed certs:

```bash
openssl req -x509 -nodes -days 365 \
    -subj  "/C=CA/ST=QC/O=web3270 Inc/CN=3270.web" \
    -newkey rsa:2048 -keyout ca.key \
    -out ca.csr
```


## Docker

To build a docker container use: `docker build --tag "mainframed767/web3270:latest" .`

To run the container:

```bash
docker run -d \
  --name=web3270 \
  -p 4443:443 \
  -v /opt/docker/web3270:/config \
  -v /opt/docker/web3270/certs:/certs \
  --restart unless-stopped \
  mainframed767/web3270
```
This command will run web3270 on port 4443.

After the first run the config file `web3270.ini` will be placed in `/opt/docker/web3270`. Edit that file to fit your environment then restart the container.

## Known Bugs

* Changing the font only shows the current row. Resizing the browser window fixes this.