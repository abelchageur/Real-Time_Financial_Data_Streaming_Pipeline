FROM bitnami/spark:3.5

USER root

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
WORKDIR /app
COPY app/ .

# Set the entry command
CMD ["spark-submit", "--packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,com.datastax.spark:spark-cassandra-connector_2.12:3.4.0", "--master", "spark://spark-master:7077", "streaming_job.py"]