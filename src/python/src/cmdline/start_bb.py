from core.bb_innards.big_brother import BigBrother
from core.bb_innards.storage.bb_storage import BBStorage
from core.bb_innards.storage.bb_storage_keeper import BBStorageKeeper
from settings import DB_DRIVER
from utils.project.func.dbca import get_dbca


async def _run(options):
    bb_storage = BBStorage()
    dbca = get_dbca(DB_DRIVER)
    bbc = BigBrother(storage_keeper=BBStorageKeeper(bb_storage), dbca=dbca)
    await bbc.run(options)
