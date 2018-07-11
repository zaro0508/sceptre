import logging

from sceptre.hooks import Hook
from botocore.exceptions import ClientError

class UndefinedExportException(Exception):
    pass

""" Hook for Synapse External Bucket. """
class SynapseExternalBucket(Hook):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    def __init__(self, *args, **kwargs):
        super(SynapseExternalBucket, self).__init__(*args, **kwargs)

    def run(self):
        """
        run is the method called by Sceptre. It should carry out the work
        intended by this hook.
        """
        synapse_username = self.stack_config['parameters']['SynapseUserName']
        owner_email = self.stack_config['parameters']['OwnerEmail']

        synapse_bucket = self.get_synapse_bucket()
        self.create_owner_file(synapse_username, synapse_bucket)
        self.email_owner(owner_email, synapse_bucket)


    def get_synapse_bucket(self):
        client = self.connection_manager.boto_session.client('cloudformation')

        try:
            response = client.list_exports()
            stack_name = self.stack_config['stack_name']
            export_key = self.environment_config['region'] + '-' + stack_name + '-' + 'SynapseExternalBucket'
            export_val = self.find_export_value(response, export_key)
            return export_val
        except ClientError as e:
            self.logger.error(e.response['Error']['Message'])

    def find_export_value(self, json, key):
        for export in json['Exports']:
            if export['Name'] == key:
                return export['Value']

        raise UndefinedExportException("Export not found: " + key)

    def create_owner_file(self, synapse_username, synapse_bucket):
        client = self.connection_manager.boto_session.client('s3')
        filename = 'owner.txt'
        try:
            client.put_object(Body=synapse_username.encode('UTF-8'),
                              Bucket=synapse_bucket,
                              Key=filename)
        except ClientError as e:
            self.logger.error(e.response['Error']['Message'])
        else:
            self.logger.info("Created " + synapse_bucket + "/" + filename),


    def email_owner(self, owner_email, synapse_bucket):
        client = self.connection_manager.boto_session.client('ses')

        # This address must be verified with Amazon SES.
        SENDER = "AWS Scicomp <aws.scicomp@sagebase.org>"

        # if SES is still in the sandbox, this address must be verified.
        RECIPIENT = owner_email

        # Specify a configuration set. If you do not want to use a configuration
        # set, comment the following variable, and the
        # ConfigurationSetName=CONFIGURATION_SET argument below.
        # CONFIGURATION_SET = "ConfigSet"

        # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
        # AWS_REGION = "us-west-2"

        # The subject line for the email.
        SUBJECT = "Scicomp Automated Provisioning"

        # The email body for recipients with non-HTML email clients.
        BODY_TEXT = ("An S3 bucket has been provisioned on your behalf. "
                     "The bucket name is " + synapse_bucket)

        # The HTML body of the email.
        BODY_HTML1 = """<html>
        <head></head>
        <body>
          <p>"""
        BODY_HTML2 = """</p>
        </body>
        </html>
        """

        # The character encoding for the email.
        CHARSET = "UTF-8"

        try:
            #Provide the contents of the email.
            response = client.send_email(
                Destination={
                    'ToAddresses': [
                        RECIPIENT,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML1 + BODY_TEXT + BODY_HTML2,
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT,
                        },
                    },
                    'Subject': {
                        'Charset': CHARSET,
                        'Data': SUBJECT,
                    },
                },
                Source=SENDER,
                # If you are not using a configuration set, comment or delete the
                # following line
                # ConfigurationSetName=CONFIGURATION_SET,
            )
        except ClientError as e:
            self.logger.error(e.response['Error']['Message'])
        else:
            self.logger.info("Email sent! Message ID:" + response['MessageId']),
