destroy:
	AWS_REGION="us-west-2" cdk destroy -f DdbTablesStack
	for i in $$(aws dynamodb list-tables | jq -r '.TableNames[] | select(. | contains("Import"))') ; do AWS_REGION="us-west-2" aws dynamodb delete-table --table-name $$i ; done

deploy:
	AWS_REGION="us-west-2" cdk deploy DdbTablesStack
	AWS_REGION="us-west-2" aws cloudformation describe-stack-resources --stack-name DdbTablesStack | jq -r '.StackResources[] | .LogicalResourceId+ " "+.ResourceType' | awk '{ printf("%30s %-30s\n", $$1, $$2) }'

changeset:
	AWS_REGION="us-west-2" aws cloudformation create-change-set --stack-name DdbTablesStack --change-set-name ImportChangeSet --change-set-type IMPORT --resources-to-import "[{\"ResourceType\":\"AWS::DynamoDB::GlobalTable\",\"LogicalResourceId\":\"ImportTable\",\"ResourceIdentifier\":{\"TableName\":\"$$(aws dynamodb list-tables | jq -r '.TableNames[] | select (. | contains("ImportTable"))')\"}}]" --template-body file://cdk.out/L1DdbTablesStack.template.json --capabilities CAPABILITY_NAMED_IAM
	echo "Waiting" && sleep 90
	AWS_REGION="us-west-2" aws cloudformation execute-change-set --change-set-name ImportChangeSet --stack-name DdbTablesStack
	AWS_REGION="us-west-2" aws cloudformation describe-stack-drift-detection-status --stack-drift-detection-id $$(AWS_REGION="us-west-2" aws cloudformation detect-stack-drift --stack-name DdbTablesStack | jq -r '.StackDriftDetectionId')
	AWS_REGION="us-west-2" aws cloudformation describe-stack-resources --stack-name DdbTablesStack
	AWS_REGION="us-west-2" aws cloudformation describe-stack-resource-drifts --stack-name DdbTablesStack
