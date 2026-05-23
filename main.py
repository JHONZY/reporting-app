import streamlit as st
import sys
import os

# Add the current directory to path to ensure clients module is found
sys.path.insert(0, os.path.dirname(__file__))

# Import client modules
from clients import cbs, msb, chinabank

# Page configuration
st.set_page_config(
    page_title="GENESIS 2.0",
    page_icon="🏦",
    layout="wide"
)

# Custom CSS to hide default page navigation
st.markdown("""
    <style>
    /* Hide default page navigation */
    .stApp header {
        display: none;
    }
    
    /* Hide the default sidebar navigation menu */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #f0f2f6;
    }
    
    /* Header styling */
    .sidebar-header {
        text-align: center;
        padding: 20px 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 30px;
    }
    
    .sidebar-header h1 {
        color: white;
        font-size: 24px;
        margin: 0;
        font-weight: bold;
    }
    
    /* Footer styling */
    .sidebar-footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        text-align: center;
        padding: 20px;
        background-color: #f0f2f6;
        font-size: 12px;
        color: #666;
    }
    
    /* Combo box styling in sidebar */
    .stSelectbox {
        margin-bottom: 20px;
    }
    
    .stSelectbox label {
        font-weight: bold;
        color: #333;
    }
    
    /* Remove top padding to utilize space */
    .main .block-container {
        padding-top: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# SIDEBAR NAVIGATION WITH COMBO BOX
with st.sidebar:
    # Header
    st.markdown("""
        <div class="sidebar-header">
            <h1>GENESIS 2.0</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Navigation label
    st.markdown("### 📋 Navigation")
    
    # COMBO BOX (Selectbox) for client selection
    selected_client = st.selectbox(
        "Select Client",
        options=["CBS HOMELOAN", "MSB MALAYAN", "CHINABANK SAVINGS"],
        index=0,
        key="client_selector"
    )
    
    st.markdown("---")
    
    # Report Type Selection based on client
    st.markdown("### 📊 Report Type")
    
    if selected_client == "CBS HOMELOAN":
        report_type = st.selectbox(
            "Select Report",
            options=["Dashboard", "Trails Upload", "Daily Remark Report", "Payment Posted", "PTP Tracker"],
            index=0,
            key="report_selector"
        )
    elif selected_client == "MSB MALAYAN":
        report_type = st.selectbox(
            "Select Report",
            options=["Dashboard", "Collection Remarks"],
            index=0,
            key="report_selector"
        )
    else:  # CHINABANK SAVINGS
        report_type = st.selectbox(
            "Select Report",
            options=["Dashboard", "PTP Inventory", "Confirmed Payments", "Collection Remarks"],
            index=0,
            key="report_selector"
        )
    
    st.markdown("---")
    
    # Footer
    st.markdown("""
        <div class="sidebar-footer">
            Powered by chester @2026
        </div>
    """, unsafe_allow_html=True)

# In the MAIN CONTENT AREA section, add the PTP Tracker condition:
if selected_client == "CBS HOMELOAN":
    if report_type == "Dashboard":
        cbs.show()
    elif report_type == "Daily Remark Report":
        cbs.show_daily_remark_report()
    elif report_type == "Payment Posted":
        cbs.show_payment_posted_report()
    elif report_type == "PTP Tracker":
        cbs.show_ptp_tracker_report()
    else:
        # Show placeholder for other CBS reports
        cbs.show_report(report_type)
        
elif selected_client == "MSB MALAYAN":
    if report_type == "Dashboard":
        msb.show()
    elif report_type == "Collection Remarks":
        msb.show_collection_remarks()

# In the MAIN CONTENT AREA section, update Chinabank routing:
elif selected_client == "CHINABANK SAVINGS":
    if report_type == "Dashboard":
        chinabank.show()
    elif report_type == "PTP Inventory":
        chinabank.show_ptp_inventory()
    elif report_type == "Confirmed Payments":
        chinabank.show_confirmed_payments()
    elif report_type == "Collection Remarks":
        chinabank.show_collection_remarks()
    else:
        chinabank.show_report(report_type)