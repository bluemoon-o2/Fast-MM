from app.core.agents import WriterAgent, CoderAgent, CoordinatorAgent, ModelerAgent
from app.schemas.request import Problem
from app.schemas.response import SystemMessage
from app.tools.openalex_scholar import OpenAlexScholar
from app.utils.log_util import logger
from app.utils.common_utils import create_work_dir, get_config_template
from app.models.user_output import UserOutput
from app.config.setting import settings
from app.tools.interpreter_factory import create_interpreter
from app.services.redis_manager import redis_manager
from app.tools.notebook_serializer import NotebookSerializer
from app.core.flows import Flows
from app.core.llm.llm_factory import LLMFactory
from app.core.evaluation.evaluator import MMBenchEvaluator
import json
import os


class WorkFlow:
    def __init__(self):
        pass

    def execute(self) -> str:
        # RichPrinter.workflow_start()
        # RichPrinter.workflow_end()
        pass


class FastMMWorkFlow(WorkFlow):
    task_id: str  #
    work_dir: str  # worklow work dir
    ques_count: int = 0  # 问题数量
    questions: dict[str, str | int] = {}  # 问题

    async def execute(self, problem: Problem):
        self.task_id = problem.task_id
        self.work_dir = create_work_dir(self.task_id)

        llm_factory = LLMFactory(self.task_id)
        coordinator_llm, modeler_llm, coder_llm, writer_llm = llm_factory.get_all_llms()

        coordinator_agent = CoordinatorAgent(self.task_id, coordinator_llm)

        await redis_manager.publish_message(
            self.task_id,
            SystemMessage(content="识别用户意图和拆解问题ing..."),
        )

        try:
            coordinator_response = await coordinator_agent.run(problem.ques_all)
            self.questions = coordinator_response.questions
            self.ques_count = coordinator_response.ques_count
        except Exception as e:
            #  非数学建模问题
            logger.error(f"CoordinatorAgent 执行失败: {e}")
            raise e

        await redis_manager.publish_message(
            self.task_id,
            SystemMessage(content="识别用户意图和拆解问题完成,任务转交给建模手"),
        )

        await redis_manager.publish_message(
            self.task_id,
            SystemMessage(content="建模手开始建模ing..."),
        )

        modeler_agent = ModelerAgent(self.task_id, modeler_llm)

        # Removed batch modeling execution
        # modeler_response = await modeler_agent.run(coordinator_response)

        user_output = UserOutput(work_dir=self.work_dir, ques_count=self.ques_count)

        await redis_manager.publish_message(
            self.task_id,
            SystemMessage(content="正在创建代码沙盒环境"),
        )

        notebook_serializer = NotebookSerializer(work_dir=self.work_dir)
        code_interpreter = await create_interpreter(
            kind="local",
            task_id=self.task_id,
            work_dir=self.work_dir,
            notebook_serializer=notebook_serializer,
            timeout=3000,
        )

        scholar = OpenAlexScholar(task_id=self.task_id, email=settings.OPENALEX_EMAIL)

        await redis_manager.publish_message(
            self.task_id,
            SystemMessage(content="创建完成"),
        )

        await redis_manager.publish_message(
            self.task_id,
            SystemMessage(content="初始化代码手"),
        )

        # modeler_agent
        coder_agent = CoderAgent(
            task_id=problem.task_id,
            model=coder_llm,
            work_dir=self.work_dir,
            max_chat_turns=settings.MAX_CHAT_TURNS,
            max_retries=settings.MAX_RETRIES,
            code_interpreter=code_interpreter,
        )

        writer_agent = WriterAgent(
            task_id=problem.task_id,
            model=writer_llm,
            comp_template=problem.comp_template,
            format_output=problem.format_output,
            scholar=scholar,
        )

        flows = Flows(self.questions)

        ################################################ solution steps
        # Interleaved Execution Loop (Modeler -> Coder -> Writer)
        # Sequence: EDA -> Subtasks (DAG Order) -> Sensitivity Analysis
        tasks_sequence = ["eda"] + coordinator_response.order + ["sensitivity_analysis"]
        config_template = get_config_template(problem.comp_template)
        
        context_string = ""
        
        # Initialize evaluation data
        evaluation_data = {
            "background": problem.ques_all, 
            "problem_requirement": "", 
        }
        # Try to parse ques_all if it follows MMBenchLoader format
        if "# Problem Background" in problem.ques_all and "# Problem Requirement" in problem.ques_all:
            parts = problem.ques_all.split("# Problem Requirement")
            evaluation_data["background"] = parts[0].replace("# Problem Background", "").strip()
            evaluation_data["problem_requirement"] = parts[1].strip()

        for task_key in tasks_sequence:
            # 1. Modeling Step
            await redis_manager.publish_message(
                self.task_id,
                SystemMessage(content=f"建模手开始建模 {task_key}"),
            )
            
            # ModelerAgent handles skipping if task_key is not in questions (e.g. EDA might be implicit)
            # For EDA/Sensitivity, if they are not in questions dict, Modeler might return empty.
            # We pass context_string to allow Modeler to see previous results.
            modeler_response = await modeler_agent.run(
                coordinator_response, target_task=task_key, context_solution=context_string
            )
            
            current_model_solution = modeler_response.questions_solution.get(task_key, "")
            
            # Append Model to Context
            if current_model_solution:
                 context_string += f"\n\nTask {task_key} Model:\n{current_model_solution}"
                 await redis_manager.publish_message(
                    self.task_id,
                    SystemMessage(content=f"建模手完成建模 {task_key}", type="success"),
                )

            # 2. Coding Step
            await redis_manager.publish_message(
                self.task_id,
                SystemMessage(content=f"代码手开始求解 {task_key}"),
            )
            
            # Generate Coder Prompt
            if task_key == "eda":
                coder_prompt = flows.get_eda_prompt(current_model_solution)
            elif task_key == "sensitivity_analysis":
                coder_prompt = flows.get_sensitivity_prompt(current_model_solution)
            else:
                coder_prompt = flows.get_task_coder_prompt(
                    task_key, self.questions.get(task_key, ""), current_model_solution
                )

            coder_response = await coder_agent.run(
                prompt=coder_prompt, subtask_title=task_key
            )

            await redis_manager.publish_message(
                self.task_id,
                SystemMessage(content=f"代码手求解成功 {task_key}", type="success"),
            )
            
            # Append Code Output to Context
            try:
                code_output = await code_interpreter.get_code_output(task_key)
                context_string += f"\n\nTask {task_key} Code Output:\n{code_output}"
            except Exception as e:
                logger.warning(f"Failed to get code output for {task_key}: {e}")

            # 3. Writing Step (Incremental)
            writer_prompt = flows.get_writer_prompt(
                task_key, coder_response.coder_response, code_interpreter, config_template
            )

            await redis_manager.publish_message(
                self.task_id,
                SystemMessage(content=f"论文手开始写 {task_key} 部分"),
            )

            ## TODO: 图片引用错误
            writer_response = await writer_agent.run(
                writer_prompt,
                available_images=coder_response.created_images,
                sub_title=task_key,
            )

            await redis_manager.publish_message(
                self.task_id,
                SystemMessage(content=f"论文手完成 {task_key} 部分"),
            )

            user_output.set_res(task_key, writer_response)

            # Collect data for evaluation
            evaluation_data[task_key] = {
                "task_description": self.questions.get(task_key, ""),
                "task_analysis": current_model_solution, # Using model solution as analysis
                "mathematical_modeling_process": current_model_solution, # Using model solution as process
                "subtask_outcome_analysis": writer_response.response_content
            }

        # 关闭沙盒

        await code_interpreter.cleanup()
        logger.info(user_output.get_res())

        ################################################ write steps

        write_flows = flows.get_write_flows(
            user_output, config_template, problem.ques_all
        )
        for key, value in write_flows.items():
            await redis_manager.publish_message(
                self.task_id,
                SystemMessage(content=f"论文手开始写{key}部分"),
            )

            writer_response = await writer_agent.run(prompt=value, sub_title=key)

            user_output.set_res(key, writer_response)

        logger.info(user_output.get_res())

        user_output.save_result()
        
        # Save evaluation data for manual triggering
        eval_data_path = os.path.join(self.work_dir, "evaluation_context.json")
        with open(eval_data_path, "w", encoding="utf-8") as f:
            json.dump(evaluation_data, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Evaluation context saved to {eval_data_path}")
        
        # Trigger MMBench Evaluation
        # try:
        #     evaluator = MMBenchEvaluator(self.task_id)
        #     await redis_manager.publish_message(
        #         self.task_id,
        #         SystemMessage(content="正在进行 MMBench 评估..."),
        #     )
        #     await evaluator.evaluate_solution(evaluation_data, self.work_dir)
        #     await redis_manager.publish_message(
        #         self.task_id,
        #         SystemMessage(content="MMBench 评估完成", type="success"),
        #     )
        # except Exception as e:
        #     logger.error(f"MMBench Evaluation failed: {e}")
