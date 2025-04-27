import streamlit as st
import pandas as pd
import plotly.express as px
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from datetime import datetime, timedelta
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Streamlit page configuration
st.set_page_config(page_title="FinTech Price and Volume Dashboard", layout="wide")

# Initialize Cassandra connection
@st.cache_resource
def init_cassandra():
    try:
        cluster = Cluster(['cassandra'], port=9042)
        session = cluster.connect('fintech')
        logger.info("Successfully connected to Cassandra")
        return session
    except Exception as e:
        logger.error(f"Failed to connect to Cassandra: {str(e)}")
        st.error(f"Cannot connect to Cassandra: {str(e)}")
        return None

# Function to fetch available symbols
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_available_symbols(_session):
    try:
        query = "SELECT DISTINCT symbol FROM raw_financial_data"
        rows = _session.execute(query)
        symbols = [row.symbol for row in rows if row.symbol]
        logger.info(f"Available symbols: {symbols}")
        return symbols if symbols else ["No symbols found"]
    except Exception as e:
        logger.error(f"Error fetching symbols: {str(e)}")
        st.error(f"Error fetching symbols: {str(e)}")
        return ["Error fetching symbols"]

# Function to fetch raw data for a symbol
def fetch_raw_data(_session, symbol, time_window_hours=24, fetch_all=False):
    try:
        if fetch_all:
            query = "SELECT timestamp, price, volume FROM raw_financial_data WHERE symbol = %s"
            statement = SimpleStatement(query)
            rows = _session.execute(statement, [symbol])
        else:
            query = """
            SELECT timestamp, price, volume 
            FROM raw_financial_data 
            WHERE symbol = %s AND timestamp >= %s
            """
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_window_hours)
            statement = SimpleStatement(query)
            rows = _session.execute(statement, [symbol, start_time])
        
        df = pd.DataFrame(rows, columns=['timestamp', 'price', 'volume'])
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.sort_values('timestamp')
            logger.info(f"Fetched {len(df)} raw data rows for {symbol}")
        else:
            logger.warning(f"No raw data found for {symbol}")
        return df
    except Exception as e:
        logger.error(f"Error fetching raw data for {symbol}: {str(e)}")
        st.error(f"Error fetching raw data for {symbol}: {str(e)}")
        return pd.DataFrame()

# Function to fetch aggregated data for a symbol
def fetch_aggregated_data(_session, symbol, time_window_hours=24, fetch_all=False):
    try:
        if fetch_all:
            query = """
            SELECT window_start, avg_price, price_change, total_volume 
            FROM aggregated_financial_data 
            WHERE symbol = %s
            """
            statement = SimpleStatement(query)
            rows = _session.execute(statement, [symbol])
        else:
            query = """
            SELECT window_start, avg_price, price_change, total_volume 
            FROM aggregated_financial_data 
            WHERE symbol = %s AND window_start >= %s
            """
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=time_window_hours)
            statement = SimpleStatement(query)
            rows = _session.execute(statement, [symbol, start_time])
        
        df = pd.DataFrame(rows, columns=['window_start', 'avg_price', 'price_change', 'total_volume'])
        if not df.empty:
            df['window_start'] = pd.to_datetime(df['window_start'])
            df = df.sort_values('window_start')
            logger.info(f"Fetched {len(df)} aggregated data rows for {symbol}")
        else:
            logger.warning(f"No aggregated data found for {symbol}")
        return df
    except Exception as e:
        logger.error(f"Error fetching aggregated data for {symbol}: {str(e)}")
        st.error(f"Error fetching aggregated data for {symbol}: {str(e)}")
        return pd.DataFrame()

