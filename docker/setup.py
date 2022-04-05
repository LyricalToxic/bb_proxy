from plumbum import local

print("`setup.py` start")

with local.cwd("/home/app/src/python/src"):
    print(local["poetry"].run(args=("install")))
with local.cwd("/home/app/pm2/"):
    local.cmd.cp("pm2.config.example.js", "pm2.config.js")
    pm2 = local["pm2"]
    pm2.popen(args=("start", "pm2.config.js"))
    print(pm2.run(args=("status",)))
print("`setup.py` finish")
local["python"].run()
#  python3 /home/app/docker/setup.py
#  curl --location --request GET 'https://ident.me' --header 'Proxy-Authorization1: Basic dGVzdDp0ZXN0MQ==' -x 127.0.0.1:8081 -k