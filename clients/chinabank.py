import streamlit as st
import plotly.express as px
import pandas as pd
import io
import time
from datetime import datetime, date
from utils import fetch_dashboard_data, fetch_chinabank_ptp, fetch_chinabank_collection_remarks, fetch_top_agents

CLIENT_ID = 113
CLIENT_NAME = "Chinabank Savings"

def show_top_agents():
    """Display Top Agents based on posted payments for Chinabank"""
    
    st.subheader("🏆 Top Agents Performance")
    st.markdown("---")
    
    # Fetch top agents data with extra condition for Chinabank
    with st.spinner("Loading top agents data..."):
        extra_condition = "AND debtor.`account_type` <> 'WRITEOFF'"
        df = fetch_top_agents(CLIENT_ID, extra_condition)
    
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
    """Display Chinabank Savings dashboard"""
    st.title(f"💰 {CLIENT_NAME} Dashboard")
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
            f"₱{summary.get('total_balance', 0):,.2f}"
        )
    
    with col2:
        st.metric(
            "👥 Total Accounts", 
            f"{int(summary.get('total_accounts', 0)):,}"
        )
    
    with col3:
        st.metric(
            "📊 Average Balance", 
            f"₱{summary.get('avg_balance', 0):,.2f}"
        )
    
    with col4:
        st.metric(
            "📈 Data Points", 
            f"{len(df)} periods" if not df.empty else "0"
        )
    
    st.markdown("---")
    
    # Trend Chart
    st.subheader("📊 Account Activity Trend Analysis")
    
    if not df.empty:
        fig = px.area(
            df, 
            x='date', 
            y='active_accounts',
            title=f'{CLIENT_NAME} - Account Activity Trend ({user_filter_trend} Accounts)',
            labels={'date': 'Assignment Date', 'active_accounts': 'Number of Active Accounts'},
            color_discrete_sequence=['#2ecc71']
        )
        
        fig.update_layout(
            hovermode='x unified',
            template='plotly_white',
            height=500,
            xaxis_title="Date",
            yaxis_title="Number of Active Accounts"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Display raw data
        with st.expander("📋 View Detailed Data Table"):
            display_df = df.copy()
            display_df['active_accounts'] = display_df['active_accounts'].astype(int)
            display_df['total_balance'] = display_df['total_balance'].apply(lambda x: f"₱{x:,.2f}")
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Data as CSV",
            data=csv,
            file_name=f"{CLIENT_NAME.lower().replace(' ', '_')}_{user_filter_trend.lower()}_data.csv",
            mime="text/csv"
        )
    else:
        st.warning(f"No data available for {CLIENT_NAME} with filter: {user_filter_trend}")
    
    st.markdown("---")
    
    # Add Top Agents Section
    show_top_agents()
    
    st.markdown("---")
    st.caption(f"Powered by chester @2026 | Client ID: {CLIENT_ID}")

