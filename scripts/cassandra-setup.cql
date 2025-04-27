-- Create keyspace
CREATE KEYSPACE IF NOT EXISTS fintech
WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor' : 1 };
-- Create raw financial data table
CREATE TABLE IF NOT EXISTS fintech.raw_financial_data (
timestamp TIMESTAMP,
symbol TEXT,
price DECIMAL,
volume BIGINT,
PRIMARY KEY (symbol, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
-- Create aggregated financial data table
CREATE TABLE IF NOT EXISTS fintech.aggregated_financial_data (
window_start TIMESTAMP,
window_end TIMESTAMP,
symbol TEXT,
avg_price DECIMAL,
total_volume BIGINT,
price_change DECIMAL,
PRIMARY KEY ((symbol), window_start)
) WITH CLUSTERING ORDER BY (window_start DESC);