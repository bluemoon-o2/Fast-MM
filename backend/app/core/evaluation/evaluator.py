import os
import json
import re
from typing import Dict, Any
from app.core.llm.llm_factory import LLMFactory
from app.core.evaluation.prompts import (
    generate_problem_analysis_prompt,
    generate_modeling_rigorousness_prompt,
    generate_practicality_and_scientificity_prompt,
    generate_result_and_bias_analysis_prompt
)
from app.utils.log_util import logger

class MMBenchEvaluator:
    def __init__(self, task_id: str):
        self.task_id = task_id
        # Use a "coordinator" or similar high-level model for evaluation
        self.llm_factory = LLMFactory(task_id)
        # Assuming coordinator model is suitable (usually GPT-4 or similar)
        self.llm = self.llm_factory.get_llm_model("coordinator") 

    async def evaluate_solution(self, solution_data: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
        """
        Evaluate the solution using MMBench criteria.
        
        Args:
            solution_data: Dictionary containing task-based solution data.
            output_dir: Directory to save evaluation results.
            
        Returns:
            Dict containing evaluation results.
        """
        logger.info("Starting MMBench evaluation...")
        
        # Ensure output directory exists
        evaluation_dir = os.path.join(output_dir, "evaluation_result")
        os.makedirs(evaluation_dir, exist_ok=True)
        
        results = {}
        
        try:
            # 1. Problem Analysis
            logger.info("Evaluating Problem Analysis...")
            prompt1 = generate_problem_analysis_prompt(solution_data)
            res1 = await self.llm.aask(prompt1)
            results["analysis_evaluation"] = self._parse_evaluation_data(res1)
            
            # 2. Modeling Rigorousness
            logger.info("Evaluating Modeling Rigorousness...")
            prompt2 = generate_modeling_rigorousness_prompt(solution_data)
            res2 = await self.llm.aask(prompt2)
            results["modeling_rigorousness_evaluation"] = self._parse_evaluation_data(res2)
            
            # 3. Practicality and Scientificity
            logger.info("Evaluating Practicality and Scientificity...")
            prompt3 = generate_practicality_and_scientificity_prompt(solution_data)
            res3 = await self.llm.aask(prompt3)
            results["practicality_and_scientificity_evaluation"] = self._parse_evaluation_data(res3)
            
            # 4. Result and Bias Analysis
            logger.info("Evaluating Result and Bias Analysis...")
            prompt4 = generate_result_and_bias_analysis_prompt(solution_data)
            res4 = await self.llm.aask(prompt4)
            results["result_and_bias_analysis_evaluation"] = self._parse_evaluation_data(res4)
            
            # Save results
            json_path = os.path.join(evaluation_dir, "evaluation_results.json")
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
                
            # Save text report
            txt_path = os.path.join(evaluation_dir, "evaluation_results.txt")
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(f"--- Analysis ---\n{res1}\n\n--- Rigorousness ---\n{res2}\n\n--- Practicality ---\n{res3}\n\n--- Result ---\n{res4}")
                
            logger.info(f"Evaluation completed. Results saved to {evaluation_dir}")
            
        except Exception as e:
            logger.error(f"Evaluation failed: {e}")
            results["error"] = str(e)
            
        return results

    def _parse_evaluation_data(self, text: str) -> Dict[str, Any]:
        reason_pattern = r'<reason>\s*(.*?)\s*</reason>'
        score_pattern = r'<score>\s*(\d+)\s*</score>'

        reasons = re.findall(reason_pattern, text, re.DOTALL)
        scores = re.findall(score_pattern, text, re.DOTALL)

        if not reasons or not scores:
            logger.warning("No matches found for reasons or scores in evaluation output.")
            return {"raw_output": text}

        result_dict = {}
        # MMBench evaluator logic: maps analysis_i to (reason, score)
        for i, (reason, score) in enumerate(zip(reasons, scores), 1):
            result_dict[f"criteria_{i}"] = {
                "reason": reason.strip(),
                "score": int(score)
            }

        return result_dict
