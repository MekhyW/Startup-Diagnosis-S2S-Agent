# Register task definition
aws ecs register-task-definition --cli-input-json file://ecs-task-definition.json

# Create ECS cluster
aws ecs create-cluster --cluster-name startup-diagnosis-cluster
aws ecs put-cluster-capacity-providers --cluster startup-diagnosis-cluster --capacity-providers FARGATE --default-capacity-provider-strategy capacityProvider=FARGATE,weight=1 

# Create service
aws ecs create-service \
  --cluster startup-diagnosis-cluster \
  --service-name startup-diagnosis-service \
  --task-definition startup-diagnosis-agent:1 \
  --desired-count 1 \
  --launch-type FARGATE