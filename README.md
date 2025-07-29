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

## Frontend & Telephony

Get started quickly with our pre-built frontend starter apps, or add telephony support:

| Platform | Link | Description |
|----------|----------|-------------|
| **Web** | [`livekit-examples/agent-starter-react`](https://github.com/livekit-examples/agent-starter-react) | Web voice AI assistant with React & Next.js |
| **iOS/macOS** | [`livekit-examples/agent-starter-swift`](https://github.com/livekit-examples/agent-starter-swift) | Native iOS, macOS, and visionOS voice AI assistant |
| **Flutter** | [`livekit-examples/agent-starter-flutter`](https://github.com/livekit-examples/agent-starter-flutter) | Cross-platform voice AI assistant app |
| **React Native** | [`livekit-examples/voice-assistant-react-native`](https://github.com/livekit-examples/voice-assistant-react-native) | Native mobile app with React Native & Expo |
| **Android** | [`livekit-examples/agent-starter-android`](https://github.com/livekit-examples/agent-starter-android) | Native Android app with Kotlin & Jetpack Compose |
| **Web Embed** | [`livekit-examples/agent-starter-embed`](https://github.com/livekit-examples/agent-starter-embed) | Voice AI widget for any website |
| **Telephony** | [📚 Documentation](https://docs.livekit.io/agents/start/telephony/) | Add inbound or outbound calling to your agent |

For advanced customization, see the [complete frontend guide](https://docs.livekit.io/agents/start/frontend/).

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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.