def show_ptp_inventory():
    """Display PTP Inventory Report for Chinabank with refresh button and loading animation"""
    
    # Initialize session state
    if 'refresh_count_chinabank_ptp' not in st.session_state:
        st.session_state.refresh_count_chinabank_ptp = 0
    if 'loading_chinabank_ptp' not in st.session_state:
        st.session_state.loading_chinabank_ptp = False
    
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
        st.title(f"📋 {CLIENT_NAME} - PTP Inventory")
    with col2:
        st.markdown("##")
        if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
            st.session_state.refresh_count_chinabank_ptp += 1
            st.session_state.loading_chinabank_ptp = True
            st.rerun()

    
    st.markdown("---")
    
    # Show loading animation while fetching data
    if st.session_state.loading_chinabank_ptp:
        loading_placeholder = st.empty()
        
        with loading_placeholder.container():
            st.markdown('<div class="loader"></div>', unsafe_allow_html=True)
            st.markdown('<p class="loading-text pulse">🔄 Fetching PTP Inventory data from database...</p>', unsafe_allow_html=True)
            st.markdown('<p style="text-align: center; color: #888; font-size: 14px;">Please wait while we refresh your data</p>', unsafe_allow_html=True)
        
        time.sleep(1)
        loading_placeholder.empty()
        st.session_state.loading_chinabank_ptp = False
    
    # Fetch PTP Inventory data
    with st.spinner("📊 Loading PTP Inventory reports..."):
        df = fetch_chinabank_ptp()
    
    if not df.empty:
        # Display metrics
        st.markdown('<div class="pulse">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Records", f"{len(df):,}")
        with col2:
            st.metric("👥 Unique PNs", f"{df['PN'].nunique():,}")
        with col3:
            total_ob = df['OB'].sum() if 'OB' in df.columns else 0
            st.metric("💰 Total Outstanding Balance", f"₱{total_ob:,.2f}")
        with col4:
            total_ptp = df['PTP AMOUNT'].sum() if 'PTP AMOUNT' in df.columns else 0
            st.metric("💵 Total PTP Amount", f"₱{total_ptp:,.2f}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Display the table
        st.subheader("📋 PTP Inventory Details")
        
        # Format the dataframe for display
        display_df = df.copy()
        
        # Format currency columns
        if 'OB' in display_df.columns:
            display_df['OB'] = display_df['OB'].apply(lambda x: f"₱{x:,.2f}" if pd.notnull(x) else "₱0.00")
        if 'MO. AMORT' in display_df.columns:
            display_df['MO. AMORT'] = display_df['MO. AMORT'].apply(lambda x: f"₱{x:,.2f}" if pd.notnull(x) else "₱0.00")
        if 'PTP AMOUNT' in display_df.columns:
            display_df['PTP AMOUNT'] = display_df['PTP AMOUNT'].apply(lambda x: f"₱{x:,.2f}" if pd.notnull(x) else "₱0.00")
        
        with st.spinner("🎨 Rendering table..."):
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "ENDORSEMENT DATE": st.column_config.TextColumn("Endorsement Date", width="small"),
                    "AGENCY": st.column_config.TextColumn("Agency", width="small"),
                    "COLLECTOR": st.column_config.TextColumn("Collector", width="medium"),
                    "ACCOUNT NUMBER": st.column_config.TextColumn("Account Number", width="medium"),
                    "PN": st.column_config.TextColumn("PN", width="medium"),
                    "ACCOUNT NAME": st.column_config.TextColumn("Account Name", width="large"),
                    "PRODUCT DESCRIPTION": st.column_config.TextColumn("Product Description", width="medium"),
                    "OB": st.column_config.TextColumn("OB", width="medium"),
                    "MO. AMORT": st.column_config.TextColumn("MO. Amort", width="medium"),
                    "PTP AMOUNT": st.column_config.TextColumn("PTP Amount", width="medium"),
                    "PTP_ACQUIRED": st.column_config.TextColumn("PTP Acquired", width="small"),
                    "REMARKS": st.column_config.TextColumn("Remarks", width="large"),
                    "PTP DATE": st.column_config.TextColumn("PTP Date", width="small"),
                    "Final Bucket": st.column_config.TextColumn("Final Bucket", width="medium")
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
                    df.to_excel(writer, sheet_name='PTP Inventory', index=False)
                    
                    # Auto-adjust column widths
                    worksheet = writer.sheets['PTP Inventory']
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
                file_name=f"chinabank_ptp_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
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
            search_term = st.text_input("Search by PN, Account Number, or Account Name:", placeholder="Enter search term...")
        
        if search_term:
            with st.spinner("🔎 Searching..."):
                filtered_df = df[
                    df['PN'].astype(str).str.contains(search_term, case=False, na=False) |
                    df['ACCOUNT NUMBER'].astype(str).str.contains(search_term, case=False, na=False) |
                    df['ACCOUNT NAME'].astype(str).str.contains(search_term, case=False, na=False)
                ]
            st.write(f"✅ Found {len(filtered_df)} records:")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    else:
        st.warning("⚠️ No PTP Inventory data available for the current period")
    
    # Success message after refresh
    if st.session_state.refresh_count_chinabank_ptp > 0:
        st.success(f"✅ Data refreshed successfully! (Refresh #{st.session_state.refresh_count_chinabank_ptp})")
    
    st.markdown("---")
    st.caption(f"Powered by chester @2026 | Client ID: {CLIENT_ID}")

def show_collection_remarks():
    """Display Collection Remarks Report for Chinabank with refresh button and loading animation"""
    
    # Initialize session state
    if 'refresh_count_chinabank_remarks' not in st.session_state:
        st.session_state.refresh_count_chinabank_remarks = 0
    if 'loading_chinabank_remarks' not in st.session_state:
        st.session_state.loading_chinabank_remarks = False
    
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
        st.title(f"📋 {CLIENT_NAME} - Collection Remarks Report")
    with col2:
        st.markdown("##")
        if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
            st.session_state.refresh_count_chinabank_remarks += 1
            st.session_state.loading_chinabank_remarks = True
            st.rerun()

    
    st.markdown("---")
    
    # Show loading animation while fetching data
    if st.session_state.loading_chinabank_remarks:
        loading_placeholder = st.empty()
        
        with loading_placeholder.container():
            st.markdown('<div class="loader"></div>', unsafe_allow_html=True)
            st.markdown('<p class="loading-text pulse">🔄 Fetching collection remarks from database...</p>', unsafe_allow_html=True)
            st.markdown('<p style="text-align: center; color: #888; font-size: 14px;">Please wait while we refresh your data</p>', unsafe_allow_html=True)
        
        time.sleep(1)
        loading_placeholder.empty()
        st.session_state.loading_chinabank_remarks = False
    
    # Fetch collection remarks data
    with st.spinner("📊 Loading collection remarks reports..."):
        df = fetch_chinabank_collection_remarks()
    
    if not df.empty:
        # Display metrics
        st.markdown('<div class="pulse">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Records", f"{len(df):,}")
        with col2:
            st.metric("👥 Unique PNs", f"{df['PN'].nunique():,}")
        with col3:
            st.metric("🏢 Agency", "SPM")
        with col4:
            st.metric("🔄 Refresh Count", st.session_state.refresh_count_chinabank_remarks)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Display the table
        st.subheader("📋 Collection Remarks Details")
        
        # Format the dataframe for display
        display_df = df.copy()
        
        # Truncate long remarks for better display
        if 'COLLECTION_REMARKS' in display_df.columns:
            display_df['COLLECTION_REMARKS'] = display_df['COLLECTION_REMARKS'].str[:300] + '...' if display_df['COLLECTION_REMARKS'].str.len().max() > 300 else display_df['COLLECTION_REMARKS']
        
        with st.spinner("🎨 Rendering table..."):
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "DATE": st.column_config.TextColumn("Date", width="small"),
                    "PN": st.column_config.TextColumn("PN", width="medium"),
                    "NAME": st.column_config.TextColumn("Account Name", width="large"),
                    "COLLECTION_REMARKS": st.column_config.TextColumn("Collection Remarks", width="large"),
                    "AGENCY": st.column_config.TextColumn("Agency", width="small")
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
                    df.to_excel(writer, sheet_name='Collection Remarks', index=False)
                    
                    # Auto-adjust column widths
                    worksheet = writer.sheets['Collection Remarks']
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
                file_name=f"chinabank_collection_remarks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
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
            search_term = st.text_input("Search by PN or Account Name:", placeholder="Enter search term...")
        
        if search_term:
            with st.spinner("🔎 Searching..."):
                filtered_df = df[
                    df['PN'].astype(str).str.contains(search_term, case=False, na=False) |
                    df['NAME'].astype(str).str.contains(search_term, case=False, na=False)
                ]
            st.write(f"✅ Found {len(filtered_df)} records:")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    else:
        st.warning("⚠️ No collection remarks data available for the selected period")
    
    # Success message after refresh
    if st.session_state.refresh_count_chinabank_remarks > 0:
        st.success(f"✅ Data refreshed successfully! (Refresh #{st.session_state.refresh_count_chinabank_remarks})")
    
    st.markdown("---")
    st.caption(f"Powered by chester @2026 | Client ID: {CLIENT_ID}")

def show_confirmed_payments():
    """Display Confirmed Payments Report - Coming Soon"""
    st.title(f"💰 {CLIENT_NAME} - Confirmed Payments")
    st.markdown("---")
    
    # Coming Soon banner with styling
    st.markdown("""
        <div style="text-align: center; padding: 60px 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 20px; margin: 20px 0;">
            <h1 style="color: white; font-size: 48px; margin-bottom: 20px;">🚧 COMING SOON 🚧</h1>
            <p style="color: white; font-size: 20px; opacity: 0.9;">This feature is currently under development</p>
            <p style="color: white; font-size: 16px; opacity: 0.7; margin-top: 20px;">Confirmed Payments report will be available in the next release</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Add some visual elements
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📊 **Features Coming:**")
        st.write("• Payment confirmation tracking")
        st.write("• Real-time payment status")
    with col2:
        st.info("📅 **Expected Features:**")
        st.write("• Date range filtering")
        st.write("• Payment amount summaries")
    with col3:
        st.info("📥 **Export Options:**")
        st.write("• Excel download with auto-fit")
        st.write("• Search and filter capabilities")
    
    st.markdown("---")
    st.caption(f"Powered by chester @2026 | Client ID: {CLIENT_ID} | Status: In Development")

def show_report(report_name):
    """Display Chinabank reports placeholder"""
    st.title(f"📊 {CLIENT_NAME} - {report_name}")
    st.markdown("---")
    st.info(f"This is the {report_name} report for {CLIENT_NAME}.")
    st.write("Report content will be implemented here.")
    st.markdown("---")
    st.caption(f"Powered by chester @2026 | Client ID: {CLIENT_ID}")