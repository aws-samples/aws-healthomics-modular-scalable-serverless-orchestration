import json
import boto3

def lambda_handler(event, context):
    # Configure SNS client
    sns = boto3.client('sns')

    # SNS topic details
    topic_arn = 'arn:aws:sns:us-east-1:123456789012:WorkflowCompletionNotifications'
    subject = 'AWS HealthOmics Workflows Completed'
    message = """
    Dear Administrator,

    This is to notify you that all AWS HealthOmics workflows for the current batch of flowcell samples and the QC workflow have been completed successfully.

    Please review the analysis results and take any necessary actions.

    Best regards,
    Your Genomics Analysis Pipeline
    """

    # Publish message to SNS topic
    response = sns.publish(
        TopicArn=topic_arn,
        Message=message,
        Subject=subject
    )

    return {
        'statusCode': 200,
        'body': json.dumps('Notification sent successfully')
    }
