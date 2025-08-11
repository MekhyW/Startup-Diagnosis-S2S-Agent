import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import jsonschema
from livekit.plugins import openai
from livekit.agents.llm import ChatContext, ChatMessage

logger = logging.getLogger("report_generator")

class ReportGenerator:
    def __init__(self):
        self.llm = openai.LLM(model="gpt-4o")
        self.schema = self._load_schema()
    
    def _load_schema(self) -> Dict[str, Any]:
        """Load the JSON schema for validation"""
        try:
            with open("src/schema/schema.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            return {}
    
    def _get_report_prompt(self, transcription: str) -> str:
        """Generate the prompt for report generation"""
        return f"""
TRANSCRIÇÃO DA ENTREVISTA:
{transcription}

INSTRUÇÕES:
1. Analise cuidadosamente toda a transcrição da entrevista
2. Extraia informações sobre a startup
3. Preencha todos os campos do schema
4. Forneça insights sobre pontos fortes, lacunas críticas e próximos passos

FORMATO DE RESPOSTA:
Retorne APENAS um JSON válido seguindo exatamente o seguinte schema fornecido. Não inclua texto adicional antes ou depois do JSON.
Schema:
{json.dumps(self.schema, indent=2)}
"""
    
    async def generate_report(self, transcription: str, interview_id: str) -> Optional[Dict[str, Any]]:
        """ Generate a structured report from the interview transcription """
        try:
            prompt = self._get_report_prompt(transcription)
            logger.info("Generating report from transcription...")
            chat_ctx = ChatContext()
            chat_ctx.messages.append(ChatMessage.create(text="Você é um consultor especialista em análise de startups e deve gerar um relatório estruturado baseado na entrevista transcrita.", role="system"))
            chat_ctx.messages.append(ChatMessage.create(text=prompt, role="user"))
            stream = self.llm.chat(chat_ctx=chat_ctx, temperature=0.3)
            report_text = ""
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    report_text += chunk.choices[0].delta.content
            try:
                if report_text.startswith("```json"): # Remove any markdown formatting if present
                    report_text = report_text[7:]
                if report_text.endswith("```"):
                    report_text = report_text[:-3]
                report_data = json.loads(report_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.error(f"Response text: {report_text[:500]}...")
            if "metadata" not in report_data:
                report_data["metadata"] = {}
            report_data["metadata"]["interview_id"] = interview_id
            report_data["metadata"]["date"] = datetime.now().isoformat()
            report_data["metadata"]["interviewer"] = "Atena - Startup Diagnosis S2S Agent"
            if self.schema:
                try:
                    jsonschema.validate(report_data, self.schema)
                    logger.info("Report validation successful")
                except jsonschema.ValidationError as e:
                    logger.warning(f"Report validation failed: {e}")
            return report_data
        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            return None
    
    def validate_report(self, report_data: Dict[str, Any]) -> bool:
        """ Validate report data against the schema (True if valid, False otherwise)v"""
        if not self.schema:
            logger.warning("No schema loaded for validation")
            return False
        try:
            jsonschema.validate(report_data, self.schema)
            return True
        except jsonschema.ValidationError as e:
            logger.error(f"Validation error: {e}")
            return False