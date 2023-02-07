import aws_cdk as core
import aws_cdk.assertions as assertions

from ddb_tables.ddb_tables_stack import DdbTablesStack

# example tests. To run these tests, uncomment this file along with the example
# resource in ddb_tables/ddb_tables_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = DdbTablesStack(app, "ddb-tables")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
