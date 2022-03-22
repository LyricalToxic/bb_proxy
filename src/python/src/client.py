from core.comunication.client import BBClient
from settings import SECRET_KEY

# BBClient(address, SECRET_KEY).start()
from utils.types_.constans import ADDRESS

# print(BBClient(ADDRESS, SECRET_KEY).ping())
BBClient(ADDRESS, SECRET_KEY).communicate("--t 1")