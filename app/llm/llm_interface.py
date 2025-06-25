import json
import logging

from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.schema import HumanMessage

from app.config import settings
from app.llm.prompt_template import PROMPT_TEMPLATE
from app.errors import LLMError

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.llm = ChatOpenAI(
            temperature=0,
            model="gpt-4",
            api_key=settings.OPENAI_API_KEY
        )
        self.template = PromptTemplate(
            input_variables=["question"],
            template=PROMPT_TEMPLATE
        )

    def get_analysis_instruction(self, question: str) -> dict:
        prompt = self.template.format(question=question)
        response = self.llm.invoke([HumanMessage(content=prompt)])

        if not response.content or response.content.strip() == 'None':
            logger.error("LLM вернула пустой или недопустимый ответ.")
            raise LLMError("Некорректный вопрос.")

        logger.info("LLM вернула ответ:%s", response.content)
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            logger.error("LLM вернула невалидный JSON", )
            raise LLMError("Ответ LLM не является корректным JSON.")
