import json
import boto3

def lambda_handler(event, context):
    # Extract input parameter
    execution_id = event['ExecutionId']

    # Call the AWS HealthOmics get_run API
    aho = boto3.client('healthomics')
    response = aho.get_run(id=execution_id)

    return {
        'Status': response['status']
    }
