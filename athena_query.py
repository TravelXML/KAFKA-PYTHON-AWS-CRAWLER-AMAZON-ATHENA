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
