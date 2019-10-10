import sys
import boto3, botostubs
from botocore.exceptions import ClientError
import json
import logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


client: botostubs.IoT = boto3.client('iot') # type: botostubs.IOT

# iot policy doc with greengrass support
policyDocument = {
    'Version': '2012-10-17',
    'Statement': [
        {
            'Effect': 'Allow',
            'Action': 'iot:*',
            'Resource': '*'
        },
        {
            'Effect': 'Allow',
            'Action': 'greengrass:*',
            'Resource': '*'
        }
    ]
}

# iot thing greengrass core
core_policyDocument = {
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iot:Publish",
        "iot:Subscribe",
        "iot:Connect",
        "iot:Receive"
      ],
      "Resource": [
        "*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "iot:GetThingShadow",
        "iot:UpdateThingShadow",
        "iot:DeleteThingShadow"
      ],
      "Resource": [
        "*"
      ]
    },
    {
      "Effect": "Allow",
      "Action": [
        "greengrass:*"
      ],
      "Resource": [
        "*"
      ]
    }
  ]
}


def myiot_create_thing(thingName):
    responseData = {}

    # boto3 create thing, create keys and device cert
    client.create_thing(
        thingName=thingName
    )
    response = client.create_keys_and_certificate(
        setAsActive=True
    )
    certId = response['certificateId']
    certArn = response['certificateArn']
    certPem = response['certificatePem']
    privateKey = response['keyPair']['PrivateKey']
    client.create_policy(
        policyName='{}-full-access'.format(thingName),
        policyDocument=json.dumps(policyDocument)
    )
    response = client.attach_policy(
        policyName='{}-full-access'.format(thingName),
        target=certArn
    )
    response = client.attach_thing_principal(
        thingName=thingName,
        principal=certArn,
    )
    logger.info('Created thing: %s, cert: %s and policy: %s' % 
        (thingName, certId, '{}-full-access'.format(thingName)))
    responseData['certificateArn'] = certArn
    responseData['certificateId'] = certId
    responseData['certificatePem'] = certPem
    responseData['privateKey'] = privateKey
    responseData['iotEndpoint'] = client.describe_endpoint(endpointType='iot:Data-ATS')['endpointAddress']
    return responseData


def myiot_create_csr(): # ugh! - would like to avoid this but will require a custom resource
    response = client.create_keys_and_certificate(
        setAsActive=True
    )
    # certId = response['certificateId']
    # certArn = response['certificateArn']
    # certPem = response['certificatePem']
    # privateKey = response['keyPair']['PrivateKey']
    return response