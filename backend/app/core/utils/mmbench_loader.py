import os
import json
import shutil
from typing import Tuple, List
from app.utils.log_util import logger

class MMBenchLoader:
    def __init__(self, base_path: str = None):
        if base_path is None:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # backend/app/core/utils -> backend/app/core/data/MMBench
            base_path = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "core", "data", "MMBench")
        
        self.base_path = base_path
        self.problem_path = os.path.join(base_path, "problem")
        self.dataset_path = os.path.join(base_path, "dataset")

    def load_problem(self, task_id: str) -> Tuple[str, List[str]]:
        """
        Load problem description and dataset files.
        Returns:
            ques_all (str): Combined background and requirements.
            dataset_files (List[str]): List of dataset file paths.
        """
        json_path = os.path.join(self.problem_path, f"{task_id}.json")
        if not os.path.exists(json_path):
            # Try finding it case-insensitive or just check if user omitted extension?
            # Assuming exact match for now as per MMBench structure
            raise FileNotFoundError(f"Problem file not found: {json_path}")

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
             logger.error(f"Failed to load JSON {json_path}: {e}")
             raise e

        background = data.get('background', '')
        requirement = data.get('problem_requirement', '')
        
        # Format similar to how typical math modeling problems are presented
        ques_all = f"# Problem Background\n{background}\n\n# Problem Requirement\n{requirement}"
        
        # Append dataset description if available
        if 'dataset_description' in data:
            ques_all += "\n\n# Dataset Description\n"
            desc = data['dataset_description']
            if isinstance(desc, dict):
                for k, v in desc.items():
                    ques_all += f"- **{k}**: {v}\n"
            else:
                ques_all += str(desc)
        
        # Append variable description if available
        if 'variable_description' in data:
            ques_all += "\n\n# Variable Description\n"
            var_desc = data['variable_description']
            if isinstance(var_desc, list):
                for item in var_desc:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            ques_all += f"- **{k}**: {v}\n"
                        ques_all += "---\n"
            else:
                 ques_all += str(var_desc)

        # Dataset files
        dataset_dir = os.path.join(self.dataset_path, task_id)
        dataset_files = []
        if os.path.exists(dataset_dir):
            for root, _, files in os.walk(dataset_dir):
                for file in files:
                    dataset_files.append(os.path.join(root, file))
        else:
            logger.warning(f"Dataset directory not found: {dataset_dir}")
        
        return ques_all, dataset_files

    def copy_dataset(self, dataset_files: List[str], work_dir: str):
        for src_path in dataset_files:
            try:
                file_name = os.path.basename(src_path)
                dst_path = os.path.join(work_dir, file_name)
                # Ensure destination doesn't exist or overwrite? Overwrite is fine.
                shutil.copy2(src_path, dst_path)
                logger.info(f"Copied {src_path} to {dst_path}")
            except Exception as e:
                logger.error(f"Failed to copy {src_path} to {work_dir}: {e}")
