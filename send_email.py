import os
from datetime import datetime, timedelta

def send_email(file_path=None):
    email_freq = 30*60
    with open('last_send', 'r') as f:
        last_send = f.read().strip()
    last_send = datetime.strptime(last_send, '%Y%m%d-%H%M%S')

    if datetime.now()-last_send > timedelta(0, email_freq):
        print('here')
        ts = datetime.now().strftime('%Y%m%d-%H%M%S')
        to = 'anto_nozomi@126.com'
        title = ts + '-motion-detect'
        content = 'null'
        attachment = file_path
        os.system('python3 /home/pi/scripts/send_email.py {} {} {} {}'\
            .format(to, title, content, attachment))
        with open('last_send', 'w') as f:
            f.write(ts)
        print('email sent')
