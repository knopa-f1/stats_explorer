import json
import logging
from deepdiff import DeepDiff

from app.llm.llm_interface import LLMService
from app.services.instruction_executor import InstructionExecutor
from app.services.data_loader import load_data

logger = logging.getLogger("benchmarks")
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

def run_benchmarks():
    df = load_data()
    llm = LLMService()
    executor = InstructionExecutor()

    with open("benchmarks/cases.jsonl", encoding="utf-8") as f:
        cases = [json.loads(line) for line in f if line.strip()]

    ok = 0
    fail = 0

    for i, case in enumerate(cases, 1):
        logger.info(f"[{i}] {case['question']}")
        try:
            instruction = llm.get_analysis_instruction(case["question"])

            if "expected_instruction" in case:
                diff = DeepDiff(case["expected_instruction"], instruction, ignore_order=True)
                if diff:
                    logger.error("Инструкция отличается от ожидаемой")
                    logger.info("Ожидалось: %s", json.dumps(case["expected_instruction"], indent=2, ensure_ascii=False))
                    logger.info("Фактически: %s", json.dumps(instruction, indent=2, ensure_ascii=False))
                    logger.info("Diff: %s", diff)
                    fail += 1
                    continue

            result = executor.execute(df, instruction)
            result_str = str(result)

            if "expected_result" in case:
                if result_str.strip() == str(case["expected_result"]).strip():
                    logger.info("OK")
                    ok += 1
                else:
                    logger.error(f"Результат не совпадает. Ожидалось: {case['expected_result']}, получено: {result_str}")
                    fail += 1
            elif "expected_result_contains" in case:
                if case["expected_result_contains"] in result_str:
                    logger.info("OK")
                    ok += 1
                else:
                    logger.error(f"В результате нет подстроки: '{case['expected_result_contains']}'")
                    logger.info("Результат: %s", result_str)
                    fail += 1
            else:
                logger.warning("Нет заданного критерия сравнения результата.")
                fail += 1

        except Exception as e:
            logger.exception("Ошибка")
            fail += 1

    print(f"\nИтог: {ok} OK / {fail} FAIL / {ok + fail} Total")

if __name__ == "__main__":
    run_benchmarks()
