# Create CloudWatch Log Group
aws logs create-log-group --log-group-name /ecs/startup-diagnosis-agent

# Create ecsTaskRole and ecsTaskExecutionRole
aws iam create-role --role-name ecsTaskRole --assume-role-policy-document file://trust-policy.json
aws iam create-role --role-name ecsTaskExecutionRole --assume-role-policy-document file://trust-policy.json
