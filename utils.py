import os
import pandas as pd
import io
from database import execute_query

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
QUERIES_PATH = os.path.join(BASE_DIR, "queries")

REPORT_QUERIES = {
    "dashboard": os.path.join(QUERIES_PATH, "dashboard.sql"),
    "dashboard_agents": os.path.join(QUERIES_PATH, "dashboard_agents.sql"),
    "remarks_msb": os.path.join(QUERIES_PATH, "remarks_msb.sql"),
    "remarks_cbs": os.path.join(QUERIES_PATH, "remarks_cbs.sql"),
    "remarks_chinabank": os.path.join(QUERIES_PATH, "remarks_chinabank.sql"),
    "posted_cbs": os.path.join(QUERIES_PATH, "posted_cbs.sql"),
    "ptp_tracker_cbs": os.path.join(QUERIES_PATH, "ptp_tracker_cbs.sql"),
    "chinabank_ptp": os.path.join(QUERIES_PATH, "chinabank_ptp.sql")
}

def load_sql_query(query_name):
    """Load SQL query from file"""
    query_path = REPORT_QUERIES.get(query_name)
    if query_path and os.path.exists(query_path):
        with open(query_path, 'r') as file:
            return file.read()
    return None

def get_user_filter_condition(filter_type):
    """Get user filter condition based on selection"""
    if filter_type == "Active":
        return "AND debtor.`is_aborted` = 0"
    elif filter_type == "Abort":
        return "AND debtor.`is_aborted` = 1"
    else:  # "All"
        return ""

def get_status_filter_condition(filter_type):
    """Get status filter condition for Payment Posted report"""
    if filter_type == "Locked":
        return "AND debtor.`is_locked` = 0"
    elif filter_type == "Aborted":
        return "AND debtor.`is_aborted` = 0"
    else:  # "All"
        return ""

def fetch_dashboard_data(client_id, filter_type):
    """Fetch dashboard data based on client and filter"""
    dashboard_query = load_sql_query("dashboard")
    user_filter = get_user_filter_condition(filter_type)
    
    if dashboard_query:
        formatted_query = dashboard_query.format(
            client_id=client_id,
            user_condition_filter=user_filter
        )
        
        data = execute_query(formatted_query)
        df = pd.DataFrame(data) if data else pd.DataFrame()
        
        # Calculate summary metrics
        if not df.empty:
            summary = {
                'total_balance': df['total_balance'].sum() if 'total_balance' in df.columns else 0,
                'total_accounts': df['active_accounts'].sum() if 'active_accounts' in df.columns else 0,
                'avg_balance': df['total_balance'].mean() if 'total_balance' in df.columns else 0,
                'peak_accounts': df['active_accounts'].max() if 'active_accounts' in df.columns else 0,
                'peak_date': df.loc[df['active_accounts'].idxmax(), 'date'] if not df.empty and 'active_accounts' in df.columns else None
            }
            return df, summary
        return df, {}
    return pd.DataFrame(), {}

def fetch_top_agents(client_id, extra_condition=""):
    """Fetch top agents based on posted payments"""
    query = load_sql_query("dashboard_agents")
    
    if query:
        formatted_query = query.format(
            client_id=client_id,
            extra_condition=extra_condition
        )
        data = execute_query(formatted_query)
        df = pd.DataFrame(data) if data else pd.DataFrame()
        return df
    return pd.DataFrame()

def fetch_collection_remarks_msb():
    """Fetch collection remarks data for MSB"""
    query = load_sql_query("remarks_msb")
    
    if query:
        data = execute_query(query)
        df = pd.DataFrame(data) if data else pd.DataFrame()
        return df
    return pd.DataFrame()

# Alias for backward compatibility
fetch_collection_remarks = fetch_collection_remarks_msb

def fetch_daily_remarks_cbs():
    """Fetch daily remarks data for CBS"""
    query = load_sql_query("remarks_cbs")
    
    if query:
        data = execute_query(query)
        df = pd.DataFrame(data) if data else pd.DataFrame()
        return df
    return pd.DataFrame()

def fetch_posted_payments_cbs(start_date, end_date, status_filter_type):
    """Fetch posted payments data for CBS with date range and status filters"""
    query = load_sql_query("posted_cbs")
    
    if query:
        # Format dates for SQL
        start_date_str = start_date.strftime('%Y-%m-%d 00:00:00')
        end_date_str = end_date.strftime('%Y-%m-%d 23:59:59')
        
        # Get status filter condition
        status_filter = get_status_filter_condition(status_filter_type)
        
        # Format the query
        formatted_query = query.format(
            start_date=start_date_str,
            end_date=end_date_str,
            status_filter=status_filter
        )
        
        data = execute_query(formatted_query)
        df = pd.DataFrame(data) if data else pd.DataFrame()
        return df
    return pd.DataFrame()

def fetch_ptp_tracker_cbs(start_date, end_date):
    """Fetch PTP tracker data for CBS with date range filter"""
    query = load_sql_query("ptp_tracker_cbs")
    
    if query:
        # Format dates as mm/dd/yyyy
        start_date_str = start_date.strftime('%m/%d/%Y')
        end_date_str = end_date.strftime('%m/%d/%Y')
        
        # Format the query
        formatted_query = query.format(
            start_date=start_date_str,
            end_date=end_date_str
        )
        
        data = execute_query(formatted_query)
        df = pd.DataFrame(data) if data else pd.DataFrame()
        return df
    return pd.DataFrame()

def fetch_chinabank_ptp():
    """Fetch PTP Inventory data for Chinabank"""
    query = load_sql_query("chinabank_ptp")
    
    if query:
        data = execute_query(query)
        df = pd.DataFrame(data) if data else pd.DataFrame()
        return df
    return pd.DataFrame()

def fetch_chinabank_collection_remarks():
    """Fetch collection remarks data for Chinabank"""
    query = load_sql_query("remarks_chinabank")
    
    if query:
        data = execute_query(query)
        df = pd.DataFrame(data) if data else pd.DataFrame()
        return df
    return pd.DataFrame()