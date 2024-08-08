# Install and Set Up Kafka on Amazon EC2 for Streaming Data to S3 with AWS Glue and Athena


![Architecture](https://github.com/TravelXML/KAFKA-PYTHON-AWS-CRAWLER-AMAZON-ATHENA/blob/master/images/Architecture.jpg)


Setting up Apache Kafka on an Amazon EC2 instance can be a powerful way to handle real-time data streaming. This guide will walk you through installing Kafka on an EC2 instance, configuring Zookeeper, producer, and consumer, and streaming logs to an S3 bucket. We'll then use AWS Glue to create a data catalog and run SQL queries with Amazon Athena to analyze the data.

## Prerequisites

- An AWS account
- An EC2 instance (t2.medium recommended)
- SSH access to your EC2 instance
- Basic knowledge of Kafka and AWS services

## Step 1: Launch an EC2 Instance

1. **Create an EC2 Instance:**
   - Type: `t2.medium`
   - OS: `Amazon Linux 2 AMI`
   - Security Group: Allow inbound traffic on ports `22` (SSH), `2181` (Zookeeper), `9092` (Kafka)

2. **SSH into Your EC2 Instance:**
   ```bash
   ssh -i "path/to/your-key.pem" ec2-user@your-ec2-public-ip
   ```

## Step 2: Install Java and Kafka

1. **Install Java:**
   ```bash
   sudo yum install java-1.8.0-openjdk -y
   java -version
   ```

2. **Download and Extract Kafka:**
   ```bash
   wget https://archive.apache.org/dist/kafka/3.3.1/kafka_2.12-3.3.1.tgz
   tar -xvf kafka_2.12-3.3.1.tgz
   cd kafka_2.12-3.3.1
   ```

## Step 3: Start Zookeeper

1. **Start Zookeeper:**
   ```bash
   bin/zookeeper-server-start.sh config/zookeeper.properties
   ```

## Step 4: Start Kafka Server

1. **Open a New SSH Session and Connect to EC2 Instance:**
   ```bash
   ssh -i "path/to/your-key.pem" ec2-user@your-ec2-public-ip
   ```

2. **Start Kafka Server:**
   ```bash
   export KAFKA_HEAP_OPTS="-Xmx256M -Xms128M"
   cd kafka_2.12-3.3.1
   bin/kafka-server-start.sh config/server.properties
   ```

3. **Configure Kafka for Public Access:**
   - Edit `server.properties`:
     ```bash
     sudo nano config/server.properties
     ```
   - Update `ADVERTISED_LISTENERS` to your EC2 instance's public IP:
     ```plaintext
     advertised.listeners=PLAINTEXT://your-ec2-public-ip:9092
     ```

## Step 5: Create a Kafka Topic

1. **Open a New SSH Session and Connect to EC2 Instance:**
   ```bash
   ssh -i "path/to/your-key.pem" ec2-user@your-ec2-public-ip
   ```

2. **Create the Topic:**
   ```bash
   cd kafka_2.12-3.3.1
   bin/kafka-topics.sh --create --topic SAPDEMOTESTING --bootstrap-server your-ec2-public-ip:9092 --replication-factor 1 --partitions 1
   ```

## Step 6: Start Producer

1. **Open a New SSH Session and Connect to EC2 Instance:**
   ```bash
   ssh -i "path/to/your-key.pem" ec2-user@your-ec2-public-ip
   ```

2. **Start Kafka Producer:**
   ```bash
   cd kafka_2.12-3.3.1
   bin/kafka-console-producer.sh --topic SAPDEMOTESTING --bootstrap-server your-ec2-public-ip:9092
   ```

## Step 7: Start Consumer

1. **Open a New SSH Session and Connect to EC2 Instance:**
   ```bash
   ssh -i "path/to/your-key.pem" ec2-user@your-ec2-public-ip
   ```

2. **Start Kafka Consumer:**
   ```bash
   cd kafka_2.12-3.3.1
   bin/kafka-console-consumer.sh --topic SAPDEMOTESTING --bootstrap-server your-ec2-public-ip:9092
   ```

## Step 8: Stream Consumer Logs to S3

1. **Configure Consumer to Stream Logs to S3:**
   - Create an S3 bucket and set up necessary permissions.
   - Use a script or application to redirect consumer logs to the S3 bucket.

## Step 9: Create AWS Glue Data Catalog

1. **Set Up AWS Glue Crawler:**
   - Configure the crawler to crawl your S3 bucket and create a data catalog.

2. **Run the Crawler:**
   - Verify that the crawler has created tables in the Glue Data Catalog.

## Step 10: Query Data with Amazon Athena

1. **Configure Athena to Use Glue Data Catalog:**
   - In the Athena console, set the Glue Data Catalog as the data source.

2. **Run SQL Queries:**
   - Use SQL queries in Athena to analyze the Kafka consumer logs stored in S3.

## Repository Files and Their Explanation

The repository [KAFKA-PYTHON-AWS-CRAWLER-AMAZON-ATHENA](https://github.com/TravelXML/KAFKA-PYTHON-AWS-CRAWLER-AMAZON-ATHENA) contains scripts and configurations that automate the steps mentioned above. Here’s an explanation of the key files and their content:

### 1. `kafka_producer.py`

This script sets up a Kafka producer that sends data to the specified Kafka topic.

```python
from kafka import KafkaProducer
from json import dumps
import time

producer = KafkaProducer(
    bootstrap_servers=['13.201.13.205:9092'],
    value_serializer=lambda x: dumps(x).encode('utf-8')
)

for j in range(999):
    data = {'number': j}
    producer.send('SAPDEMOTESTING', value=data)
    time.sleep(1)
```

### 2. `kafka_consumer_s3.py`

This script sets up a Kafka consumer that reads data from a specified Kafka topic and writes it to an S3 bucket.

```python
from kafka import KafkaConsumer
from json import loads
import boto3

s3 = boto3.client('s3')
consumer = KafkaConsumer(
    'SAPDEMOTESTING',
    bootstrap_servers=['13.201.13.205:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group',
    value_serializer=lambda x: loads(x.decode('utf-8'))
)

for message in consumer:
    message = message.value
    s3.put_object(Bucket='your-s3-bucket', Key=f'{message["number"]}.json', Body=str(message))
```

### 3. `glue_crawler_setup.py`

This script sets up an AWS Glue Crawler that creates a data catalog from the files stored in an S3 bucket.

```python
import boto3

client = boto3.client('glue')

response = client.create_crawler(
    Name='kafka-crawler',
    Role='your-iam-role',
    DatabaseName='kafka-db',
    Description='Crawler for Kafka logs in S3',
    Targets={
        'S3Targets': [
            {
                'Path': 's3://your-s3-bucket/'
            },
        ]
    },
    Schedule='cron(15 * * * ? *)'
)
```

### 4. `athena_query.py`

This script uses AWS Athena to run SQL queries on the data catalog created by AWS Glue.

```python
import boto3

client = boto3.client('athena')

response = client.start_query_execution(
    QueryString='SELECT * FROM kafka_logs',
    QueryExecutionContext={
        'Database': 'kafka-db'
    },
    ResultConfiguration={
        'OutputLocation': 's3://your-athena-query-results/'
    }
)
```

By following these steps and utilizing the provided scripts, you can set up a Kafka environment on an Amazon EC2 instance, stream logs to S3, create a data catalog with AWS Glue, and query the data with Amazon Athena. This setup enables real-time data processing and powerful data analytics capabilities, leveraging the scalability and flexibility of AWS services.
