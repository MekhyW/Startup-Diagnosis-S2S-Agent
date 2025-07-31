# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create ECS cluster
aws ecs create-cluster --cluster-name startup-diagnosis-cluster --capacity-providers FARGATE

# Create service
aws ecs create-service \
  --cluster startup-diagnosis-cluster \
  --service-name startup-diagnosis-service \
  --task-definition startup-diagnosis-agent:1 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-12345],assignPublicIp=ENABLED}"