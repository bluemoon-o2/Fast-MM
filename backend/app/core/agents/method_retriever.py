import json
import os
from typing import List
from functools import partial
from app.core.prompts import METHOD_CRITIQUE_PROMPT
from app.core.utils.hmml_utils import markdown_to_json_method, parse_llm_output_to_json
from app.core.utils.embedding import EmbeddingScorer
from app.core.llm.llm import LLM
import asyncio

class MethodScorer:

    def __init__(self, score_func, parent_weight=0.5, child_weight=0.5):
        self.parent_weight = parent_weight
        self.child_weight = child_weight
        self.score_func = score_func
        self.leaves = []

    async def process(self, data):
        self.leaves = []
        for root_node in data:
            await self._process_node(root_node, parent_scores=[])
        for root_node in data:
            self._collect_leaves(root_node)
        return self.leaves

    async def _process_node(self, node, parent_scores):
        if 'children' in node:
            children = node.get('children', [])
            if children:
                first_child = children[0]
                if 'method_class' in first_child:
                    input_for_llm = [{"method": child["method_class"], "description": child.get("description", "")} for child in children]
                    # Check if score_func is coroutine
                    if asyncio.iscoroutinefunction(self.score_func) or (isinstance(self.score_func, partial) and asyncio.iscoroutinefunction(self.score_func.func)):
                        llm_result = await self.score_func(input_for_llm)
                    else:
                        llm_result = self.score_func(input_for_llm)
                        
                    for idx, child in enumerate(children):
                        if idx < len(llm_result):
                            child['score'] = llm_result[idx]['score']
                        else:
                            child['score'] = 0
                    current_score = node.get('score')
                    new_parent = parent_scores.copy()
                    if current_score is not None:
                        new_parent.append(current_score)
                    for child in children:
                        await self._process_node(child, new_parent)
                else:
                    input_for_llm = [{"method": child["method"], "description": child.get("description", "")} for child in children]
                    if asyncio.iscoroutinefunction(self.score_func) or (isinstance(self.score_func, partial) and asyncio.iscoroutinefunction(self.score_func.func)):
                        llm_result = await self.score_func(input_for_llm)
                    else:
                        llm_result = self.score_func(input_for_llm)

                    for idx, child in enumerate(children):
                        if idx < len(llm_result):
                            child_score = llm_result[idx]['score']
                        else:
                            child_score = 0
                        child['score'] = child_score
                        parent_avg = sum(parent_scores) / len(parent_scores) if parent_scores else 0
                        final_score = parent_avg * self.parent_weight + child_score * self.child_weight
                        child['final_score'] = final_score

    def _collect_leaves(self, node):
        if 'children' in node:
            for child in node['children']:
                self._collect_leaves(child)
        else:
            if 'final_score' in node:
                self.leaves.append({
                    "method": node["method"],
                    "description": node.get("description", ""),
                    "score": node['final_score']
                })


class MethodRetriever:
    def __init__(self, model: LLM, rag=True):
        self.model = model
        self.rag = rag
        self.embedding_scorer = EmbeddingScorer()
        
        # Path resolution
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # backend/app/core
        data_dir = os.path.join(base_dir, 'data', 'HMML')
        self.json_path = os.path.join(data_dir, 'HMML.json')
        self.md_path = os.path.join(data_dir, 'HMML.md')
        
        if os.path.exists(self.md_path):
            with open(self.md_path, "r", encoding="utf-8") as f:
                self.markdown_text = f.read()
            self.method_tree = markdown_to_json_method(self.markdown_text)
            # Ensure JSON file exists/updated
            if not os.path.exists(self.json_path):
                 try:
                    with open(self.json_path, "w+", encoding="utf-8") as f:
                        json.dump(self.method_tree, f, ensure_ascii=False, indent=4)
                 except Exception as e:
                     print(f"Warning: Could not write HMML.json: {e}")
        else:
            self.markdown_text = ""
            self.method_tree = []
            print(f"Warning: HMML.md not found at {self.md_path}")
        
    async def llm_score_method(self, problem_description: str, methods: List[dict]):
        methods_str = '\n'.join([f"{i+1}. {method['method']} {method.get('description', '')}" for i, method in enumerate(methods)])
        prompt = METHOD_CRITIQUE_PROMPT.format(problem_description=problem_description, methods=methods_str)
        
        response = await self.model.chat(
            history=[{"role": "user", "content": prompt}],
            agent_name="MethodRetriever"
        )
        answer = response.choices[0].message.content
        
        try:
            method_scores = parse_llm_output_to_json(answer).get('methods', [])
        except:
            method_scores = []
            
        method_scores = sorted(method_scores, key=lambda x: x['method_index'])
        for method in method_scores:
            if 'scores' in method:
                method['score'] = sum(method['scores'].values()) / len(method['scores'])
            else:
                method['score'] = 0
        return method_scores

    def format_methods(self, methods: List[dict]):
        return '\n'.join([f"**{method['method']}:** {method['description']}" for method in methods])

    async def retrieve_methods(self, problem_description: str, top_k: int=6, method: str='embedding'):
        if self.rag and self.method_tree:
            if method == 'embedding':
                # Embedding scorer is sync, but we call it in async process method
                score_func = partial(self.embedding_scorer.score_method, problem_description)
            else:
                score_func = partial(self.llm_score_method, problem_description)
                
            scorer = MethodScorer(score_func)
            method_scores = await scorer.process(self.method_tree)
            method_scores.sort(key=lambda x: x['score'], reverse=True)
            return self.format_methods(method_scores[:top_k])
        else:
            return self.markdown_text
