import logging

from app.errors import LLMError, InvalidInstructionError
from app.llm.llm_interface import LLMService
from app.services.data_loader import load_data
from app.services.instruction_executor import InstructionExecutor

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


def run_process():
    df = load_data()
    llm = LLMService()
    executor = InstructionExecutor()

    try:
        question = input("Введите вопрос: ").strip()
        if not question:
            print("Вопрос не может быть пустым.")
            return

        instruction = llm.get_analysis_instruction(question)
        result = executor.execute(df, instruction)

        print("\nРезультат:\n", result)

    except LLMError as e:
        logger.error("Ошибка LLM: %s", e)
        print("Ошибка LLM:  %s", e)
    except InvalidInstructionError as e:
        logger.error("Ошибка инструкции: %s", e)
        print("Ошибка инструкции: %s", e)
    except KeyboardInterrupt:
        logger.warning("Прервано пользователем.")
        print("Операция прервана пользователем.")
    except Exception as e:
        logger.exception("Критическая ошибка")
        print("Критическая ошибка: %s",e)
