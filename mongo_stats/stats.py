import curses

from pymongo import MongoClient

from mongo_stats.screen import Screen
from mongo_stats.collection import collection_stats

db_client = MongoClient("mongodb://localhost:27017/admin", connect=True)
db = db_client['admin']


def number_of_connections():
    server_status = db.command("serverStatus")

    return server_status["connections"]


def get_current_operations():
    current_operation = db.current_op()
    current_operations = current_operation['inprog']
    current_operation_count = len(current_operations)

    operations = []
    for current_operation in current_operations:
        operations.append({
            "opid": current_operation['opid'],
            "secs_running": current_operation['secs_running'],
            "waitingForLock": current_operation['waitingForLock']
        })

    return {
        "count": current_operation_count,
        "operations": operations
    }


def current_operation_waiting_for_lock():
    return db.current_op({
        "waitingForLock": True,
        "$or": [
            {"op": {"$in": ["insert", "update", "remove"]}},
            {"query.findandmodify": { "$exists": True}}
        ]
    })


def list_all_databases():
    """
    {
      "name": "admin",
      "dataSize": 167936.0,
      "empty": false
    }
    """
    databases = [database["name"] for database in db.command("listDatabases")['databases']]

    result = []
    for database in databases:
        database = db_client[database]
        db_stat = database.command("dbStats", scale=1024 * 1024)

        result.append({
            "name": db_stat["db"],
            "avgObjSize": db_stat["avgObjSize"],
            "dataSize": db_stat["dataSize"],
            "indexes": db_stat["indexes"],
            "indexSize": db_stat["indexSize"],
            "storageSize": db_stat["storageSize"],
            "collections": db_stat["collections"]
        })

    return result


def start(stdscr):
    screen = Screen(stdscr)

    while True:
        screen.clear()
        if not screen.start():
            break

        # Number of connections
        connections = number_of_connections()
        screen.print("Connections:", "heading")
        screen.print("Current: {}".format(connections["current"]))
        screen.print("Available: {}".format(connections["available"]))
        screen.print("Total Created: {}".format(connections["totalCreated"]))

        # Current operation
        current_operations = get_current_operations()
        screen.print("Current operation:", "heading")
        screen.print("Count: {}".format(current_operations['count']))

        operations = current_operations['operations']
        for operation in operations:
            op_id = operation['opid']
            secs_running = operation['secs_running']
            waiting_for_lock = operation['waitingForLock']
            screen.print("Op id: {}".format(op_id), same_row=True)
            screen.print("Secs running: {}".format(secs_running), same_row=True)
            screen.print("Waiting for lock: {}".format(waiting_for_lock), same_row=True)
            screen.print("")

        # List all databases
        databases = list_all_databases()
        screen.print("Databases:", "heading")
        for database in databases:
            database_name = database['name']
            database_size = database['dataSize']
            database_indexes = database['indexes']
            database_index_size = database['indexSize']
            database_collections = database['collections']

            screen.print(database_name, same_row=True)
            screen.print(str(database_size), same_row=True)
            screen.print(str(database_indexes), same_row=True)
            screen.print(str(database_index_size), same_row=True)
            screen.print(str(database_collections), same_row=True)
            screen.print("")

        # Collection
        dbs = [database["name"] for database in databases]
        db_collections = collection_stats(db_client, dbs)
        screen.print("Collections:", "heading")

        for collections in db_collections:
            screen.print(collections)
            for collection in db_collections[collections]:
                collection_name = collection['name']
                collection_count = collection['count']

                screen.print("{}: {}".format(collection_name, str(collection_count)), same_row=True)
                screen.print("")

        screen.sleep(5, stdscr)

curses.wrapper(start)
