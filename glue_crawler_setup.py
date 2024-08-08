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
