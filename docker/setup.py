from plumbum import local
import time
print("`setup.py` start")

with local.cwd("/home/app/src/python/src"):
    print(local["poetry"].run(args=("install")))
with local.cwd("/home/app/pm2/"):
    local.cmd.cp("pm2.config.example.js", "pm2.config.js")
    pm2 = local["pm2"]
    pm2.popen(args=("start", "pm2.config.js"))
    print(pm2.run(args=("status",)))
print("`setup.py` finish")

while True:
    time.sleep(60 * 60 * 24)