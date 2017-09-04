from pymongo import MongoClient

from mongo_stats.utils import json_format
from mongo_stats.collection import collection_stats

db_client = MongoClient("mongodb://localhost:27017/admin", connect=True)
db = db_client['admin']


@json_format()
def number_of_connections():
    server_status = db.command("serverStatus")

    return server_status["connections"]


@json_format()
def current_operation():
    return db.current_op()


@json_format()
def current_operation_waiting_for_lock():
    return db.current_op({
        "waitingForLock": True,
        "$or": [
            {"op": {"$in": ["insert", "update", "remove"]}},
            {"query.findandmodify": { "$exists": True}}
        ]
    })


@json_format()
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


def start():
    print("#### No of connections ####")
    print(number_of_connections(), end="\n\n")

    print("#### Current operation ####")
    print(current_operation(), end="\n\n")

    print("#### Current operation waiting for lock ####")
    print(current_operation_waiting_for_lock(), end="\n\n")

    print("#### Collection stats ####")
    dbs =  [database["name"] for database in db.command("listDatabases")['databases']]
    print(collection_stats(db_client, dbs), end="\n\n")

    print("### List all databases ###")
    print(list_all_databases())

start()