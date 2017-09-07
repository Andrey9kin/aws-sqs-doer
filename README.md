# aws-sqs-doer
Docker image that listens to AWS SQS, executes received commands and then sends results back to SQS

Make sure to define the following env variables
* AWS_DEFAULT_REGION
* IN_QUEUE_NAME
* OUT_QUEUE_NAME

