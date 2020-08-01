# Introduction
WarThunder virtual panel for fighting.

## Prerequirements

Strongly recommend [Anaconda](https://www.anaconda.com/) on Windows

[vjoy](http://vjoystick.sourceforge.net/) is required for external trim for some German fighters.

```bash
pip install pymavlink
pip install tornado
pip install websockets
pip install pynput
pip install pyserial
```

## Usage
On PC running WarThunder

```bash
python3 wt_server.py
```

On your mobile device or other screen open http://pc-ip-address:8888/index.html or http://127.0.0.1:8888/index.html on your local screen
