# Startup Diagnosis S2S Agent

An AI-powered voice agent backend designed specifically for conducting automated interviews with startup owners who are students at Link School of Business. This system provides intelligent conversation capabilities to gather insights about startup ventures, business models, challenges, and growth opportunities.

## Purpose

This voice agent serves as an automated interviewer that can:
- Conduct structured interviews with startup founders
- Gather comprehensive business insights and diagnostics
- Analyze startup challenges and opportunities
- Provide intelligent follow-up questions based on responses
- Generate valuable data for business education and mentorship

This backend is compatible with any [custom web/mobile frontend](https://docs.livekit.io/agents/start/frontend/) or [SIP-based telephony](https://docs.livekit.io/agents/start/telephony/) for flexible deployment options.

Check out the [Frontend Repository](https://github.com/MekhyW/Startup-Diagnosis-S2S-Frontend)

## Dev Setup

Clone the repository and install dependencies:

```console
cd Startup-Diagnosis-S2S-Agent
pip install -r requirements.txt
```

Set up the environment by copying `.env.example` to `.env.local` and filling in the required values:

- `LIVEKIT_URL`: Use [LiveKit Cloud](https://cloud.livekit.io/) or [run your own](https://docs.livekit.io/home/self-hosting/)
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`
- `OPENAI_API_KEY`
- `ELEVEN_API_KEY`
- `ENCRYPTION_KEY`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `S3_BUCKET_NAME`

You can load the LiveKit environment automatically using the [LiveKit CLI](https://docs.livekit.io/home/cli/cli-setup):

```bash
lk app env -w .env.local
```

## Run the agent in development mode

Before your first run, you must download certain models such as [Silero VAD](https://docs.livekit.io/agents/build/turns/vad/) and the [LiveKit turn detector](https://docs.livekit.io/agents/build/turns/turn-detector/):

```console
python src/agent.py download-files
```

### Alternative Methods

To speak to your agent directly in your terminal:

```console
python src/agent.py console
```

For the standard agent (may experience issues on Windows):

```console
python src/agent.py dev
```

In production, use the `start` command:

```console
python src/agent.py start
```

## Tests and evals

This project includes a complete suite of evals, based on the LiveKit Agents [testing & evaluation framework](https://docs.livekit.io/agents/build/testing/). To run them, use `pytest`.

```console
python -m pytest
```

## Startup Interview Configuration

The agent is specifically configured for startup diagnosis interviews with:

- **Custom System Prompts**: Tailored prompts for startup evaluation
- **Business-Focused Questions**: Structured interview flow covering:
  - Business model validation
  - Market analysis and competition
  - Financial planning and projections
  - Team composition and skills
  - Growth strategies and challenges
  - Technology and product development
- **Adaptive Questioning**: AI-driven follow-up questions based on responses
- **Educational Integration**: Designed for Link School of Business curriculum

## Deploying to production

This project is production-ready and includes a working `Dockerfile`. You can deploy it using either AWS Fargate (recommended) or Kubernetes.

## AWS Fargate Deployment (Recommended)

This project includes automated scripts for deploying to AWS ECS with Fargate, providing a serverless container experience.

### Prerequisites

1. **AWS CLI**: Install and configure the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
2. **Docker**: Build and push your container image to Amazon Elastic Container Registry (ECR)
3. **VPC Configuration**: Ensure you have subnets and security groups configured

### Step 1: Create ECR Repository and Push Docker Image

```bash
# Create ECR repository
aws ecr create-repository --repository-name startup-diagnosis-s2s-agent --region us-east-2

# Get login token for ECR
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com

# Build the Docker image
docker build -t startup-diagnosis-s2s-agent:latest .

# Tag the image for ECR
docker tag startup-diagnosis-s2s-agent:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com/startup-diagnosis-s2s-agent:latest

# Push to Amazon ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-2.amazonaws.com/startup-diagnosis-s2s-agent:latest
```

### Step 2: Configure Secrets

Use the provided script to create AWS Secrets Manager secrets. First, edit the values in the script:

```bash
# Edit the script with your actual values
nano bash/create_secrets.bash

# Run the script to create secrets
bash bash/create_secrets.bash
```

### Step 3: Update ECS Task Definition

Edit the `ecs-task-definition.json` file and update:
- Replace `YOUR_ACCOUNT_ID` with your AWS account ID
- Update subnet and security group IDs in the network configuration
- Adjust resource requirements if needed

Make sure your account and the ECS task definition have the necessary permissions to access the secrets!

### Step 4: Deploy to ECS Fargate

Use the provided deployment script:

```bash
# Create required log group and IAM roles
bash bash/create_resources.bash

# Edit the script to update subnet and security group IDs
nano bash/deploy.sh

# Run the deployment script
bash bash/deploy.sh
```

### Step 5: Monitor Deployment

```bash
# Check service status
aws ecs describe-services --cluster startup-diagnosis-cluster --services startup-diagnosis-service

# View logs
aws logs tail /ecs/startup-diagnosis-agent --follow

# Scale the service
aws ecs update-service --cluster startup-diagnosis-cluster --service startup-diagnosis-service --desired-count 3
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.