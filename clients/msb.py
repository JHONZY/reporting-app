import streamlit as st
import plotly.express as px
import pandas as pd
import io
import time
from datetime import datetime
from utils import fetch_dashboard_data, fetch_collection_remarks_msb, fetch_top_agents

CLIENT_ID = 112
CLIENT_NAME = "MSB Malayan"


def show_top_agents():
    """Display Top Agents based on posted payments for MSB"""
    
    st.subheader("🏆 Top Agents Performance")
    st.markdown("---")
    
    # Fetch top agents data (no extra condition for MSB)
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
    """Display MSB Malayan dashboard"""
    st.title(f"🏦 {CLIENT_NAME} Dashboard")
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
        if user_filter_trend == "Active":
            st.metric("Status", "✅ Active")
        elif user_filter_trend == "Abort":
            st.metric("Status", "❌ Aborted")
        else:
            st.metric("Status", "📊 All")
    
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
        
        # Display raw data
        with st.expander("📋 View Detailed Data"):
            display_df = df.copy()
            display_df['active_accounts'] = display_df['active_accounts'].astype(int)
            display_df['total_balance'] = display_df['total_balance'].apply(lambda x: f"₱{x:,.2f}")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
    else:
        st.warning(f"No data available for {CLIENT_NAME} with filter: {user_filter_trend}")
    
    # Add Top Agents Section
    show_top_agents()
    
    st.markdown("---")

    st.caption(f"Powered by chester @2026 | Client ID: {CLIENT_ID}")

def show_collection_remarks():
    """Display Collection Remarks report with refresh button and loading animation"""
    
    # Initialize session state
    if 'refresh_count_msb' not in st.session_state:
        st.session_state.refresh_count_msb = 0
    if 'loading_msb' not in st.session_state:
        st.session_state.loading_msb = False
    
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
            st.session_state.refresh_count_msb += 1
            st.session_state.loading_msb = True
            st.rerun()
    
    st.markdown("---")
    
    # Show loading animation while fetching data
    if st.session_state.loading_msb:
        loading_placeholder = st.empty()
        
        with loading_placeholder.container():
            st.markdown('<div class="loader"></div>', unsafe_allow_html=True)
            st.markdown('<p class="loading-text pulse">🔄 Fetching latest collection remarks from database...</p>', unsafe_allow_html=True)
            st.markdown('<p style="text-align: center; color: #888; font-size: 14px;">Please wait while we refresh your data</p>', unsafe_allow_html=True)
        
        time.sleep(1)
        loading_placeholder.empty()
        st.session_state.loading_msb = False
    
    # Fetch collection remarks data
    with st.spinner("📊 Loading collection remarks data..."):
        df = fetch_collection_remarks_msb()
    
    if not df.empty:
        # Display metrics
        st.markdown('<div class="pulse">', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Records", f"{len(df):,}")
        with col2:
            st.metric("👥 Unique Accounts", f"{df['PN'].nunique():,}")
        with col3:
            st.metric("📅 Last Update in Data", df['DATE'].max() if 'DATE' in df.columns else "N/A")
        with col4:
            st.metric("🔄 Refresh Count", st.session_state.refresh_count_msb)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Display the table
        st.subheader("📋 Collection Remarks Details")
        
        # Format the dataframe for display
        display_df = df.copy()
        
        # Truncate long remarks for better display
        if 'COLLECTION_REMARKS' in display_df.columns:
            display_df['COLLECTION_REMARKS'] = display_df['COLLECTION_REMARKS'].str[:200] + '...'
        
        with st.spinner("🎨 Rendering table..."):
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "DATE": st.column_config.TextColumn("Date", width="small"),
                    "PN": st.column_config.TextColumn("PN", width="medium"),
                    "NAME": st.column_config.TextColumn("Name", width="large"),
                    "OLD IC": st.column_config.TextColumn("Old IC", width="medium"),
                    "COLLECTION_REMARKS": st.column_config.TextColumn("Collection Remarks", width="large"),
                    "AGENCY": st.column_config.TextColumn("Agency", width="small"),
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
                file_name=f"msb_collection_remarks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
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
            search_term = st.text_input("Search by PN, Name, or Old IC:", placeholder="Enter search term...")
        
        if search_term:
            with st.spinner("🔎 Searching..."):
                filtered_df = df[
                    df['PN'].astype(str).str.contains(search_term, case=False, na=False) |
                    df['NAME'].astype(str).str.contains(search_term, case=False, na=False) |
                    df['OLD IC'].astype(str).str.contains(search_term, case=False, na=False)
                ]
            st.write(f"✅ Found {len(filtered_df)} records:")
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
    
    else:
        st.warning("⚠️ No collection remarks data available for the selected period")
    
    # Success message after refresh
    if st.session_state.refresh_count_msb > 0:
        st.success(f"✅ Data refreshed successfully! (Refresh #{st.session_state.refresh_count_msb})")

    
    st.markdown("---")
    
    st.caption(f"Powered by chester @2026 | Client ID: {CLIENT_ID}")