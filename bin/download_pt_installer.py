"""Download Pythonista Tools Installer script to working directory.
https://github.com/ywangd/pythonista-tools-installer/
"""

import requests as r
o = open('ptinstaller.py', 'w')
o.write(r.get('http://j.mp/pt-i').text)
o.close()