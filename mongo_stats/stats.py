from pymongo import MongoClient


class Stats:
    def __init__(self, connection_string, scale=1024 * 1024):
        self.db_client = MongoClient(connection_string, connect=True)
        self.db = self.db_client["admin"]

        self.scale = scale

    def get_db_client(self):
        return self.db_client

    def get_scale(self):
        return self.scale

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
            db_stat = database.command("dbStats", scale=self.scale)

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

    def collection_stats(self, databases):
        result = {}
        for database in databases:
            if database == "admin":
                continue
            db = self.db_client[database]

            result[database] = []

            collections = db.collection_names()
            for collection in collections:
                collstats = db.command("collstats", collection, scale=self.scale)

                result[database].append({
                    "name": collection,
                    "ns": collstats["ns"],
                    "count": collstats["count"],
                    "avgObjSize": collstats.get("avgObjSize"),
                    "storageSize": collstats["storageSize"]
                })

        return result
