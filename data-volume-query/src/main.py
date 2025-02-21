import getpass
import pandas as pd
import cx_Oracle
from tqdm.auto import tqdm


def get_oracle_summary_data(conn: cx_Oracle.Connection, schema_name: str = "APP_CPS"):
    """
    :param conn: cx_Oracle.Connection -> An open connection to an oracle database as created by cx_Oracle.
    :param schema_name: str -> The name of the schema which needs the Data Volume Summary to be generated.
    :return: None -> This function does not return anything as it creates an output file.
    """
    data = []
    with conn.cursor() as cursor:
        for row in cursor.execute(f'''
        SELECT
        C.TABLE_NAME AS TABLE_NAME,
        COUNT(UNIQUE(C.COLUMN_NAME)) AS COLUMN_COUNT,
        T.NUM_ROWS AS RECORD_COUNT,
        COUNT(UNIQUE(C.COLUMN_NAME)) * T.NUM_ROWS AS DATA_POINTS_TOTAL,
        ((T.NUM_ROWS * T.AVG_ROW_LEN)/(1024*1024)) AS STORAGE_SIZE_MB
        FROM ALL_TAB_COLUMNS C
        JOIN ALL_TABLES T
        ON C.TABLE_NAME = T.TABLE_NAME
        WHERE C.OWNER = '{schema_name}' AND T.OWNER = '{schema_name}'
        GROUP BY C.TABLE_NAME, T.NUM_ROWS,T.BLOCKS, T.AVG_ROW_LEN
        ORDER BY storage_size_mb DESC
        '''):

            data.append({
                'TABLE_NAME': row[0],
                'COLUMN_COUNT': row[1],
                'RECORD_COUNT': row[2],
                'DATA_POINTS_TOTAL': row[3],
                'STORAGE_SIZE_MB': row[4],
            })

        for row in tqdm(range(len(data))):
            try:
                cursor.execute(f"SELECT min(create_datetime), max(create_datetime) FROM {schema_name}.{data[row]['TABLE_NAME']}")
                results = cursor.fetchone()
                data[row]["min_datetime"] = results[0]
                data[row]["max_datetime"] = results[1]

            except cx_Oracle.DatabaseError as e:
                print(e)
                data[row]["min_datetime"] = None
                data[row]["max_datetime"] = None
                continue

        df = pd.DataFrame(data)
        df.to_csv(f'DataVolumeReport_{schema_name}.csv', index=False)
    pass

if __name__ == '__main__':
    # This block gets input from the user. Probably refactoring this to leverage a .env file would be
    # a better way to go about it. But, I didn't want to add too many layers of complexity.
    user_name = input("Please enter your username: ")
    password = getpass.getpass(prompt="Please enter your password: " )
    host = input("Please enter the host uri for the database: ")
    port = input("Please enter the port number the server is listening on: ")
    service = input("Please enter the name of the service (eg. PRD11): ")
    schema = input("Please enter the schema name: ")

    # Creates a formatted string which cx_Oracle connect will recognise as a connection string.
    dsn = cx_Oracle.makedsn(host, port, service)
    # Creates a connection object to the database using the connection string, username and password provided by the user
    with cx_Oracle.connect(user_name, password, dsn) as connection:
        # Calls the oracle related summary function.
        get_oracle_summary_data(connection, schema)


