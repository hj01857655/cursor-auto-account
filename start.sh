#!/bin/bash

# Start socat in the background to forward port 9223 to 9222
socat TCP-LISTEN:9223,fork TCP:127.0.0.1:9222 &

# Start the Python application
python app.py
