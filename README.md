# Orchestrating Multiple AWS HealthOmics Workflows at Scale

This repository is linked from the Blog Post : <LINK>

**Solution Architecture:**

The proposed solution employs a modular and scalable serverless architecture to orchestrate AWS HealthOmics workflows efficiently.
![image](https://github.com/aws-samples/aws-healthomics-modular-scalable-serverless-orchestration/assets/159836702/228c6fb6-20f0-4d9f-a7b8-887f516d5d23)

The key components of this architecture are as follows:
 
1. ‘Main’ S3 Bucket: This S3 bucket hosts the JSON metadata file containing information about the flowcell samples and the QC workflow. A genomics flowcell is a platform used in next-generation sequencing (NGS) technologies, facilitating the controlled movement of reagents and samples through the sequencing process, enabling high-throughput sequencing of DNA molecules.
2. ‘TriggerLambda’: This Lambda function is triggered when the JSON metadata file is uploaded to the Main S3 bucket. It parses the metadata file and starts the ‘SFNA’ Step Functions state machine.
3. ‘SFNA’ Step Functions State Machine: This state machine orchestrates the parallel execution of multiple flowcell sample workflows and the subsequent QC workflow.
   - The ‘ProcessFlowcellSamples’ Map state iterates through the flowcell samples and invokes the ‘SFNB’ state machine for each sample.
   - The 'ProcessQCWorkflow' state invokes the 'SFNB' state machine for the QC workflow.
   - The 'NotifyAdministrator' state is responsible for sending a notification upon completion of all workflows.
4. ‘SFNB’ Step Functions State Machine: This modular state machine encapsulates the logic for executing AWS HealthOmics workflows.
   - The 'TriggerAHO' Lambda function initiates the AWS HealthOmics workflow execution.
   - The 'CheckAHO' Lambda function periodically checks the status of the workflow execution.
   - The state machine handles completion, failure, and notification logic.
5. ‘NotifyAdministrator’ Lambda: This Lambda function sends a notification (e.g., email or SNS message) to the administrator upon successful completion of all workflows.

The diagram illustrates the flow of data and execution between the various components, highlighting the modular and parallelized nature of the solution. The orchestration of multiple workflows is achieved through the SFNA’ state machine, while the ‘SFNB’ state machine provides a reusable component for executing individual AWS HealthOmics workflows.

The orchestration process is initiated by uploading a JSON metadata file to an Amazon S3 bucket. This metadata file serves as the central source of information, containing details about the genomic data samples and the associated workflows. Specifically, the JSON metadata file includes:

1. A list of flowcell samples, each with its unique sample ID and a reference to the corresponding FASTQ file located in another Amazon S3 bucket dedicated to storing sample data. 
2. The AWS HealthOmics workflow ID (AHOSampleWorkflowID) associated with each flowcell sample, indicating the specific genomics analysis workflow to be executed for that sample.
3. A reference to a Quality Control (QC) workflow file stored in a separate Amazon S3 bucket (QCFASTQ), along with the corresponding AWS HealthOmics workflow ID (AHOQCWorkflowID) for the QC workflow.

Upload action triggers an S3 event notification, which invokes a Lambda function named ‘TriggerLambda’. ‘TriggerLambda’ parses the metadata file to extract crucial information about the flowcell samples and the associated QC workflow details.

‘TriggerLambda’ then invokes the primary AWS Step Functions state machine, ‘SFNA’, passing the relevant metadata. ‘SFNA’ orchestrates the parallel execution of multiple workflows by iterating through the flowcell samples listed in the metadata file using a Map state. For each sample, ‘SFNA’ invokes the modular ‘SFNB’ state machine, passing the sample ID, the reference to the FASTQ file in an Amazon S3 bucket, and the associated AWS HealthOmics workflow ID.

‘SFNB’, the modular component, encapsulates the intricate logic for triggering and monitoring AWS HealthOmics workflows. Specifically, ‘SFNB’ employs a Lambda function named ‘TriggerAHO’ to initiate the execution of AWS HealthOmics workflows. ‘TriggerAHO’ invokes the AWS HealthOmics API's 'start_run' command, passing the relevant workflow ID and the reference to the input data file stored in an Amazon S3 bucket.
'
To monitor the workflow's progress, 'SFNB' incorporates a Wait state, which introduces a configurable delay before invoking another Lambda function, 'CheckAHO'. This function periodically queries the AWS HealthOmics API using the 'get_run' command, passing the execution ID obtained from 'TriggerAHO'. Once the 'get_run' command receives a COMPLETED status, 'SFNB' gracefully concludes the workflow orchestration process.

By abstracting the workflow execution details within ‘SFNB’, the architecture enables seamless integration of both pre-built R2R (Ready2Run) workflows and custom private workflows hosted in AWS HealthOmics. This modular design fosters reusability and extensibility, allowing you to easily incorporate new workflows or modify existing ones without disrupting the overall orchestration logic, fostering agility and adaptability in the rapidly evolving field of genomics analysis.

**Sample Code Walkthrough:**


**JSON Metadata file:**
JSON metadata file has two main sections:        
1. 'flowcellSamples': An array of objects, where each object represents a flowcell sample and contains the following properties:
   - 'sampleId': A unique identifier for the sample.
   - 'fastqFileRef': The S3 URI of the FASTQ file for the sample, located in the 'SamplesFASTQ' bucket.
   - 'ahoSampleWorkflowId': The Amazon Resource Name (ARN) or an ID of the AWS HealthOmics workflow to be used for analyzing the sample.
   - 'OutputS3path': The S3 URI of the Output located bucket.
        
2. 'qcWorkflow': An object containing the following properties:
   - 'qcWorkflowFileRef': The S3 URI of the QC workflow file, located in the 'QCFASTQ' bucket.
   - 'ahoQcWorkflowId': The ARN of the AWS HealthOmics workflow to be used for the QC workflow.
   - 'OutputS3path': The S3 URI of the Output located bucket.
        
The AWS HealthOmics Workflow ARN is a unique identifier for the specific genomics analysis workflow to be executed by AWS HealthOmics. However, it's essential to ensure that these values are valid and correspond to the correct workflows in your AWS HealthOmics environment.
        
This JSON metadata file should be hosted in the designated 'Main' S3 bucket that triggers the orchestration process when uploaded or updated. The Lambda function 'TriggerLambda' will parse this metadata file to retrieve the necessary information for initiating the genomics analysis workflows.

**'TriggerLambda' Lambda Function:**

This Lambda function parses the S3 event to retrieve the bucket name and object key (file path) of the uploaded JSON metadata file. It then uses the 'boto3' library to fetch the metadata file from S3, extract the flowcell samples and QC workflow information, and start the 'SFNA' Step Functions state machine by passing the extracted data as input.
Create this AWS Lambda function named 'TriggerLambda' using the Python runtime. 

Next, you need to configure the S3 bucket to trigger the 'TriggerLambda' function when the JSON metadata file is uploaded.
        
1. Open the Amazon S3 console and navigate to the 'Main' S3 bucket where the JSON metadata file will be uploaded.
2. Select the bucket, and then choose the "Properties" tab.
3. Scroll down to the "Event notifications" section and click "Create event notification."
4. In the "Event notifications" window, configure the following settings:
   - Event name: Give a descriptive name for the event (e.g., "TriggerLambdaOnMetadataUpload").
   - Event types: Select "All object create events" or "PUT" (depending on your use case).
   - Destination: Choose "Lambda function."
   - Lambda function: Select the 'TriggerLambda' function from the dropdown list.
5. Click "Save changes" to create the event notification.

With this configuration, whenever the JSON metadata file is uploaded to the 'Main' S3 bucket, an S3 event will trigger the 'TriggerLambda' function. The function will parse the metadata file, extract the necessary information, and start the 'SFNA' Step Functions state machine with the extracted data as input.
        
Note: Ensure that the 'TriggerLambda' function has the necessary permissions to access the S3 bucket and invoke the 'SFNA' Step Functions state machine. You may need to adjust the IAM role and policies associated with the Lambda function accordingly.


**'SFNB' Step Functions State Machine:**

This Step Functions state machine defines the following states:
        
- 'TriggerAHOTask': Invokes the 'TriggerAHO' Lambda function to start the AWS HealthOmics workflow execution.
- 'WaitForCompletion': Waits for 5 minutes (300 seconds) before checking the workflow execution status. This should correspond to the workflow execution length in your AWS HealthOmics environment and the frequency of the task execution information you need.
- 'CheckAHOTask': Invokes the 'CheckAHO' Lambda function to get the status of the AWS HealthOmics workflow execution.
- 'CheckStatusChoice': Evaluates the workflow execution status received from 'CheckAHO'. If the status is "COMPLETED", it transitions to the 'SuccessState'. If the status is "FAILED", it transitions to the 'NotifyFailureTask'. For any other status, it goes back to the 'WaitForCompletion' state.
- 'SuccessState': Indicates a successful completion of the workflow execution.
- 'NotifyFailureTask': Invokes the 'NotifyLambda' function to send a notification in case of a workflow execution failure.


**'TriggerAHO' Lambda Function:**

This Lambda function takes 'WorkflowFileRef', 'AHOWorkflowID' and 'OutputS3Path' as input parameters. It then calls the AWS HealthOmics 'start_run' API, passing them as input along with IAM Role that will be used to run the execution. Ensure to create the IAM role prior to this step. This role should have appropriate execute permissions for AWS HealthOmics workflows. This AWS Lambda function returns the unique run 'id' received from the API response. Every AWS HealthOmics workflow can have different requirements for input and output parameters, depending on the specific genomics analysis task it is designed to perform. You should update the architecture and sample code accordingly. 


**'CheckAHO' Lambda Function:**

This Lambda function takes the 'ExecutionId' as input, which is received from the 'TriggerAHO' Lambda function. It calls the AWS HealthOmics 'get_run' API with the 'ExecutionId' to retrieve the status of the workflow execution. The function returns the 'Status' received from the API response.


**'NotifyLambda' Function:**

This Lambda function is responsible for sending a notification to an Amazon Simple Notification Service (SNS) topic in case of a workflow execution failure. It configures the 'boto3' SNS client and publishes a message to the specified SNS topic ARN. You'll need to replace the 'TopicArn' value with the ARN of your SNS topic.
        
Note: Ensure that you have set up the necessary IAM roles and policies for the Lambda functions to have the required permissions to access AWS HealthOmics, Step Functions, and SNS services.


**'SFNA' Step Functions State Machine:**

Here's how the 'SFNA' state machine works:
        
1. The 'ParallelProcessing' state is a 'Parallel' state that runs two branches concurrently:
   - The first branch is the 'ProcessFlowcellSamples' Map state. This state iterates over the `flowcellSamples` array from the input data. For each flowcell sample, it invokes the `SFNB` Step Functions state machine using the `aws-sdk:stepfunctions:startExecution.sync` integration
   - The second branch is a 'WaitForCompletionMap' Map state, which ensures that the 'WaitForCompletionMap' state completes only after all flowcell samples have been processed successfully.

2. ParallelProcessing:
 - This state transitions to the 'ProcessQCWorkflow' state only after both branches have completed successfully.

3. ProcessFlowcellSamples:
   - This state uses a Map to iterate over the 'flowcellSamples' array from the input data.
   - For each flowcell sample, it invokes the 'SFNB' Step Functions state machine using the 'arn:aws:states:::states:startExecution' integration.
   - The 'InvokeSFNBForSample' state within the Map passes the 'fastqFileRef' and 'ahoSampleWorkflowId' as input to the 'SFNB' state machine.
   - The Map state has a maximum concurrency of 10, meaning it can process up to 10 flowcell samples in parallel.

4. ProcessQCWorkflow:
   - After processing all flowcell samples, this state invokes the 'SFNB' Step Functions state machine.
   - It passes the 'qcWorkflowFileRef' and 'ahoQcWorkflowId' from the input data as input to the 'SFNB' state machine.

5. NotifyAdministrator:
   - This state invokes an AWS Lambda function ('NotifyAdministrator') to send a notification to the administrator upon completion of the QC workflow.

In this state machine, the 'SFNB' state machine is used as a reusable component for executing both the flowcell sample workflows and the QC workflow. The 'SFNA' state machine orchestrates the parallel execution of the flowcell sample workflows using the Map state, and then executes the QC workflow after all sample workflows are complete.
        
Note: Make sure to replace the placeholders ('arn:aws:states:us-east-1:123456789012:stateMachine:SFNB' and 'arn:aws:lambda:us-east-1:123456789012:function:NotifyAdministrator') with the actual ARNs of your 'SFNB' state machine and 'NotifyAdministrator' Lambda function, respectively.


**'NotifyAdministrator' Lambda Function:**

The Lambda function uses the Amazon SNS service to publish a message to a designated SNS topic upon successful completion of all AWS HealthOmics workflows.
        
Make sure to replace the placeholder 'arn:aws:sns:us-east-1:123456789012:WorkflowCompletionNotifications' with the actual ARN of the SNS topic you want to use for sending notifications.
        
Additionally, ensure that you have created the SNS topic and configured the necessary permissions for the Lambda function to publish messages to the topic.
        
When implementing the solution for parallelizing and modularizing genomics analysis workflows using AWS serverless technologies, you may encounter a few limitations or considerations that require tuning or adjustments. Here are a couple of examples:
        
1. Lambda Function Timeout: The Lambda functions used in this solution have a default timeout limit. If you encounter timeout errors during execution, you may need to increase the timeout value for these Lambda functions. This can be done by modifying the timeout configuration in the AWS Lambda console or through the AWS CloudFormation template, if you're using one for deployment.
        
2. AWS HealthOmics StartRun Quota: AWS HealthOmics imposes a default quota limit of 0.1 transactions per second (TPS) for the 'StartRun' API operation. When parallelizing the execution of multiple genomics analysis workflows, you may hit this quota limit, causing throttling or delays in workflow initiation. To overcome this limitation and achieve higher parallelization, you can request a service limit increase for the 'StartRun' quota by reaching out to the AWS Support team. Provide them with your use case and desired TPS limit, and they can assist you in adjusting the quota based on your requirements.

It's highly recommended to thoroughly review the documentation for each service and understand the applicable quotas for your specific use case. If your workload requires higher limits than the default quotas, you should proactively request a quota increase from AWS Support to avoid any potential bottlenecks or service disruptions during the implementation and operation of your workload.



