import sqlite3 as sql



class DataBase:
    def __init__(self, database):
        self.db = sql.connect(database)
        self.cursore = self.db.cursor()

    def send_data(self, table, data):
        request = f"INSERT INTO {table} VALUES {data}"
        self.cursore.execute(request)
        self.db.commit()

    def get_data(self, table, data, condition=""):
        request = f"SELECT {data} FROM {table} {condition}"
        self.cursore.execute(request)
        answer = self.cursore.fetchall()
        return answer

    def update_data(self, table, column, new_data, condition):
        request = f"UPDATE {table} SET {column}='{new_data}' {condition}"
        self.cursore.execute(request)
        self.db.commit()

    def delete_data(self, table, condition):
        request = f"DELETE FROM {table} {condition}"
        self.cursore.execute(request)
        self.db.commit()