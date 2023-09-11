import aws_cdk as core
import aws_cdk.assertions as assertions

from aptly_s3_poc.stacks.aptly_s3_poc_stack import AptlyS3PocStack

# example tests. To run these tests, uncomment this file along with the example
# resource in aptly_s3_poc/aptly_s3_poc_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AptlyS3PocStack(app, "aptly-s3-poc")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
