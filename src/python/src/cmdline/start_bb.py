from core.bb.big_brother import BigBrother
from core.bb.data_access.stmt_collections.basic_interaction_stmt_collection import BasicInteractionStmtCollection
from core.bb.storage.bb_storage import BBStorage
from core.bb.storage.bb_storage_keeper import BBStorageKeeper


async def _run(options):
    bb_storage = BBStorage()
    bb_stmt_collection = BasicInteractionStmtCollection()
    bbc = BigBrother(storage_keeper=BBStorageKeeper(bb_storage), stmt_collection=bb_stmt_collection)
    await bbc.run(options)
