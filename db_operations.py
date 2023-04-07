import mysql.connector 

class db_operations():

    #constructor with connection path to DB
    def __init__(self):
        # SET THIS PASSWORD BACK TO cpsc408 WHEN YOU'RE DONE
        self.connection = mysql.connector.connect(host="localhost",
            user="root",
            password="Mustang21!",
            auth_plugin='msql_native_password',
            database="RideShare")
        self.cursor = self.connection.cursor()

     # function to return a single value from table
    def single_record(self,query):
        self.cursor.execute(query)
        return self.cursor.fetchone()[0]
    
    # function for bulk inserting records
    def bulk_insert(self,query,records):
        self.cursor.executemany(query,records)
        self.connection.commit()
        print("query executed..")

    # function to return a single attribute values from table
    def single_attribute(self,query):
        self.cursor.execute(query)
        results = self.cursor.fetchall()
        results = [i[0] for i in results]
        #results.remove(None)
        return results
    
    # SELECT with named placeholders
    def name_placeholder_query(self,query,values):
        self.cursor.execute(query,values)
        results = self.cursor.fetchall()
        results = [i for i in results]
        return results

    #destructor that closes connection with DB
    def destructor(self):
        self.connection.close()

    def commit(self):
        self.connection.commit()