# Main dashboard function
def main():
    session = init_cassandra()
    if session is None:
        st.stop()
    
    st.title("FinTech Price and Volume Dashboard")
    
    # Sidebar for configuration
    st.sidebar.header("Settings")
    default_symbols = ["IC MARKETS:1", "BINANCE:BTCUSDT", "AAPL"]
    available_symbols = get_available_symbols(session)
    
    # Combine default symbols with available ones
    display_symbols = [s for s in default_symbols if s in available_symbols]
    if len(display_symbols) < len(default_symbols):
        display_symbols += [s for s in available_symbols if s not in default_symbols and s != "BINANCE"]
    
    symbol = st.sidebar.selectbox("Select Symbol", display_symbols, index=0)
    time_window = st.sidebar.slider("Time Window (hours)", 1, 48, 24)
    refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 30, 5)
    fetch_all = st.sidebar.checkbox("Fetch All Data (Ignore Time Window)", value=True)
    debug_mode = st.sidebar.checkbox("Enable Debug Mode", value=True)
    
    # Create tabs for better organization
    tab1, tab2 = st.tabs(["Raw Data", "Aggregated Data"])
    
    # Create placeholder for last updated text
    last_update_placeholder = st.sidebar.empty()
    
    # Create placeholders for all charts and metrics
    with tab1:
        raw_price_chart = st.empty()
        raw_volume_chart = st.empty()
    
    with tab2:
        metrics_container = st.empty()
        agg_price_chart = st.empty()
        price_change_chart = st.empty()
        total_volume_chart = st.empty()
    
    # Debug placeholder
    if debug_mode:
        debug_container = st.empty()
    
    # Main update loop - runs forever but uses Streamlit's rerun mechanism
    while True:
        # Update timestamp
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        last_update_placeholder.write(f"Last updated: {current_time}")
        
        # Fetch fresh data
        raw_df = fetch_raw_data(session, symbol, time_window_hours=time_window, fetch_all=fetch_all)
        agg_df = fetch_aggregated_data(session, symbol, time_window_hours=time_window, fetch_all=fetch_all)
        
        # Debug information
        if debug_mode:
            with debug_container.container():
                st.write(f"Selected Symbol: {symbol}")
                st.write(f"Raw Data Rows: {len(raw_df)}")
                st.write(f"Aggregated Data Rows: {len(agg_df)}")
                st.write(f"Update Time: {current_time}")
        
        # Update Raw Data tab
        with tab1:
            # Update raw price chart
            with raw_price_chart.container():
                st.subheader(f"Price Trend for {symbol}")
                if not raw_df.empty:
                    fig = px.line(raw_df, x='timestamp', y='price', title=f"{symbol} Price Over Time")
                    fig.update_layout(
                        xaxis_title="Time",
                        yaxis_title="Price (USD)",
                        xaxis=dict(rangeslider=dict(visible=True), type="date")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No price data available for {symbol}. Check Cassandra data or time window.")
            
            # Update raw volume chart
            with raw_volume_chart.container():
                st.subheader(f"Volume Trend for {symbol}")
                if not raw_df.empty:  # Removed the volume.notnull() check to show chart even with zero values
                    fig = px.bar(raw_df, x='timestamp', y='volume', title=f"{symbol} Volume Over Time")
                    fig.update_layout(
                        xaxis_title="Time",
                        yaxis_title="Volume",
                        xaxis=dict(rangeslider=dict(visible=True), type="date")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No data available for {symbol}.")
        
        # Update Aggregated Data tab
        with tab2:
            # Update metrics
            with metrics_container.container():
                st.subheader(f"Key Metrics for {symbol}")
                if not agg_df.empty:
                    latest_agg = agg_df.iloc[-1]
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Latest Avg Price", 
                              f"${latest_agg['avg_price']:.2f}", 
                              f"{latest_agg['price_change']:.4f}" if 'price_change' in latest_agg else None)
                    col2.metric("Price Change", 
                              f"${latest_agg['price_change']:.4f}" if 'price_change' in latest_agg else "N/A")
                    col3.metric("Total Volume", 
                              f"{latest_agg['total_volume']}" if latest_agg['total_volume'] is not None else "N/A")
                else:
                    st.warning(f"No metrics available for {symbol}.")
            
            # Update average price chart
            with agg_price_chart.container():
                st.subheader(f"Average Price Trend for {symbol}")
                if not agg_df.empty:
                    fig = px.line(agg_df, x='window_start', y='avg_price', title=f"{symbol} Average Price Over Time")
                    fig.update_layout(
                        xaxis_title="Time",
                        yaxis_title="Average Price (USD)",
                        xaxis=dict(rangeslider=dict(visible=True), type="date")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No aggregated price data available for {symbol}.")
            
            # Update price change chart
            with price_change_chart.container():
                st.subheader(f"Price Change Trend for {symbol}")
                if not agg_df.empty:
                    fig = px.line(agg_df, x='window_start', y='price_change', title=f"{symbol} Price Change Over Time")
                    fig.update_layout(
                        xaxis_title="Time",
                        yaxis_title="Price Change (USD)",
                        xaxis=dict(rangeslider=dict(visible=True), type="date")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No price change data available for {symbol}.")
            
            # Update total volume chart
            with total_volume_chart.container():
                st.subheader(f"Total Volume Trend for {symbol}")
                if not agg_df.empty:  # Removed the volume.notnull() check
                    fig = px.bar(agg_df, x='window_start', y='total_volume', title=f"{symbol} Total Volume Over Time")
                    fig.update_layout(
                        xaxis_title="Time",
                        yaxis_title="Total Volume",
                        xaxis=dict(rangeslider=dict(visible=True), type="date")
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"No total volume data available for {symbol}.")
        
        # Wait for the specified interval
        time.sleep(refresh_interval)

if __name__ == "__main__":
    main()