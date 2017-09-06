import time
import curses

from pymongo import MongoClient

from mongo_stats.utils import json_format
from mongo_stats.collection import collection_stats

db_client = MongoClient("mongodb://localhost:27017/admin", connect=True)
db = db_client['admin']


def number_of_connections():
    server_status = db.command("serverStatus")

    return server_status["connections"]


def get_current_operation():
    return db.current_op()


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


def sleep(secs, stdscr):
    """
    Sleep for a long time will freeze the screen for the user.
    Pressing a `q` button won't get processed until the sleep
    time is over.

    This custom sleep, sleeps over steps of `freq` values, so that
    we can response to `q` faster.
    """
    freq = 0.1

    while True:
        time.sleep(freq)
        secs -= freq

        char = stdscr.getch()
        if char == 113:
            exit(0)

        if secs <= 0:
            return


def start(stdscr):
    curses.start_color()
    curses.use_default_colors()
    stdscr.nodelay(1)

    while True:
        char = stdscr.getch()
        if char == 113:
            break

        curses.init_pair(1, curses.COLOR_GREEN, -1)

        # Number of connections
        connections = number_of_connections()
        stdscr.addstr(0, 0, "Connections:", curses.color_pair(1))
        stdscr.addstr(1, 3, "Current: {}".format(connections["current"]))
        stdscr.addstr(2, 3, "Available: {}".format(connections["available"]))
        stdscr.addstr(3, 3, "Total Created: {}".format(connections["totalCreated"]))

        # Current operation
        current_operation_count = len(get_current_operation()['inprog'])
        stdscr.addstr(5, 0, "Current operation:", curses.color_pair(1))
        stdscr.addstr(6, 3, "Operations: {}".format(current_operation_count))

        # List all databases
        databases = list_all_databases()
        stdscr.addstr(8, 0, "Databases:", curses.color_pair(1))

        cursor_pos_col = 3
        stdscr.addstr(9, 3, "name")

        cursor_pos_col += len("name") + 2
        stdscr.addstr(9, cursor_pos_col, "dataSize")

        cursor_pos_col += len("dataSize") + 2
        stdscr.addstr(9, cursor_pos_col, "indexes")

        cursor_pos_col += len("indexes") + 2
        stdscr.addstr(9, cursor_pos_col, "indexSize")

        cursor_pos_col += len("indexSize") + 2
        stdscr.addstr(9, cursor_pos_col, "collections")

        cursor_pos_row = 11
        for database in databases:
            database_name = database['name']
            database_size = database['dataSize']
            database_indexes = database['indexes']
            database_index_size = database['indexSize']
            database_collections = database['collections']

            cursor_pos_col = 3
            stdscr.addstr(cursor_pos_row, cursor_pos_col, database_name)

            cursor_pos_col += len(database_name) + 2
            stdscr.addstr(cursor_pos_row, cursor_pos_col, str(database_size))

            cursor_pos_col += len(str(database_size)) + 2
            stdscr.addstr(cursor_pos_row, cursor_pos_col, str(database_indexes))

            cursor_pos_col += len(str(database_indexes)) + 2
            stdscr.addstr(cursor_pos_row, cursor_pos_col, str(database_index_size))

            cursor_pos_col += len(str(database_index_size)) + 2
            stdscr.addstr(cursor_pos_row, cursor_pos_col, str(database_collections))

            cursor_pos_row += 1

        cursor_pos_row += 1

        # Collection
        dbs = [database["name"] for database in databases]
        stdscr.addstr(cursor_pos_row, 0, "Collection:", curses.color_pair(1))
        db_collections = collection_stats(db_client, dbs)

        cursor_pos_row += 1
        for collections in db_collections:
            stdscr.addstr(cursor_pos_row, 3, collections)
            cursor_pos_row += 1
            for collection in db_collections[collections]:
                collection_name = collection["name"]
                collection_count = collection["count"]

                # 3 after the starting 3 column index.
                cursor_pos_col = 6
                stdscr.addstr(cursor_pos_row, cursor_pos_col, collection_name + ":")

                cursor_pos_col += len(collection_name) + 2
                stdscr.addstr(cursor_pos_row, cursor_pos_col, str(collection_count))

                cursor_pos_row += 1

        stdscr.refresh()
        sleep(5, stdscr)

curses.wrapper(start)
