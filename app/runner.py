import logging

from app.services.data_loader import load_data
from app.llm.llm_interface import LLMService
from app.services.instruction_executor import InstructionExecutor
from app.errors import LLMError, InvalidInstructionError

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
        logger.error(f"LLM error: {e}")
        print(f"Ошибка LLM: {e}")
    except InvalidInstructionError as e:
        logger.error(f"Instruction error: {e}")
        print(f"Ошибка инструкции: {e}")
    except KeyboardInterrupt:
        logger.warning("Прервано пользователем.")
        print("Операция прервана пользователем.")
    except Exception as e:
        logger.exception("Неожиданная ошибка")
        print(f"Критическая ошибка: {e}")