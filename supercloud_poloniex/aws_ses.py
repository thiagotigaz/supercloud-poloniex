import logging

import boto3
from botocore.exceptions import ClientError

# Replace sender@example.com with your "From" address.
# This address must be verified with Amazon SES.
SENDER = "Poloniex Notifier <poloniex@supercloud.com.br>"

# Replace recipient@example.com with a "To" address. If your account
# is still in the sandbox, this address must be verified.
RECIPIENT = "thiagotigaz@gmail.com"

# Specify a configuration set. If you do not want to use a configuration
# set, comment the following variable, and the
# ConfigurationSetName=CONFIGURATION_SET argument below.
# CONFIGURATION_SET = "ConfigSet"

# If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
AWS_REGION = "us-east-1"

# The subject line for the email.
SUBJECT = "Poloniex Status / Order Update"

# The email body for recipients with non-HTML email clients.
BODY_TEXT = ("Poloniex Status / Order Update\r\n"
             "{}"
             )

# The HTML body of the email.
BODY_HTML = """<html>
<head></head>
<body>
  <h1>Poloniex Status / Order Update</h1>
  <p>{}</p>
</body>
</html>
            """

# The character encoding for the email.
CHARSET = "UTF-8"

logger = logging.getLogger(__name__)


class AwsSes(object):
    def __init__(self, key=None, secret=None, region=AWS_REGION):
        # Create a new SES resource and specify a region.
        session = boto3.session.Session(aws_access_key_id=key, aws_secret_access_key=secret, region_name=region)
        self.client = session.client('ses', region_name=region)

    def send_email(self, content=None):
        # Try to send the email.
        try:
            # Provide the contents of the email.
            response = self.client.send_email(
                Destination={
                    'ToAddresses': [
                        RECIPIENT,
                    ],
                },
                Message={
                    'Body': {
                        'Html': {
                            'Charset': CHARSET,
                            'Data': BODY_HTML.format(content),
                        },
                        'Text': {
                            'Charset': CHARSET,
                            'Data': BODY_TEXT.format(content),
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
        # Display an error if something goes wrong.
        except ClientError as ex:
            logger.error(ex)
        else:
            logger.info("Email sent! Message ID:"),
            logger.info(response['ResponseMetadata']['RequestId'])

