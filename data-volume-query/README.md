# Data Volume Report Generator

This script generates a CSV report summarizing the data volume and characteristics of tables within a specified Oracle database schema. It provides insights into table sizes, record counts, column counts, and date ranges, which can be useful for database administration, capacity planning, and data analysis.

## What it Does

The script connects to an Oracle database, queries metadata about tables in a given schema, and calculates the following for each table:

*   **TABLE_NAME:** The name of the table.
*   **COLUMN_COUNT:** The number of columns in the table.
*   **RECORD_COUNT:** The number of rows (records) in the table.  (Uses `ALL_TABLES.NUM_ROWS`, which is based on statistics, so may not be 100% accurate if statistics are stale).
*   **DATA_POINTS_TOTAL:**  `COLUMN_COUNT` * `RECORD_COUNT`, representing the total number of data points in the table.
*   **STORAGE_SIZE_MB:** The approximate storage size of the table in megabytes (calculated using `AVG_ROW_LEN` and `NUM_ROWS`).
*   **min_datetime:** The earliest `create_datetime` value found in the table (if a `create_datetime` column exists).
*   **max_datetime:** The latest `create_datetime` value found in the table (if a `create_datetime` column exists).

The results are saved to a CSV file named `DataVolumeReport_[schema_name].csv`, where `[schema_name]` is replaced with the schema you provided.

## Prerequisites

Before running the script, you'll need the following:

1.  **Python:**  Make sure you have Python 3 installed (preferably 3.6 or later).
2.  **Create the environment:** Navigate to the `data-volume-query` directory in your terminal:

        ``` 
        cd MOTT-DataServices-monorepo/data-volume-query
        ```

        Then, create a virtual environment (you can name it anything; `.venv` is a common convention):

        ```
        python -m venv .venv
        ```

    *   **Activate the environment:**

        *   **On Windows (Command Prompt):**

            ```
            .venv\Scripts\activate.bat
            ```

        *   **On Windows (PowerShell):**

            ```
            .venv\Scripts\Activate.ps1
            ```

        You should see `(.venv)` (or your environment name) at the beginning of your command prompt, indicating that the virtual environment is active.
3.  **Dependencies:** Install the required Python packages using pip and the provided `requirements.txt` file.  Navigate to the `data-volume-query` directory and run:

    ```
    pip install -r requirements.txt
    ```
    This will install `cx_Oracle`, `pandas` and `tqdm`.
4.  **Oracle Client Libraries:** You'll need the Oracle Instant Client (or a full Oracle client installation) to connect to the database.  This is *separate* from `cx_Oracle`.  You can download it from the Oracle website:
    [https://www.oracle.com/database/technologies/instant-client/downloads.html](https://www.oracle.com/database/technologies/instant-client/downloads.html)
    Make sure you install the correct version of oracle client that is compatible with your Oracle Server. You also need to configure environment variables so that python knows where to find your Oracle client libraries.
5.  **Database Credentials:** You'll need a valid username, password, and connection details (host, port, service name) for the Oracle database you want to analyze.

## How to Run

1.  **Navigate to the Script Directory:** Open a terminal or command prompt and navigate to the `data-volume-query/src` directory within the monorepo:

    ```
    cd MOTT-DataServices-monorepo/data-volume-query/src
    ```

2.  **Execute the Script:** Run the script using:

    ```
    python main.py
    ```
4.  **Provide Input:** The script will prompt you for the following information:
    *   **username:** Your Oracle database username.
    *   **password:** Your Oracle database password.
    *   **host:** The hostname or IP address of the database server.
    *   **port:** The port number the database is listening on (usually 1521).
    *   **service:**  The Oracle service name (e.g., `PRD11`, `XE`, etc.).
    *   **schema:** The name of the database schema you want to analyze (e.g., `APP_CPS`).
5.   **Check the Output** After execution the csv with results will be saved in the same directory you ran the script from.

## Important Notes

*   **`create_datetime` Column:** The script attempts to find the minimum and maximum `create_datetime` values *if* a column named `create_datetime` exists in the table.  If this column doesn't exist or has a different name, the `min_datetime` and `max_datetime` columns in the report will be `None`.  The script does *not* automatically detect other date/time columns.
*   **Statistics:** The `RECORD_COUNT` and `STORAGE_SIZE_MB` values are based on database statistics. If the statistics are outdated, these values might not be perfectly accurate.  You may want to gather statistics on the schema before running the script for the most precise results.
*   **Error Handling:** The script includes basic error handling for cases where it cannot determine the min/max `create_datetime`.  More comprehensive error handling (e.g., for connection failures) could be added.
* **Permissions** The database user you connect with needs to have `SELECT` privileges on the `ALL_TAB_COLUMNS` and `ALL_TABLES` views, as well as on the tables within the target schema.
*   **Large Schemas:** For very large schemas (thousands of tables), the script might take a considerable amount of time to run.  The `tqdm` library provides a progress bar to show the progress of the date range query.

## Example Output (CSV)

```csv
TABLE_NAME,COLUMN_COUNT,RECORD_COUNT,DATA_POINTS_TOTAL,STORAGE_SIZE_MB,min_datetime,max_datetime
EMPLOYEES,11,107,1177,0.018310546875,2023-01-15 08:00:00,2024-01-20 17:30:00
DEPARTMENTS,4,27,108,0.00244140625,None,None
PRODUCTS,9,1000,9000,0.457763671875,2022-05-01 00:00:00,2024-02-28 23:59:59
SALES,7,50000,350000,12.5,2023-10-01 00:00:00,2024-02-29 12:00:00
