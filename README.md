# Startup Diagnosis S2S Agent

An AI-powered voice agent backend designed specifically for conducting automated interviews with startup owners who are students at Link School of Business. This system provides intelligent conversation capabilities to gather insights about startup ventures, business models, challenges, and growth opportunities.

## Purpose

This voice agent serves as an automated interviewer that can:
- Conduct structured interviews with startup founders
- Gather comprehensive business insights and diagnostics
- Analyze startup challenges and opportunities
- Provide intelligent follow-up questions based on responses
- Generate valuable data for business education and mentorship

## Key Features

- **Intelligent Conversation Flow**: AI-driven interview process tailored for startup diagnosis
- **Voice AI Pipeline**: Built on [OpenAI](https://docs.livekit.io/agents/integrations/llm/openai/), [Cartesia](https://docs.livekit.io/agents/integrations/tts/cartesia/), and [Deepgram](https://docs.livekit.io/agents/integrations/llm/deepgram/) for natural voice interactions
- **Contextual Understanding**: Advanced turn detection and speaker recognition for smooth conversations
- **Business-Focused Prompts**: Specialized prompts designed for startup evaluation and diagnosis
- **Real-time Processing**: Live conversation analysis and adaptive questioning
- **Comprehensive Logging**: Detailed session recording and analytics for educational insights

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

You can load the LiveKit environment automatically using the [LiveKit CLI](https://docs.livekit.io/home/cli/cli-setup):

```bash
lk app env -w .env.local
```

## Run the agent

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

This project is production-ready and includes a working `Dockerfile`. To deploy it to LiveKit Cloud or another environment, see the [deploying to production](https://docs.livekit.io/agents/ops/deployment/) guide.

## Kubernetes Deployment on AWS

This project includes Kubernetes manifests for deploying the agent to an Amazon Elastic Kubernetes Service (EKS) cluster.

### Prerequisites

1. **AWS CLI**: Install and configure the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
2. **kubectl**: Install [kubectl](https://kubernetes.io/docs/tasks/tools/) for Kubernetes cluster management
3. **eksctl**: Install [eksctl](https://eksctl.io/installation/) for EKS cluster management
4. **Docker**: Build and push your container image to Amazon Elastic Container Registry (ECR)
5. **EKS Cluster**: Create an EKS cluster with sufficient resources

### Step 1: Create ECR Repository and Push Docker Image

```bash
# Create ECR repository
aws ecr create-repository --repository-name startup-diagnosis-s2s-agent --region us-east-1

# Get login token for ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com

# Build the Docker image
docker build -t startup-diagnosis-s2s-agent:latest .

# Tag the image for ECR
docker tag startup-diagnosis-s2s-agent:latest YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/startup-diagnosis-s2s-agent:latest

# Push to Amazon ECR
docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/startup-diagnosis-s2s-agent:latest
```

### Step 2: Create EKS Cluster

```bash
# Create an EKS cluster using eksctl
eksctl create cluster \
  --name startup-diagnosis-cluster \
  --region us-east-1 \
  --nodegroup-name startup-diagnosis-nodes \
  --node-type m5.large \
  --nodes 3 \
  --nodes-min 1 \
  --nodes-max 10 \
  --managed

# Update kubeconfig to connect to the EKS cluster
aws eks update-kubeconfig --region us-east-1 --name startup-diagnosis-cluster
```

### Step 3: Create Kubernetes Namespace

```bash
kubectl create namespace livekit
```

### Step 4: Configure Secrets

Before deploying, you need to create Kubernetes secrets with your API keys and configuration:

```bash
# Create LiveKit secrets
kubectl create secret generic startup-diagnosis-agent-livekit \
  --from-literal=LIVEKIT_URL="your-livekit-url" \
  --from-literal=LIVEKIT_API_KEY="your-livekit-api-key" \
  --from-literal=LIVEKIT_API_SECRET="your-livekit-api-secret" \
  --namespace=livekit

# Create application secrets
kubectl create secret generic startup-diagnosis-agent-secrets \
  --from-literal=OPENAI_API_KEY="your-openai-api-key" \
  --from-literal=ELEVEN_API_KEY="your-eleven-api-key" \
  --from-literal=ENCRYPTION_KEY="your-encryption-key" \
  --namespace=livekit
```

### Step 5: Update Deployment Manifest

Edit the `agent-manifest.yaml` file and update the image reference:

```yaml
image: YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/startup-diagnosis-s2s-agent:latest
```

### Step 6: Deploy to Kubernetes

```bash
# Apply the deployment manifest
kubectl apply -f agent-manifest.yaml

# Check deployment status
kubectl get deployments -n livekit
kubectl get pods -n livekit

# View logs
kubectl logs -f deployment/startup-diagnosis-agent -n livekit
```

### Step 7: Scaling and Monitoring

```bash
# Scale the deployment
kubectl scale deployment startup-diagnosis-agent --replicas=3 -n livekit

# Monitor resource usage
kubectl top pods -n livekit
kubectl top nodes

# Set up horizontal pod autoscaling
kubectl autoscale deployment startup-diagnosis-agent --cpu-percent=70 --min=1 --max=10 -n livekit
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.