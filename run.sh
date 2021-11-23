#!/bin/bash
# Docker is unable to run python on its own for some reason
# This scrip is needed to run properly
python3 -u /web3270/server.py --config /config --certs /certs