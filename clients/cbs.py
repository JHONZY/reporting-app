import streamlit as st
import plotly.express as px
import pandas as pd
import io
import time
import calendar
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from utils import fetch_dashboard_data, fetch_daily_remarks_cbs, fetch_posted_payments_cbs, fetch_ptp_tracker_cbs, fetch_top_agents

CLIENT_ID = 98
CLIENT_NAME = "CBS HomeLoan"

def show_top_agents():
    """Display Top Agents based on posted payments for CBS"""
    
    st.subheader("🏆 Top Agents Performance")
    st.markdown("---")
    
    # Fetch top agents data (no extra condition for CBS)
    with st.spinner("Loading top agents data..."):
        df = fetch_top_agents(CLIENT_ID, "")
    
    if not df.empty:
        # Create two columns for charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Top Agents by Posted Amount (Bar Chart)
            st.markdown("### 💰 Top Agents by Posted Amount")
            fig_amount = px.bar(
                df.head(10),
                x='agent',
                y='posted_amount',
                title='Posted Amount by Agent',
                labels={'agent': 'Agent', 'posted_amount': 'Posted Amount (₱)'},
                color='posted_amount',
                color_continuous_scale='greens',
                text='posted_amount'
            )
            fig_amount.update_traces(texttemplate='₱%{text:,.0f}', textposition='outside')
            fig_amount.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_amount, use_container_width=True)
        
        with col2:
            # Top Agents by Posted Count (Bar Chart)
            st.markdown("### 📊 Top Agents by Posted Count")
            fig_count = px.bar(
                df.head(10),
                x='agent',
                y='posted_count',
                title='Number of Posted Payments by Agent',
                labels={'agent': 'Agent', 'posted_count': 'Number of Posted Payments'},
                color='posted_count',
                color_continuous_scale='blues',
                text='posted_count'
            )
            fig_count.update_traces(textposition='outside')
            fig_count.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig_count, use_container_width=True)
        
        st.markdown("---")
        
        # Posted Today Section
        st.subheader("📅 Posted Today")
        
        # Filter agents with posted today
        posted_today_df = df[df['posted_today_count'] > 0]
        
        if not posted_today_df.empty:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                total_posted_today = posted_today_df['posted_today_count'].sum()
                st.metric("📦 Total Posted Today", f"{int(total_posted_today):,}")
            
            with col2:
                total_amount_today = posted_today_df['posted_today_amount'].sum()
                st.metric("💰 Total Amount Today", f"₱{total_amount_today:,.2f}")
            
            with col3:
                active_agents = posted_today_df['agent'].nunique()
                st.metric("👥 Active Agents Today", f"{active_agents}")
            
            with col4:
                top_agent_today = posted_today_df.iloc[0]['agent'] if not posted_today_df.empty else "N/A"
                st.metric("🏆 Top Agent Today", top_agent_today)
            
            st.markdown("---")
            
            # Display posted today table
            st.write("### Agents with Posted Payments Today")
            
            display_today_df = posted_today_df[['agent', 'posted_today_count', 'posted_today_amount']].copy()
            display_today_df.columns = ['Agent', 'Posted Count Today', 'Posted Amount Today']
            display_today_df['Posted Amount Today'] = display_today_df['Posted Amount Today'].apply(lambda x: f"₱{x:,.2f}")
            display_today_df = display_today_df.sort_values('Posted Count Today', ascending=False)
            
            st.dataframe(
                display_today_df,
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No payments posted today")
        
        st.markdown("---")
        
        # Detailed Agent Performance Table
        st.subheader("📋 Agent Performance Details")
        
        # Format the dataframe for display
        display_df = df.copy()
        display_df['posted_amount'] = display_df['posted_amount'].apply(lambda x: f"₱{x:,.2f}")
        display_df['ptp_amount'] = display_df['ptp_amount'].apply(lambda x: f"₱{x:,.2f}")
        display_df['posted_today_amount'] = display_df['posted_today_amount'].apply(lambda x: f"₱{x:,.2f}")
        display_df.columns = [
            'Agent', 'Posted Count', 'Posted Amount', 'PTP Count', 
            'PTP Amount', 'Posted Today Count', 'Posted Today Amount'
        ]
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Download button for agent data
        st.subheader("📥 Export Agent Data")
        
        def convert_to_excel_with_autofit(df):
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Top Agents', index=False)
                
                worksheet = writer.sheets['Top Agents']
                for column in worksheet.columns:
                    max_length = 0
                    column_letter = column[0].column_letter
                    for cell in column:
                        try:
                            if len(str(cell.value)) > max_length:
                                max_length = len(str(cell.value))
                        except:
                            pass
                    adjusted_width = min(max_length + 2, 50)
                    worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return output.getvalue()
        
        try:
            excel_data = convert_to_excel_with_autofit(df)
            st.download_button(
                label="📗 Download Agent Performance (Excel)",
                data=excel_data,
                file_name=f"top_agents_{CLIENT_NAME.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as e:
            st.info(f"💡 Excel download requires openpyxl. Install with: pip install openpyxl")
    
    else:
        st.info("No agent performance data available for the current month")

def show():
    """Display CBS HomeLoan dashboard"""
    st.title(f"🏠 {CLIENT_NAME} Dashboard")
    st.markdown("---")
    
    # Filter selection in sidebar
    st.sidebar.markdown("### 📊 Dashboard Filters")
    user_filter_trend = st.sidebar.selectbox(
        "Account Status Filter",
        options=["All", "Active", "Abort"],
        key=f"filter_{CLIENT_ID}"
    )
    
    # Fetch data based on filters
    df, summary = fetch_dashboard_data(CLIENT_ID, user_filter_trend)
    
    # Display KPIs
    col1, col2, col3, col4 = st.columns(4)

    
    with col1:
        st.metric(
            "💰 Total Balance", 
            f"₱{summary.get('total_balance', 0):,.2f}",
            help="Total outstanding balance"
        )
    
    with col2:
        st.metric(
            "👥 Total Accounts", 
            f"{int(summary.get('total_accounts', 0)):,}",
            help="Total number of accounts"
        )
    
    with col3:
        st.metric(
            "📊 Average Balance", 
            f"₱{summary.get('avg_balance', 0):,.2f}",
            help="Average balance per account"
        )
    
    with col4:
        if user_filter_trend == "Active":
            st.metric("Status", "✅ Active Accounts", help="is_aborted = 0")
        elif user_filter_trend == "Abort":
            st.metric("Status", "❌ Aborted Accounts", help="is_aborted = 1")
        else:
            st.metric("Status", "📊 All Accounts", help="All accounts regardless of status")
    
    st.markdown("---")
    
    # Trend Chart
    st.subheader("📈 Account Trends Over Time")
    
    if not df.empty:
        fig = px.line(
            df, 
            x='date', 
            y='active_accounts',
            title=f'{CLIENT_NAME} - Account Activity Trend ({user_filter_trend} Accounts)',
            labels={'date': 'Assignment Date', 'active_accounts': 'Number of Accounts'},
            markers=True
        )
        
        fig.update_layout(
            hovermode='x unified',
            template='plotly_white',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Key insights
        st.subheader("🔍 Key Insights")
        col1, col2 = st.columns(2)
        
        with col1:
            if len(df) >= 2:
                latest = df.iloc[-1]['active_accounts']
                previous = df.iloc[-2]['active_accounts']
                change = ((latest - previous) / previous * 100) if previous > 0 else 0
                
                st.info(f"""
                **Period-over-Period Change:**  
                {'📈 Increase' if change > 0 else '📉 Decrease'} of {abs(change):.1f}%  
                Latest: {int(latest):,} accounts  
                Previous: {int(previous):,} accounts
                """)
        
        with col2:
            if summary.get('peak_date'):
                st.success(f"""
                **Peak Activity Period:**  
                📅 Date: {summary['peak_date']}  
                👥 Accounts: {int(summary['peak_accounts']):,} active accounts
                """)
        
        # Display raw data
        with st.expander("📋 View Detailed Data"):
            display_df = df.copy()
            display_df['active_accounts'] = display_df['active_accounts'].astype(int)
            display_df['total_balance'] = display_df['total_balance'].apply(lambda x: f"₱{x:,.2f}")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.warning(f"No data available for {CLIENT_NAME} with filter: {user_filter_trend}")
    
    st.markdown("---")
    
    # Add Top Agents Section
    show_top_agents()
    
    st.markdown("---")
    st.caption(f"Powered by chester @2026 | Client ID: {CLIENT_ID}")

def show_daily_remark_report():
    """Display Daily Remark Report for CBS with refresh button and loading animation"""
    
    # Initialize session state
    if 'refresh_count_cbs' not in st.session_state:
        st.session_state.refresh_count_cbs = 0
    if 'loading_cbs' not in st.session_state:
        st.session_state.loading_cbs = False
    
    # Custom CSS for loading animation
    st.markdown("""
        <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loader {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        .loading-text {
            text-align: center;
            color: #666;
            font-size: 16px;
            margin-top: 10px;
        }
        
        .pulse {
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Title and refresh button row
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"📋 {CLIENT_NAME} - Daily Remark Report")
    with col2:
        st.markdown("##")
        if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
            st.session_state.refresh_count_cbs += 1
            st.session_state.loading_cbs = True
            st.rerun()

    st.markdown("---")
    
    # Show loading animation while fetching data
    if st.session_state.loading_cbs:
        loading_placeholder = st.empty()
        
        with loading_placeholder.container():
            st.markdown('<div class="loader"></div>', unsafe_allow_html=True)
            st.markdown('<p class="loading-text pulse">🔄 Fetching latest daily remarks from database...</p>', unsafe_allow_html=True)
            st.markdown('<p style="text-align: center; color: #888; font-size: 14px;">Please wait while we refresh your data</p>', unsafe_allow_html=True)
        
        time.sleep(1)
        loading_placeholder.empty()
        st.session_state.loading_cbs = False
    
    # Fetch daily remarks data
    with st.spinner("📊 Loading daily remark reports..."):
        df = fetch_daily_remarks_cbs()
    
    if not df.empty:
        # Display metrics
        st.markdown('<div class="pulse">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Records", f"{len(df):,}")
        with col2:
            st.metric("👥 Unique PNs", f"{df['PN'].nunique():,}")
        with col3:
            st.metric("📅 Latest Record Date", df['Latest Barcode Date'].max().strftime('%Y-%m-%d') if 'Latest Barcode Date' in df.columns else "N/A")
        with col4:
            st.metric("🔄 Refresh Count", st.session_state.refresh_count_cbs)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Display the table
        st.subheader("📋 Daily Remarks Details")
        
        # Format the dataframe for display
        display_df = df.copy()
        
        # Truncate long remarks for better display
        if 'COLLECTION_REMARKS' in display_df.columns:
            display_df['COLLECTION_REMARKS'] = display_df['COLLECTION_REMARKS'].str[:300] + '...'
        
        with st.spinner("🎨 Rendering table..."):
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "PN": st.column_config.TextColumn("PN", width="medium"),
                    "CHCODE": st.column_config.TextColumn("CHCODE", width="medium"),
                    "COLLECTION_REMARKS": st.column_config.TextColumn("Collection Remarks", width="large"),
                    "Latest Barcode Date": st.column_config.DatetimeColumn("Latest Barcode Date", width="medium")
                }
            )
        st.markdown("---")
        st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Download button - Excel only
        st.subheader("📥 Export Data")
        
        # Excel format with auto-column width
        def convert_to_excel_with_autofit(df):
            with st.spinner("📝 Preparing Excel file..."):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Daily Remarks', index=False)
                    
                    # Auto-adjust column widths
                    worksheet = writer.sheets['Daily Remarks']
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return output.getvalue()
        
        try:
            excel_data = convert_to_excel_with_autofit(df)
            st.download_button(
                label="📗 Download Excel (Auto-Fit Columns)",
                data=excel_data,
                file_name=f"cbs_daily_remarks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download Excel file with automatically adjusted column widths"
            )
        except Exception as e:
            st.info(f"💡 Excel download requires openpyxl. Install with: pip install openpyxl. Error: {e}")
        
        # Show search/filter
        st.markdown("---")
        st.subheader("🔍 Search Records")
        
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_term = st.text_input("Search by PN or CHCODE:", placeholder="Enter search term...")
        
        if search_term:
            with st.spinner("🔎 Searching..."):
                filtered_df = df[
                    df['PN'].astype(str).str.contains(search_term, case=False, na=False) |
                    df['CHCODE'].astype(str).str.contains(search_term, case=False, na=False)
                ]
            st.write(f"✅ Found {len(filtered_df)} records:")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    else:
        st.warning("⚠️ No daily remarks data available for the selected period")
    
    # Success message after refresh
    if st.session_state.refresh_count_cbs > 0:
        st.success(f"✅ Data refreshed successfully! (Refresh #{st.session_state.refresh_count_cbs})")
    
    st.markdown("---")
    st.caption(f"Powered by chester @2026 | Client ID: {CLIENT_ID}")

def show_payment_posted_report():
    """Display Payment Posted Report for CBS with date range and status filters"""
    
    # Initialize session state
    if 'refresh_count_posted' not in st.session_state:
        st.session_state.refresh_count_posted = 0
    if 'loading_posted' not in st.session_state:
        st.session_state.loading_posted = False
    
    # Custom CSS for loading animation
    st.markdown("""
        <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loader {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        .loading-text {
            text-align: center;
            color: #666;
            font-size: 16px;
            margin-top: 10px;
        }
        
        .pulse {
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Title and refresh button row
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"💰 {CLIENT_NAME} - Payment Posted Report")
    with col2:
        st.markdown("##")
        if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
            st.session_state.refresh_count_posted += 1
            st.session_state.loading_posted = True
            st.rerun()
    
    st.markdown("---")
    
    # Filters
    st.subheader("📅 Date Range Filter")
    
    # Get today's date
    today = date.today()
    
    # First and last day of the previous month
    first_day_prev_month = (today.replace(day=1) - relativedelta(months=1)).replace(day=1)
    last_day_prev_month = today.replace(day=1) - relativedelta(days=1)
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", first_day_prev_month, key="start_date_posted")
    with col2:
        end_date = st.date_input("End Date", last_day_prev_month, key="end_date_posted")
    
    if start_date > end_date:
        st.warning("🚫 Start date must not be after end date.")
        st.stop()
    
    st.markdown("---")
    
    # Account Status Filter
    st.subheader("🔒 Account Status Filter")
    status_filter = st.selectbox(
        "Select Account Status",
        options=["All", "Locked", "Aborted"],
        key="status_filter_posted",
        help="All = Show all accounts, Locked = Show only locked accounts (is_locked=0), Aborted = Show only aborted accounts (is_aborted=0)"
    )
  
    
    st.markdown("---")
    
    # Show loading animation while fetching data
    if st.session_state.loading_posted:
        loading_placeholder = st.empty()
        
        with loading_placeholder.container():
            st.markdown('<div class="loader"></div>', unsafe_allow_html=True)
            st.markdown('<p class="loading-text pulse">🔄 Fetching payment posted data from database...</p>', unsafe_allow_html=True)
            st.markdown('<p style="text-align: center; color: #888; font-size: 14px;">Please wait while we refresh your data</p>', unsafe_allow_html=True)
        
        time.sleep(1)
        loading_placeholder.empty()
        st.session_state.loading_posted = False
    
    # Fetch payment posted data
    with st.spinner("📊 Loading payment posted reports..."):
        df = fetch_posted_payments_cbs(start_date, end_date, status_filter)
    
    if not df.empty:
        # Display metrics
        st.markdown('<div class="pulse">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Transactions", f"{len(df):,}")
        with col2:
            st.metric("👥 Unique PNs", f"{df['PN NUMBER'].nunique():,}")
        with col3:
            total_ob = df['OB'].sum() if 'OB' in df.columns else 0
            st.metric("💰 Total Outstanding Balance", f"₱{total_ob:,.2f}")
        with col4:
            total_ptp = df['PTP_AMOUNT'].sum() if 'PTP_AMOUNT' in df.columns else 0
            st.metric("💵 Total PTP Amount", f"₱{total_ptp:,.2f}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Display the table
        st.subheader("📋 Payment Posted Details")
        
        # Format the dataframe for display
        display_df = df.copy()
        
        # Format currency columns
        if 'OB' in display_df.columns:
            display_df['OB'] = display_df['OB'].apply(lambda x: f"₱{x:,.2f}" if pd.notnull(x) else "₱0.00")
        if 'PTP_AMOUNT' in display_df.columns:
            display_df['PTP_AMOUNT'] = display_df['PTP_AMOUNT'].apply(lambda x: f"₱{x:,.2f}" if pd.notnull(x) else "₱0.00")
        
        # Truncate long remarks for better display
        if 'REMARKS' in display_df.columns:
            display_df['REMARKS'] = display_df['REMARKS'].str[:100] + '...' if display_df['REMARKS'].str.len().max() > 100 else display_df['REMARKS']
        
        with st.spinner("🎨 Rendering table..."):
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "CLIENT NAME": st.column_config.TextColumn("Client Name", width="medium"),
                    "CH": st.column_config.TextColumn("CH", width="medium"),
                    "ENDO DATE": st.column_config.TextColumn("Endo Date", width="small"),
                    "PN NUMBER": st.column_config.TextColumn("PN Number", width="medium"),
                    "ACCOUNT NAME": st.column_config.TextColumn("Account Name", width="large"),
                    "OB": st.column_config.TextColumn("Outstanding Balance", width="medium"),
                    "PTP DATE": st.column_config.TextColumn("PTP Date", width="small"),
                    "PTP_AMOUNT": st.column_config.TextColumn("PTP Amount", width="medium"),
                    "COLLECTOR": st.column_config.TextColumn("Collector", width="medium"),
                    "STATUS": st.column_config.TextColumn("Status", width="small"),
                    "SUBSTATUS": st.column_config.TextColumn("Substatus", width="medium"),
                    "REMARKS": st.column_config.TextColumn("Remarks", width="large")
                }
            )

        st.markdown("---")
        st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        # Download button - Excel only
        st.subheader("📥 Export Data")
        
        # Excel format with auto-column width
        def convert_to_excel_with_autofit(df):
            with st.spinner("📝 Preparing Excel file..."):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Payment Posted', index=False)
                    
                    # Auto-adjust column widths
                    worksheet = writer.sheets['Payment Posted']
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return output.getvalue()
        
        try:
            excel_data = convert_to_excel_with_autofit(df)
            st.download_button(
                label="📗 Download Excel (Auto-Fit Columns)",
                data=excel_data,
                file_name=f"cbs_payment_posted_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{datetime.now().strftime('%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download Excel file with automatically adjusted column widths"
            )
        except Exception as e:
            st.info(f"💡 Excel download requires openpyxl. Install with: pip install openpyxl. Error: {e}")
        
        # Show search/filter
        st.markdown("---")
        st.subheader("🔍 Search Records")
        
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_term = st.text_input("Search by PN Number, Account Name, or CH:", placeholder="Enter search term...")
        
        if search_term:
            with st.spinner("🔎 Searching..."):
                filtered_df = df[
                    df['PN NUMBER'].astype(str).str.contains(search_term, case=False, na=False) |
                    df['ACCOUNT NAME'].astype(str).str.contains(search_term, case=False, na=False) |
                    df['CH'].astype(str).str.contains(search_term, case=False, na=False)
                ]
            st.write(f"✅ Found {len(filtered_df)} records:")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    else:
        st.warning(f"⚠️ No payment posted data available for the selected date range ({start_date.strftime('%m/%d/%Y')} to {end_date.strftime('%m/%d/%Y')}) and status filter ({status_filter})")
    
    # Success message after refresh
    if st.session_state.refresh_count_posted > 0:
        st.success(f"✅ Data refreshed successfully! (Refresh #{st.session_state.refresh_count_posted})")
    
    st.markdown("---")
    
    # Add Top Agents Section
    show_top_agents()

    st.markdown("---")
    st.caption(f"Powered by chester @2026 | Client ID: {CLIENT_ID}")

def show_ptp_tracker_report():
    """Display PTP Tracker Report for CBS with date range filter"""
    
    # Initialize session state
    if 'refresh_count_ptp' not in st.session_state:
        st.session_state.refresh_count_ptp = 0
    if 'loading_ptp' not in st.session_state:
        st.session_state.loading_ptp = False
    
    # Custom CSS for loading animation
    st.markdown("""
        <style>
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loader {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #3498db;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }
        
        .loading-text {
            text-align: center;
            color: #666;
            font-size: 16px;
            margin-top: 10px;
        }
        
        .pulse {
            animation: pulse 1.5s ease-in-out infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 0.6; }
            50% { opacity: 1; }
            100% { opacity: 0.6; }
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Title and refresh button row
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title(f"📊 {CLIENT_NAME} - PTP Tracker")
    with col2:
        st.markdown("##")
        if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
            st.session_state.refresh_count_ptp += 1
            st.session_state.loading_ptp = True
            st.rerun()
    
    st.markdown("---")
    
    # Date Range Filter
    st.subheader("📅 Date Range Filter")
    
    # Get today's date
    today = date.today()
    last_day = date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=today, key="start_date_ptp")
    with col2:
        end_date = st.date_input("End Date", value=last_day, key="end_date_ptp")
    
    if start_date > end_date:
        st.warning("🚫 Start date must not be after end date.")
        st.stop()
    
    st.markdown("---")
    
    # Show loading animation while fetching data
    if st.session_state.loading_ptp:
        loading_placeholder = st.empty()
        
        with loading_placeholder.container():
            st.markdown('<div class="loader"></div>', unsafe_allow_html=True)
            st.markdown('<p class="loading-text pulse">🔄 Fetching PTP tracker data from database...</p>', unsafe_allow_html=True)
            st.markdown('<p style="text-align: center; color: #888; font-size: 14px;">Please wait while we refresh your data</p>', unsafe_allow_html=True)
        
        time.sleep(1)
        loading_placeholder.empty()
        st.session_state.loading_ptp = False
    
    # Fetch PTP tracker data
    with st.spinner("📊 Loading PTP tracker reports..."):
        df = fetch_ptp_tracker_cbs(start_date, end_date)
    
    if not df.empty:
        # Display metrics
        st.markdown('<div class="pulse">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Records", f"{len(df):,}")
        with col2:
            st.metric("👥 Unique PNs", f"{df['PN NUMBER'].nunique():,}")
        with col3:
            total_ob = df['OB'].sum() if 'OB' in df.columns else 0
            st.metric("💰 Total Outstanding Balance", f"{total_ob:,.2f}")
        with col4:
            # Count PAID vs PENDING vs BP
            paid_count = len(df[df['PAID / BP'] == 'PAID']) if 'PAID / BP' in df.columns else 0
            st.metric("✅ PAID Status", f"{paid_count:,}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        
        st.markdown("---")
        
        # Display the table
        st.subheader("📋 PTP Tracker Details")
        
        # Format the dataframe for display
        display_df = df.copy()
        
        # Format currency columns
        if 'OB' in display_df.columns:
            display_df['OB'] = display_df['OB'].apply(lambda x: f"₱{x:,.2f}" if pd.notnull(x) else "₱0.00")
        
        with st.spinner("🎨 Rendering table..."):
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "AGENCY": st.column_config.TextColumn("Agency", width="small"),
                    "PN NUMBER": st.column_config.TextColumn("PN Number", width="medium"),
                    "ACCT NAME": st.column_config.TextColumn("Account Name", width="large"),
                    "OB": st.column_config.TextColumn("Outstanding Balance", width="medium"),
                    "BUCKET": st.column_config.TextColumn("Bucket", width="small"),
                    "PAYMENT DATE": st.column_config.TextColumn("Payment Date", width="small"),
                    "STATUS IF PAID": st.column_config.TextColumn("Status if Paid", width="medium"),
                    "PAID / BP": st.column_config.TextColumn("Paid/BP", width="small", help="PAID = Payment completed, BP = Broken Promise, PENDING = Awaiting payment"),
                    "DATE PAID": st.column_config.TextColumn("Date Paid", width="small")
                }
            )
        
        st.markdown("---")
        st.caption(f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Download button - Excel only
        st.subheader("📥 Export Data")
        
        # Excel format with auto-column width
        def convert_to_excel_with_autofit(df):
            with st.spinner("📝 Preparing Excel file..."):
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='PTP Tracker', index=False)
                    
                    # Auto-adjust column widths
                    worksheet = writer.sheets['PTP Tracker']
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            return output.getvalue()
        
        try:
            excel_data = convert_to_excel_with_autofit(df)
            st.download_button(
                label="📗 Download Excel (Auto-Fit Columns)",
                data=excel_data,
                file_name=f"cbs_ptp_tracker_{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}_{datetime.now().strftime('%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Download Excel file with automatically adjusted column widths"
            )
        except Exception as e:
            st.info(f"💡 Excel download requires openpyxl. Install with: pip install openpyxl. Error: {e}")
        
        # Status Summary Chart
        st.markdown("---")
        st.subheader("📊 Status Summary")
        
        if 'PAID / BP' in df.columns:
            status_counts = df['PAID / BP'].value_counts()
            
            col1, col2 = st.columns(2)
            with col1:
                # Create a simple bar chart
                import plotly.express as px
                fig = px.bar(
                    x=status_counts.index,
                    y=status_counts.values,
                    title="PTP Status Distribution",
                    labels={'x': 'Status', 'y': 'Count'},
                    color=status_counts.index,
                    color_discrete_map={
                        'PAID': '#28a745',
                        'PENDING': '#ffc107',
                        'BP': '#dc3545'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Show percentage breakdown
                st.write("**Percentage Breakdown:**")
                for status, count in status_counts.items():
                    percentage = (count / len(df)) * 100
                    emoji = "✅" if status == "PAID" else "⏳" if status == "PENDING" else "🔄"
                    st.write(f"{emoji} **{status}:** {percentage:.1f}% ({count:,} records)")
        
        # Show search/filter
        st.markdown("---")
        st.subheader("🔍 Search Records")
        
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_term = st.text_input("Search by PN Number or Account Name:", placeholder="Enter search term...")
        
        if search_term:
            with st.spinner("🔎 Searching..."):
                filtered_df = df[
                    df['PN NUMBER'].astype(str).str.contains(search_term, case=False, na=False) |
                    df['ACCT NAME'].astype(str).str.contains(search_term, case=False, na=False)
                ]
            st.write(f"✅ Found {len(filtered_df)} records:")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    else:
        st.warning(f"⚠️ No PTP tracker data available for the selected date range ({start_date.strftime('%m/%d/%Y')} to {end_date.strftime('%m/%d/%Y')})")
    
    # Success message after refresh
    if st.session_state.refresh_count_ptp > 0:
        st.success(f"✅ Data refreshed successfully! (Refresh #{st.session_state.refresh_count_ptp})")
    
    st.markdown("---")
    
    # Add Top Agents Section
    show_top_agents()
    
    st.markdown("---")
    st.caption(f"Powered by chester @2026 | Client ID: {CLIENT_ID}")

def show_report(report_name):
    """Display CBS reports placeholder"""
    st.title(f"📊 {CLIENT_NAME} - {report_name}")
    st.markdown("---")
    st.info(f"This is the {report_name} report for {CLIENT_NAME}.")
    st.write("Report content will be implemented here.")
    st.markdown("---")
    st.caption(f"Powered by chester @2026 | Client ID: {CLIENT_ID}")