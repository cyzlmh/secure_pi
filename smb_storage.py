# -*- coding: utf-8 -*-

from smb.SMBConnection import SMBConnection

server_ip = '192.168.3.100'
user = 'raspi'
password = 'raspberry-90'
client_name = 'pi'
server_name = 'h100'
share_name = 'raspi_Home1'

class H100Connection(SMBConnection):
    
    def __init__(self):
        super().__init__(self, user, password, client_name, server_name)

    def connect(self):
        super().connect(server_ip, timeout=30)

    def get_share(self, name=share_name):
        for s in self.listShares():
            if s.name == name:
                return s
        return None

if __name__ == '__main__':
    
    try:    
        conn = SMBConnection(user, password, client_name, server_name)
        conn.connect(server_ip, timeout=30)
        share = conn.listShares()[1]
        print(share.name)
        for d in conn.listPath(share.name, '/'):
            print(d.filename)
    except:
        raise
    finally:
        conn.close()
