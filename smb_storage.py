# -*- coding: utf-8 -*-

from smb.SMBConnection import SMBConnection

server_ip = '192.168.3.100'
user = 'raspi'
password = 'raspberry-90'
client_name = 'pi'
server_name = 'h100'
share_name = 'raspi_Home1'

def connect_h100():
    conn = SMBConnection(user, password, client_name, server_name)
    conn.connect(server_ip, timeout=30)

    for s in conn.listShares():
        if s.name == share_name:
            return conn, s
    return conn, None

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
