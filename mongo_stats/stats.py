import curses

import click
from pymongo import MongoClient

from mongo_stats.screen import Screen
from mongo_stats.utils import screen_col
from mongo_stats.collection import collection_stats


class Stats:
    def __init__(self, connection_string):
        self.db_client = MongoClient(connection_string, connect=True)
        self.db = self.db_client["admin"]

    def get_db_client(self):
        return self.db_client

    def number_of_connections(self):
        server_status = self.db.command("serverStatus")

        return server_status["connections"]


    def get_current_operations(self):
        current_operation = self.db.current_op()
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


    def current_operation_waiting_for_lock(self):
        return self.db.current_op({
            "waitingForLock": True,
            "$or": [
                {"op": {"$in": ["insert", "update", "remove"]}},
                {"query.findandmodify": { "$exists": True}}
            ]
        })


    def list_all_databases(self):
        """
        {
          "name": "admin",
          "dataSize": 167936.0,
          "empty": false
        }
        """
        databases = [database["name"] for database in self.db.command("listDatabases")['databases']]

        result = []
        for database in databases:
            database = self.db_client[database]
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


def render(stdscr):
    screen = Screen(stdscr)

    while True:
        screen.clear()
        if not screen.start():
            break

        stats = Stats(uri)
        # Number of connections
        connections = stats.number_of_connections()
        screen.print("Connections:", "heading")
        screen.print("Current: {}".format(connections["current"]))
        screen.print("Available: {}".format(connections["available"]))
        screen.print("Total Created: {}".format(connections["totalCreated"]))

        # Current operation
        current_operations = stats.get_current_operations()
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
        databases = stats.list_all_databases()
        screen.print("Databases:", "heading")
        database_rows = []
        for database in databases:
            database_rows.append({
                "name": database['name'],
                "dataSize": str(database['dataSize']),
                "indexes": str(database['indexes']),
                "indexSize": str(database['indexSize']),
                "collections": str(database['collections'])
            })

        headings = ["name", "dataSize", "indexes", "indexSize", "collections"]
        with screen_col(screen, 3):
            screen.print_table(headings, database_rows)

        # Collection
        dbs = [database["name"] for database in databases]
        db_collections = collection_stats(stats.get_db_client(), dbs)
        screen.print("Collections:", "heading")

        for collections in db_collections:
            screen.print(collections)

            headings = ["collection", "document_count"]
            rows = []
            for collection in db_collections[collections]:
                row = {
                    "collection": collection['name'],
                    "document_count": str(collection['count'])
                }
                rows.append(row)

            with screen_col(screen, 6):
                screen.print_table(headings, rows)

        screen.sleep(5, stdscr)


@click.command()
@click.option("--connection-string", help="Provide a mongodb connection string.")
def start(connection_string):
    if not connection_string:
        print("Please provide a mongodb connection string")
        exit(1)
    global uri
    uri = connection_string
    curses.wrapper(render)
