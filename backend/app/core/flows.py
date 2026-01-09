from app.models.user_output import UserOutput
from app.tools.base_interpreter import BaseCodeInterpreter
from app.core.agents.modeler_agent import ModelerToCoder
from app.core.prompts import TASK_CODING_PROMPT # Import the prompt


class Flows:
    def __init__(self, questions: dict[str, str | int]):
        self.flows: dict[str, dict] = {}
        self.questions: dict[str, str | int] = questions

    def set_flows(self, ques_count: int):
        ques_str = [f"ques{i}" for i in range(1, ques_count + 1)]
        seq = [
            "firstPage",
            "RepeatQues",
            "analysisQues",
            "modelAssumption",
            "symbol",
            "eda",
            *ques_str,
            "sensitivity_analysis",
            "judge",
        ]
        self.flows = {key: {} for key in seq}

    def get_solution_flows(
        self,
        questions: dict[str, str | int],
        modeler_response: ModelerToCoder,
        order: list[str] = None,
    ):
        if order:
            # Use provided order for questions
            questions_quesx_keys = [k for k in order if k.startswith("ques")]
            # Ensure all question keys are present
            all_ques_keys = [
                k
                for k in questions.keys()
                if k.startswith("ques") and k != "ques_count"
            ]
            for k in all_ques_keys:
                if k not in questions_quesx_keys:
                    questions_quesx_keys.append(k)
        else:
            questions_quesx_keys = [
                key
                for key in questions.keys()
                if key.startswith("ques") and key != "ques_count"
            ]

        ques_flow = {
            key: {
                "coder_prompt": self.get_task_coder_prompt(
                    key, questions.get(key, ""), modeler_response.questions_solution.get(key, "")
                ),
            }
            for key in questions_quesx_keys
        }
        flows = {
            "eda": {
                # TODO ： 获取当前路径下的所有数据集
                "coder_prompt": f"""
                        参考建模手给出的解决方案{modeler_response.questions_solution.get("eda", "")}
                        对当前目录下数据进行EDA分析(数据清洗,可视化),清洗后的数据保存当前目录下,**不需要复杂的模型**
                    """,
            },
            **ques_flow,
            "sensitivity_analysis": {
                "coder_prompt": f"""
                        参考建模手给出的解决方案{modeler_response.questions_solution.get("sensitivity_analysis", "")}
                        完成敏感性分析
                    """,
            },
        }
        return flows

    def get_task_coder_prompt(self, task_key: str, task_desc: str, model_solution: str) -> str:
        return TASK_CODING_PROMPT.format(
            data_file="当前目录下的所有数据集文件",
            data_summary="请参考前面的数据分析结果（如果有）",
            variable_description="请读取数据文件获取变量信息",
            dependent_file_prompt="请检查工作目录下其他Agent生成的中间文件（如CSV, JSON, PKL）",
            task_description=task_desc,
            task_analysis="参考下方的建模过程",
            modeling_formulas="参考下方的建模过程",
            modeling_process=model_solution,
            code_template="请编写标准的Python代码，包含必要的注释和可视化",
            user_prompt=""
        )

    def get_eda_prompt(self, model_solution: str) -> str:
        return TASK_CODING_PROMPT.format(
            data_file="当前目录下的所有数据集文件",
            data_summary="请读取数据进行统计描述",
            variable_description="请读取数据文件获取变量信息",
            dependent_file_prompt="无",
            task_description="对当前目录下数据进行EDA分析(数据清洗,可视化),清洗后的数据保存当前目录下",
            task_analysis="参考下方的建模过程",
            modeling_formulas="不需要复杂的模型，主要进行数据探索",
            modeling_process=model_solution,
            code_template="请使用pandas和seaborn/matplotlib进行分析和绘图",
            user_prompt="**不需要复杂的模型**"
        )

    def get_sensitivity_prompt(self, model_solution: str) -> str:
        return TASK_CODING_PROMPT.format(
            data_file="当前目录下的所有数据集文件",
            data_summary="参考前面的分析",
            variable_description="参考前面的分析",
            dependent_file_prompt="请使用之前步骤生成的模型结果或数据",
            task_description="完成敏感性分析，评估模型参数变化对结果的影响",
            task_analysis="参考下方的建模过程",
            modeling_formulas="参考下方的建模过程",
            modeling_process=model_solution,
            code_template="请编写敏感性分析代码，并绘制敏感性分析图表",
            user_prompt=""
        )

    def get_write_flows(
        self, user_output: UserOutput, config_template: dict, bg_ques_all: str
    ):
        model_build_solve = user_output.get_model_build_solve()
        flows = {
            "firstPage": f"""问题背景{bg_ques_all},不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template["firstPage"]}，撰写标题，摘要，关键词""",
            "RepeatQues": f"""问题背景{bg_ques_all},不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template["RepeatQues"]}，撰写问题重述""",
            "analysisQues": f"""问题背景{bg_ques_all},不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template["analysisQues"]}，撰写问题分析""",
            "modelAssumption": f"""问题背景{bg_ques_all},不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template["modelAssumption"]}，撰写模型假设""",
            "symbol": f"""不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template["symbol"]}，撰写符号说明部分""",
            "judge": f"""不需要编写代码,根据模型的求解的信息{model_build_solve}，按照如下模板撰写：{config_template["judge"]}，撰写模型的评价部分""",
        }
        return flows

    def get_writer_prompt(
        self,
        key: str,
        coder_response: str,
        code_interpreter: BaseCodeInterpreter,
        config_template: dict,
    ) -> str:
        """根据不同的key生成对应的writer_prompt

        Args:
            key: 任务类型
            coder_response: 代码执行结果

        Returns:
            str: 生成的writer_prompt
        """
        code_output = code_interpreter.get_code_output(key)

        questions_quesx_keys = self.get_questions_quesx_keys()
        bgc = self.questions["background"]
        quesx_writer_prompt = {
            key: f"""
                    问题背景{bgc},不需要编写代码,代码手得到的结果{coder_response},{code_output},按照如下模板撰写：{config_template[key]}
                """
            for key in questions_quesx_keys
        }

        writer_prompt = {
            "eda": f"""
                    问题背景{bgc},不需要编写代码,代码手得到的结果{coder_response},{code_output},按照如下模板撰写：{config_template["eda"]}
                """,
            **quesx_writer_prompt,
            "sensitivity_analysis": f"""
                    问题背景{bgc},不需要编写代码,代码手得到的结果{coder_response},{code_output},按照如下模板撰写：{config_template["sensitivity_analysis"]}
                """,
        }

        if key in writer_prompt:
            return writer_prompt[key]
        else:
            raise ValueError(f"未知的任务类型: {key}")

    def get_questions_quesx_keys(self) -> list[str]:
        """获取问题1,2...的键"""
        return list(self.get_questions_quesx().keys())

    def get_questions_quesx(self) -> dict[str, str]:
        """获取问题1,2,3...的键值对"""
        # 获取所有以 "ques" 开头的键值对
        questions_quesx = {
            key: value
            for key, value in self.questions.items()
            if key.startswith("ques") and key != "ques_count"
        }
        return questions_quesx

    def get_seq(self, ques_count: int) -> dict[str, str]:
        ques_str = [f"ques{i}" for i in range(1, ques_count + 1)]
        seq = [
            "firstPage",
            "RepeatQues",
            "analysisQues",
            "modelAssumption",
            "symbol",
            "eda",
            *ques_str,
            "sensitivity_analysis",
            "judge",
        ]
        return {key: "" for key in seq}
