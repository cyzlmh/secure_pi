import os
from datetime import datetime, timedelta

email_freq = 30*60
to = 'anto_nozomi@126.com'

def send_email(storage_path):
    with open('last_send', 'r') as f:
        last_send = f.read()
    last_send = datetime.strptime(last_send, '%Y%m%d-%H:%M:%S')
    
    if last_send - datetime.now() > timedelta(email_freq):
        ts = datetime.now().strftime('%Y%m%d-%H:%M:%S')
        title = ts + '-motion-detect'
        content = 'null'
        attachment = os.path.join(storage_path, ts+'.jpg')
        os.system('python3 /home/pi/scripts/send_email.py {} {} {} {}'\
            .format(to, title, content, attachment))
        with open('last_send', 'w') as f:
            f.write(ts)
        