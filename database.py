import os
import mysql.connector
from mysql.connector import Error
import streamlit as st

# Database configuration with your credentials
DB_CONFIG = {
    'host': '172.16.128.79',     # IP Address
    'port': 3308,                 # Port
    'database': 'volare',  # You need to specify the database name
    'user': 'usr4mis',           # Username
    'password': 'usr4MIS#@!',    # Password
}

def get_db_connection():
    """Create and return database connection with session settings"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        
        # Set session group_concat limit
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SET SESSION group_concat_max_len = 20000")
            cursor.close()
        
        return connection
    except Error as e:
        st.error(f"Database connection error: {e}")
        return None

def execute_query(sql_query, params=None):
    """
    Execute SQL query and return results as list of dictionaries
    
    Args:
        sql_query (str): SQL query to execute
        params (dict, optional): Parameters for parameterized query
    
    Returns:
        list: List of dictionaries containing query results
    """
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Set session group_concat limit again to be safe
            cursor.execute("SET SESSION group_concat_max_len = 20000")
            
            # Execute query with or without parameters
            if params:
                cursor.execute(sql_query, params)
            else:
                cursor.execute(sql_query)
                
            results = cursor.fetchall()
            cursor.close()
            connection.close()
            return results
        except Error as e:
            st.error(f"Query execution error: {e}")
            st.error(f"Failed query: {sql_query}")
            return []
    return []

def execute_non_query(sql_query, params=None):
    """
    Execute non-query SQL (INSERT, UPDATE, DELETE) and commit changes
    
    Args:
        sql_query (str): SQL query to execute
        params (dict, optional): Parameters for parameterized query
    
    Returns:
        bool: True if successful, False otherwise
    """
    connection = get_db_connection()
    if connection:
        try:
            cursor = connection.cursor()
            
            # Set session group_concat limit
            cursor.execute("SET SESSION group_concat_max_len = 20000")
            
            # Execute query with or without parameters
            if params:
                cursor.execute(sql_query, params)
            else:
                cursor.execute(sql_query)
                
            connection.commit()
            cursor.close()
            connection.close()
            return True
        except Error as e:
            st.error(f"Query execution error: {e}")
            if connection:
                connection.rollback()
            return False
    return False

def test_connection():
    """Test database connection"""
    connection = get_db_connection()
    if connection:
        st.success("✅ Successfully connected to database!")
        
        # Test group_concat setting
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT @@session.group_concat_max_len as max_len")
            result = cursor.fetchone()
            st.info(f"📊 Group Concat Max Length: {result[0]}")
            cursor.close()
        except:
            pass
        
        connection.close()
        return True
    else:
        st.error("❌ Failed to connect to database")
        return False

def get_table_info(table_name):
    """
    Get information about table columns
    
    Args:
        table_name (str): Name of the table
    
    Returns:
        list: List of column information
    """
    query = f"DESCRIBE {table_name}"
    return execute_query(query)

def get_table_count(table_name, condition=None):
    """
    Get row count from a table
    
    Args:
        table_name (str): Name of the table
        condition (str, optional): WHERE condition
    
    Returns:
        int: Number of rows
    """
    query = f"SELECT COUNT(*) as count FROM {table_name}"
    if condition:
        query += f" WHERE {condition}"
    
    result = execute_query(query)
    return result[0]['count'] if result else 0

def get_database_name():
    """Get current database name"""
    query = "SELECT DATABASE() as db_name"
    result = execute_query(query)
    return result[0]['db_name'] if result else None

# Optional: Environment variables support (more secure)
def get_db_config_from_env():
    """Get database configuration from environment variables"""
    return {
        'host': os.environ.get('DB_HOST', '172.16.128.79'),
        'port': int(os.environ.get('DB_PORT', 3308)),
        'database': os.environ.get('DB_NAME', 'your_database_name'),
        'user': os.environ.get('DB_USER', 'usr4mis'),
        'password': os.environ.get('DB_PASSWORD', 'usr4MIS#@!')
    }