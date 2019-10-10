from aws_cdk import (
    aws_iot as iot,
    core
)
import boto3, botostubs
import boto3_helper

class CdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here

        # create iot thing & policy
        thing = iot.CfnThing(self,
            "MyIoTCDKThing",
            thing_name='myiot-thing'
        )
        print("## Thing Name: %s" % thing.thing_name)

        thing_policy = iot.CfnPolicy(self,
            "MyIoTCDKThingPolicy",
            policy_document=boto3_helper.policyDocument,
            policy_name='myiot-policy'
        )

        # debug - get policy name 
        thing_policy_name = thing_policy.policy_name
        print("## Policy Name: %s" % thing_policy_name)

        # create iot thing certificate
        response = boto3_helper.myiot_create_csr()  # ugh! - gens a new cert for each deployment
        print(response)
        thing_policy_principal_props = iot.CfnPolicyPrincipalAttachmentProps(
            policy_name=thing_policy.policy_name,
            principal=response['certificateArn']
        )
        print("## Principal Cert Arn: %s" % thing_policy_principal_props.principal)

        # attach policy to iot certificate
        iot.CfnPolicyPrincipalAttachment(self,
            'MyIoTCDKPolicyPrincipalAttachment',
            policy_name=thing_policy.policy_name,
            principal=thing_policy_principal_props.principal
        )

        # attach certificate to iot thing
        iot.CfnThingPrincipalAttachment(self,
            'MyIoTCDKThingPrincipalAttachment',
            thing_name=thing.thing_name,
            principal=thing_policy_principal_props.principal
        )