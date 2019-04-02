# -*- coding: utf-8 -*-

from smb.SMBConnection import SMBConnection
from io import BytesIO

server_ip = '192.168.3.100'
user = 'raspi'
password = 'raspberry-90'
client_name = 'pi'
server_name = 'h100'

if __name__ == '__main__':
    
    try:    
        conn = SMBConnection(user, password, client_name, server_name)
        conn.connect(server_ip, timeout=30)
        share = conn.listShares()[1]
        print(share.name)
        for d in conn.listPath(share.name, '/'):
            print(d.filename)
        #conn.createDirectory(share.name, 'test')
        pos = 0
        for i in range(5):
            stream = BytesIO()
            stream.write(str(i).encode('utf-8')+b'\n')
            stream.seek(0)
            pos = conn.storeFileFromOffset(share.name, 'test/test.txt', stream, pos)
            print(pos)
    except:
        raise
    finally:
        conn.close()

