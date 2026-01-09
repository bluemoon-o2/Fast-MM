from app.core.agents.agent import Agent
from app.core.llm.llm import LLM
from app.core.prompts import COORDINATOR_PROMPT, TASK_DEPENDENCY_ANALYSIS_PROMPT, DAG_CONSTRUCTION_PROMPT
import json
import re
from collections import deque
from app.utils.log_util import logger
from app.schemas.A2A import CoordinatorToModeler


class CoordinatorAgent(Agent):
    def __init__(
        self,
        task_id: str,
        model: LLM,
        max_chat_turns: int = 30,
    ) -> None:
        super().__init__(task_id, model, max_chat_turns)
        self.system_prompt = COORDINATOR_PROMPT

    def _extract_json(self, text):
        match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
        if match:
            return match.group(1)
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            return text[start:end+1]
        return text.strip()

    def _safe_load_json(self, text):
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            try:
                # Try replacing single quotes with double quotes
                return json.loads(text.replace("'", '"'))
            except:
                raise

    def compute_dag_order(self, graph):
        """
        Compute the topological sorting (computation order) of a DAG.
        :param graph: DAG represented as an adjacency list.
        :return: A list representing the computation order.
        """
        # Calculate indegree
        in_degree = {node: 0 for node in graph}
        for node in graph:
            for neighbor in graph[node]:
                if neighbor not in in_degree:
                    in_degree[neighbor] = 0
                in_degree[neighbor] += 1

        # Find all nodes with in-degree 0
        queue = deque([node for node in in_degree if in_degree[node] == 0])
        order = []

        while queue:
            node = queue.popleft()
            order.append(node)

            if node in graph:
                for neighbor in graph[node]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)

        return order

    async def analyze_dependencies(self, modeling_problem: str, questions: dict):
        # 1. Analyze Dependencies
        task_descriptions = json.dumps(questions, ensure_ascii=False, indent=2)
        tasknum = questions.get("ques_count", 0)
        
        prompt = TASK_DEPENDENCY_ANALYSIS_PROMPT.format(
            tasknum=tasknum,
            modeling_problem=modeling_problem,
            task_descriptions=task_descriptions
        ).strip()
        
        await self.append_chat_history({"role": "user", "content": prompt})
        response = await self.model.chat(history=self.chat_history, agent_name=self.__class__.__name__)
        dependency_analysis = response.choices[0].message.content
        await self.append_chat_history({"role": "assistant", "content": dependency_analysis})
        
        # 2. Construct DAG
        prompt_dag = DAG_CONSTRUCTION_PROMPT.format(
            tasknum=tasknum,
            modeling_problem=modeling_problem,
            task_descriptions=task_descriptions,
            task_dependency_analysis=dependency_analysis
        ).strip()
        
        await self.append_chat_history({"role": "user", "content": prompt_dag})
        
        max_retries = 3
        dag = {}
        for i in range(max_retries):
            try:
                response_dag = await self.model.chat(history=self.chat_history, agent_name=self.__class__.__name__)
                dag_str = self._extract_json(response_dag.choices[0].message.content)
                dag = self._safe_load_json(dag_str)
                break
            except Exception as e:
                logger.warning(f"DAG Construction failed attempt {i+1}: {e}")
                if i == max_retries - 1:
                    logger.error("Failed to construct DAG")
                    # Fallback or empty DAG
                    dag = {}

        # 3. Compute Order
        try:
            if not dag:
                # Fallback to linear order based on question keys
                # Assuming keys are like "ques1", "ques2"...
                order = [k for k in questions.keys() if k.startswith("ques")]
                order.sort()
            else:
                order = self.compute_dag_order(dag)
                # Ensure all question keys are in order, if disconnected
                ques_keys = [k for k in questions.keys() if k.startswith("ques")]
                for k in ques_keys:
                    if k not in order:
                        order.append(k)
        except Exception as e:
            logger.error(f"Topological sort failed: {e}, using default order")
            order = [k for k in questions.keys() if k.startswith("ques")]
            order.sort()

        return dag, order

    async def run(self, ques_all: str) -> CoordinatorToModeler:
        """用户输入问题 使用LLM 格式化 questions"""
        await self.append_chat_history(
            {"role": "system", "content": self.system_prompt}
        )
        await self.append_chat_history({"role": "user", "content": ques_all})
        max_retries = 3
        attempt = 0
        questions = {}
        
        while attempt <= max_retries:
            try:
                response = await self.model.chat(
                    history=self.chat_history,
                    agent_name=self.__class__.__name__,
                )
                json_str = response.choices[0].message.content

                # 清理 JSON 字符串
                json_str = self._extract_json(json_str)
                json_str = re.sub(r"[\x00-\x1F\x7F]", "", json_str)

                if not json_str:
                    raise ValueError("返回的 JSON 字符串为空")

                questions = json.loads(json_str)
                ques_count = questions["ques_count"]
                logger.info(f"questions:{questions}")
                
                # Analyze Dependencies and Construct DAG
                dag, order = await self.analyze_dependencies(ques_all, questions)
                
                return CoordinatorToModeler(
                    questions=questions, 
                    ques_count=ques_count,
                    dag=dag,
                    order=order
                )
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                attempt += 1
                logger.warning(f"解析失败 (尝试 {attempt}/{max_retries}): {str(e)}")
                
                if attempt > max_retries:
                    logger.error(f"超过最大重试次数，放弃解析")
                    raise RuntimeError(f"无法解析模型响应: {str(e)}")
                    
                # 添加错误反馈提示
                error_prompt = f"⚠️ 上次响应格式错误: {str(e)}。请严格输出JSON格式"
                await self.append_chat_history({
                    "role": "system", 
                    "content": self.system_prompt + "\n" + error_prompt
                })
        
        # 永远不会执行到这里
        raise RuntimeError("意外的流程终止")
