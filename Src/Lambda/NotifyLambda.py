import json
import boto3

def lambda_handler(event, context):
    # Configure SNS client
    sns = boto3.client('sns')

    # Send notification to SNS topic
    response = sns.publish(
        TopicArn='arn:aws:sns:us-east-1:123456789012:WorkflowFailureNotifications',
        Message='AWS HealthOmics workflow execution failed.',
        Subject='Workflow Execution Failure'
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Notification sent successfully')
    }
