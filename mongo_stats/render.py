import curses

import click
from pymongo import MongoClient

from mongo_stats.stats import Stats
from mongo_stats.screen import Screen
from mongo_stats.utils import screen_col


def render(stdscr):
    screen = Screen(stdscr, col=2)

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
        db_collections = stats.collection_stats(dbs)
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


def uri_valid():
    try:
        client = MongoClient(uri, connect=True, serverSelectionTimeoutMS=200)
        client.server_info()
    except:
        return False
    return True


@click.command()
@click.option("--connection-string", help="Provide a mongodb connection string.")
def start(connection_string):
    if not connection_string:
        print("Please provide a mongodb connection string")
        exit(1)

    global uri
    uri = connection_string

    if not uri_valid():
        print("Unable to connect. Please check your connection string.")
        exit(1)
    curses.wrapper(render)
