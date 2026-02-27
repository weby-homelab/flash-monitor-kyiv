import re
with open('/root/geminicli/flash-monitor-kyiv/docker-compose.yml', 'r') as f:
    text = f.read()

new_text = re.sub(r'image: webyhomelab/flash-monitor-kyiv:v[0-9.]+', 'image: webyhomelab/flash-monitor-kyiv:v1.9.4', text)

with open('/root/geminicli/flash-monitor-kyiv/docker-compose.yml', 'w') as f:
    f.write(new_text)
