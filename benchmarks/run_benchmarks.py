import json
import logging

from deepdiff import DeepDiff

from app.llm.llm_interface import LLMService
from app.services.data_loader import load_data
from app.services.instruction_executor import InstructionExecutor

logger = logging.getLogger("benchmarks")
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')


def run_benchmarks():
    df = load_data()
    llm = LLMService()
    executor = InstructionExecutor()

    with open("benchmarks/cases.jsonl", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f if line.strip()]

    ok_instruction = 0
    fail_instruction = 0
    ok_result = 0
    fail_result = 0

    for i, case in enumerate(cases, 1):
        logger.info("[%s] %s", i, case['question'])
        try:
            instruction = llm.get_analysis_instruction(case["question"])

            if "expected_instruction" in case:
                diff = DeepDiff(case["expected_instruction"], instruction, ignore_order=True)
                if diff:
                    logger.error("Инструкция отличается от ожидаемой")
                    logger.info("Ожидалось: %s", json.dumps(case["expected_instruction"], indent=2, ensure_ascii=False))
                    logger.info("Фактически: %s", json.dumps(instruction, indent=2, ensure_ascii=False))
                    logger.info("Diff: %s", diff)
                    fail_instruction += 1
                    continue
                else:
                    ok_instruction += 1

            result = executor.execute(df, instruction)
            result_str = str(result)

            if "expected_result" in case:
                if result_str.strip() == str(case["expected_result"]).strip():
                    logger.info("OK")
                    ok_result += 1
                else:
                    logger.error(
                        "Результат не совпадает. Ожидалось: %s, получено: %s",
                        case['expected_result'], result_str)
                    fail_result += 1
            elif "expected_result_contains" in case:
                if case["expected_result_contains"] in result_str:
                    logger.info("OK")
                    ok_result += 1
                else:
                    logger.error("В результате нет подстроки: '%s'", case['expected_result_contains'])
                    logger.info("Результат: %s", result_str)
                    fail_result += 1
            else:
                logger.warning("Нет заданного критерия сравнения результата.")
                fail_result += 1

        except Exception as e:
            logger.exception("Ошибка %s", e)
            fail_instruction += 1
            fail_result += 1

    logger.info("Инструкции: %s OK / %s FAIL", ok_instruction, fail_instruction)
    logger.info("Результаты:  %s OK / %s FAIL", ok_result, fail_result)

    if ok_instruction + fail_instruction > 0:
        accuracy_instruction = ok_instruction / (ok_instruction + fail_instruction) * 100
        logger.info("Instruction Accuracy: %.2f%%", accuracy_instruction)
    if ok_result + fail_result > 0:
        accuracy_result = ok_result / (ok_result + fail_result) * 100
        logger.info("Execution Accuracy: %.2f%%", accuracy_result)


if __name__ == "__main__":
    run_benchmarks()
