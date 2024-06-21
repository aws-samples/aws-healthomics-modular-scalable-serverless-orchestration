import json
import boto3

def lambda_handler(event, context):
    # Extract input parameters
    workflow_file_ref = event['WorkflowFileRef']
    aho_workflow_id = event['AHOWorkflowID']
    output_s3_path = event['OutputS3Path']
    params = {
        "fasta_path": workflow_file_ref
    }


    # Call the AWS HealthOmics start_run API
    aho = boto3.client('omics')
    response = aho.start_run(
        WorkflowId=aho_workflow_id,
        RoleArn="arn:aws:iam::123456789012:role/AHOrole",
        Parameters=params,
        OutputUri=output_s3_path
    )

    return {
        'ExecutionId': response['id']
    }
