import json
import boto3

def lambda_handler(event, context):
    # Parse the event object
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Get the metadata file from S3
    s3 = boto3.client('s3')
    metadata_file = s3.get_object(Bucket=bucket, Key=key)
    metadata = json.load(metadata_file['Body'])

    # Extract the flowcell samples and QC workflow information
    flowcell_samples = metadata['flowcellSamples']
    qc_workflow = metadata['qcWorkflow']

    # Start the SFNA Step Functions state machine
    sfn = boto3.client('stepfunctions')
    response = sfn.start_execution(
        stateMachineArn='arn:aws:states:us-east-1:123456789012:stateMachine:SFNA',
        input=json.dumps({
            'flowcellSamples': flowcell_samples,
            'qcWorkflow': qc_workflow
        })
    )

    return {
        'statusCode': 200,
        'body': json.dumps(f'Triggered SFNA state machine execution: {response["executionArn"]}')
    }
