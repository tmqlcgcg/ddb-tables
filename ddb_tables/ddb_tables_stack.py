"""
Testing how we can convert an L3 to an L1 construct
"""
import os

from aws_cdk import (
  Stack, CfnTag, RemovalPolicy,
  aws_dynamodb as dynamodb,
  aws_kms as kms,
  aws_s3 as s3,
  aws_lambda as lambda_,
)
from constructs import Construct

class DdbTablesStack(Stack):
  """
  Stack to create a DynamoDB table
  """

  def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
    super().__init__(scope, construct_id, **kwargs)

    # The code that defines your stack goes here

    # Lookup common key
    alias_name: str = "alias/igtdata-ndev01/uswest2/common/0/kek"
    common_key: kms.IAlias = kms.Alias.from_alias_name(self, "myKey", alias_name)


    # Stage 1 code - this simply creates our DDB table with the L3 construct

    l3_table: dynamodb.Table = dynamodb.Table(
      self, "ImportTable",
      partition_key=dynamodb.Attribute(name="id", type=dynamodb.AttributeType.STRING),
      billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption=dynamodb.TableEncryption.CUSTOMER_MANAGED,
      encryption_key=common_key,
      point_in_time_recovery=True
    )

    # Setting the removal policy guarantees that we don't delete the table
    # when we remove it from the stack
    l3_table.apply_removal_policy(RemovalPolicy.RETAIN)

    # Step 2 code - we need a way to reference the table for dependent resources
    # once we remove the L3 table construct from the stack

    # l3_table: iTable = dynamodb.Table.from_table_name(self, "ImportTable", "ImportTable")

    # Step 3 code - this is how we will describe the table in the stack once we
    # have "converted" it to a global table. The process of _actually_ making it
    # into a global table would involve adding an additional element to the
    # replicas[] list, describing the backup region.

    # l1_table: dynamodb.CfnGlobalTable = dynamodb.CfnGlobalTable(
    #   self, "ImportTable",
    #   attribute_definitions=[dynamodb.CfnGlobalTable.AttributeDefinitionProperty(
    #     attribute_name="id",
    #     attribute_type="S"
    #   )],
    #   billing_mode="PAY_PER_REQUEST",
    #   key_schema=[dynamodb.CfnGlobalTable.KeySchemaProperty(
    #     attribute_name="id",
    #     key_type="HASH"
    #   )],
    #   replicas=[dynamodb.CfnGlobalTable.ReplicaSpecificationProperty(
    #     region="us-west-2",
    #     point_in_time_recovery_specification=dynamodb.CfnGlobalTable.PointInTimeRecoverySpecificationProperty(
    #       point_in_time_recovery_enabled=True
    #     ),
    #     sse_specification=dynamodb.CfnGlobalTable.ReplicaSSESpecificationProperty(
    #       kms_master_key_id=common_key.key_id
    #     ),
    #   )],
    #   sse_specification=dynamodb.CfnGlobalTable.SSESpecificationProperty(
    #     sse_enabled=True,
    #     sse_type="KMS"
    #   )
    # )

    # l1_table.apply_removal_policy(RemovalPolicy.RETAIN)

    # This Lambda function code is here to create a referential dependency
    # on our table. It keeps us honest in testing, so that we make sure
    # that we can still reference the table once we've converted to L1

    my_function: lambda_.Function = lambda_.Function(
      self, "MyFunction",
      runtime=lambda_.Runtime.PYTHON_3_8,
      handler="index.handler",
      code=lambda_.Code.from_inline("can't be empty"),
      environment={"TABLE_NAME": l3_table.table_name}
    )

