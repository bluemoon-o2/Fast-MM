from app.core.agents.agent import Agent
from app.core.llm.llm import LLM
from app.core.prompts import (
    MODELER_PROMPT,
    PROBLEM_ANALYSIS_PROMPT,
    PROBLEM_ANALYSIS_CRITIQUE_PROMPT,
    PROBLEM_ANALYSIS_IMPROVEMENT_PROMPT,
    PROBLEM_MODELING_PROMPT,
    PROBLEM_MODELING_CRITIQUE_PROMPT,
    PROBLEM_MODELING_IMPROVEMENT_PROMPT,
)
from app.schemas.A2A import CoordinatorToModeler, ModelerToCoder
from app.utils.log_util import logger
from app.core.agents.method_retriever import MethodRetriever


class ModelerAgent(Agent):  # 继承自Agent类
    def __init__(
        self,
        task_id: str,
        model: LLM,
        max_chat_turns: int = 30,  # 添加最大对话轮次限制
    ) -> None:
        super().__init__(task_id, model, max_chat_turns)
        self.system_prompt = "You are an expert mathematical modeler."
        self.retriever = MethodRetriever(model)

    async def run(
        self,
        coordinator_to_modeler: CoordinatorToModeler,
        target_task: str = None,
        context_solution: str = "",
    ) -> ModelerToCoder:
        results = {}

        # Determine tasks to process
        tasks_to_process = (
            [target_task] if target_task else coordinator_to_modeler.order
        )

        # Iterate over questions based on order
        for task_key in tasks_to_process:
            if task_key not in coordinator_to_modeler.questions:
                continue

            task_desc = coordinator_to_modeler.questions[task_key]
            logger.info(f"Processing task: {task_key}")

            # 1. Analysis
            analysis = await self._perform_analysis(task_desc)

            # 2. Method Retrieval
            # Use 'llm' method for better accuracy as per MMAgent design
            methods_str = await self.retriever.retrieve_methods(task_desc, method='llm')

            # 3. Modeling
            solution = await self._perform_modeling(
                task_desc, analysis, methods_str, context_solution
            )

            results[task_key] = solution
            # Update context for next internal iteration (if batch mode)
            context_solution += f"\n\nTask {task_key} Solution:\n{solution}"

        return ModelerToCoder(questions_solution=results)

    async def _perform_analysis(self, problem: str) -> str:
        # 1. Analysis
        prompt = PROBLEM_ANALYSIS_PROMPT.format(
            modeling_problem=problem, user_prompt=""
        )
        analysis = await self._simple_chat(prompt)

        # 2. Critique
        critique_prompt = PROBLEM_ANALYSIS_CRITIQUE_PROMPT.format(
            modeling_problem=problem, problem_analysis=analysis
        )
        critique = await self._simple_chat(critique_prompt)

        # 3. Improvement
        improve_prompt = PROBLEM_ANALYSIS_IMPROVEMENT_PROMPT.format(
            modeling_problem=problem,
            problem_analysis=analysis,
            problem_analysis_critique=critique,
            user_prompt="",
        )
        improved_analysis = await self._simple_chat(improve_prompt)

        return improved_analysis

    async def _perform_modeling(
        self, problem: str, analysis: str, methods: str, context: str
    ) -> str:
        # Add context if necessary
        full_problem = (
            f"{problem}\n\nContext from previous tasks:\n{context}"
            if context
            else problem
        )

        # Append methods to analysis
        analysis_with_methods = f"{analysis}\n\nSuggested Methods:\n{methods}"

        # 1. Modeling
        prompt = PROBLEM_MODELING_PROMPT.format(
            modeling_problem=full_problem,
            problem_analysis=analysis_with_methods,
            user_prompt="",
        )
        solution = await self._simple_chat(prompt)

        # 2. Critique
        critique_prompt = PROBLEM_MODELING_CRITIQUE_PROMPT.format(
            modeling_problem=full_problem,
            problem_analysis=analysis,
            modeling_solution=solution,
        )
        critique = await self._simple_chat(critique_prompt)

        # 3. Improvement
        improve_prompt = PROBLEM_MODELING_IMPROVEMENT_PROMPT.format(
            modeling_problem=full_problem,
            problem_analysis=analysis,
            modeling_solution=solution,
            modeling_solution_critique=critique,
            user_prompt="",
        )
        improved_solution = await self._simple_chat(improve_prompt)

        return improved_solution

    async def _simple_chat(self, content: str) -> str:
        messages = [{"role": "user", "content": content}]
        response = await self.model.chat(
            history=messages, agent_name=self.__class__.__name__
        )
        return response.choices[0].message.content
