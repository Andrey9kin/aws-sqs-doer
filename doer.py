#!/usr/bin/env python

import boto3
import watchtower
import logging
import subprocess
import os

logger = logging.getLogger('/aws/ec2/slack-do-handler')
logger.addHandler(watchtower.CloudWatchLogHandler())
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

logger.info('Starting slack-do handler...')

def read_env_variable_or_die(variable_name):
    result = os.environ.get(variable_name)
    if result is None:
        raise EnvironmentError('Required env variable {} not set. Exit'.format(variable_name))
    logger.debug('Got env variable: {}={}'.format(variable_name, result))
    return result

def read_message_attribute_or_die(message, attribute_name, attribute_value_type='StringValue'):
    if message.message_attributes is None:
        raise AttributeError('received message has no attributes but attribute {} expected'.format(attribute_name))
    attribute_value = message.message_attributes.get(attribute_name).get(attribute_value_type)
    if not attribute_value:
        raise AttributeError('attribute {} not defined in received message'.format(attribute_name))
    logger.debug('Got attribute {}={}'.format(attribute_name, attribute_value))
    return attribute_value


# Read params from env vars
region = read_env_variable_or_die('AWS_DEFAULT_REGION')
in_queue_name = read_env_variable_or_die('IN_QUEUE_NAME')

# Get queues
sqs = boto3.resource('sqs', region_name=region)
in_queue = sqs.get_queue_by_name(QueueName=in_queue_name)

# Handle messages
while(True):
    for message in in_queue.receive_messages(WaitTimeSeconds=20,
                                        MessageAttributeNames=['All'],
                                        AttributeNames=['All']):
        out = None
        user = None
        channel = None
        status = 0
        logger.debug('Processing message:\n[attributes: {} , message_attributes: {}, body: {}]'.format(message.attributes,
                                                                                                message.message_attributes,
                                                                                                message.body))
        # Read message attributes 
        try:
            user = read_message_attribute_or_die(message, 'user')
        except AttributeError as error:
            logger.error('Message attribute missing. Will not proceed with the message: {}'.format(error.message))
            message.delete()
            continue

        # Run the command
        logger.info('user {} requested execution of the command: {}'.format(user, message.body))
        try:
            out = subprocess.check_output(message.body, shell=True, stderr=subprocess.STDOUT)      
        except subprocess.CalledProcessError as error:
            status = error.returncode
        logger.info('Command return code: {}, output:\n{}'.format(status, out))
        
        # Let the queue know that the message is processed
        message.delete()
