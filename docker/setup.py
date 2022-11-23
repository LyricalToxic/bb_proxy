from plumbum import local
import time
import signal


def on_kill(signum, frame):
    with local.cwd("/home/app/pm2/"):
        pm2 = local["pm2"]
        pm2.run(args=("stop", "all"))


def set_signal_safety(sig, handler):
    try:
        signal.signal(sig, handler)
    except Exception as e:
        pass


signals = [signal.SIGINT, signal.SIGTERM, signal.SIGKILL]
for signal_ in signals:
    set_signal_safety(signal_, on_kill)

print("`setup.py` start")

with local.cwd("/home/app/src/python/src"):
    print(local["poetry"].run(args=("install")))
with local.cwd("/home/app/pm2/"):
    local.cmd.cp("pm2.config.example.js", "pm2.config.js")
    pm2 = local["pm2"]
    pm2.run(args=("-v",))
    pm2.run(args=("start", "pm2.config.js"))
    print(pm2.run(args=("status",)))
print("`setup.py` finished")

while True:
    time.sleep(60 * 60 * 24)
