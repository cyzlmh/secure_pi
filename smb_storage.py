# -*- coding: utf-8 -*-

from smb.SMBConnection import SMBConnection
from datetime import datetime, timedelta
from time import sleep

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

def dir_manage(conn, share):
    # create today's dir if not exists
    current = datetime.now()
    try:
        conn.createDirectory(share.name, current.strftime('%Y%m%d'))
    except:
        pass

    # clear deprecated dir
    deprecated = current - timedelta(14)
    dirs = [d.filename for d in conn.listPath(share.name, '/') if not d.filename.startswith('.')]
    try:
        for d_name in dirs:
            if datetime.strptime(d_name, '%Y%m%d') < deprecated:
                for f in conn.listPath(share.name, d_name):
                    if not f.filename.startswith('.'):
                        conn.deleteFiles(share.name, d_name+'/'+f.filename)
                conn.deleteDirectory(share.name, d_name)
    except:
        pass

    nextday = current + timedelta(1)
    nextday = nextday.replace(hour=0, minute=0, second=0)
    sec_to_nextday = (nextday - current).seconds
    return sec_to_nextday

if __name__ == '__main__':

    try:
        while True:
            conn, share = connect_h100()
            to_sleep = dir_manage(conn, share)
            conn.close()
            sleep(to_sleep)
        
    except:
        raise
    finally:
        conn.close()
