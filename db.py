import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="127.0.0.1",   # or "localhost"
        user="root",        # your MySQL username
        password="SetyourPassword", # your MySQL password
        database="company_db"  # your database name
    )

def run_query(sql: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    
    columns = [desc[0] for desc in cursor.description]
    conn.close()
    return rows, columns

def get_schema_info():
    """Fetch tables and columns from the current database."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES;")
    tables = cursor.fetchall()

    schema = {}
    for (table_name,) in tables:
        cursor.execute(f"DESCRIBE {table_name};")
        columns = [col[0] for col in cursor.fetchall()]
        schema[table_name] = columns

    conn.close()
    return schema