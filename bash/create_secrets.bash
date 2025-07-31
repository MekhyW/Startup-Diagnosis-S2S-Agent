# Create secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name "startup-diagnosis/livekit" \
  --description "LiveKit configuration for startup diagnosis agent" \
  --secret-string '{
    "LIVEKIT_URL":"your-livekit-url",
    "LIVEKIT_API_KEY":"your-livekit-api-key",
    "LIVEKIT_API_SECRET":"your-livekit-api-secret"
  }'

aws secretsmanager create-secret \
  --name "startup-diagnosis/app" \
  --description "Application secrets for startup diagnosis agent" \
  --secret-string '{
    "OPENAI_API_KEY":"your-openai-api-key",
    "ELEVEN_API_KEY":"your-eleven-api-key",
    "ENCRYPTION_KEY":"your-encryption-key"
  }'