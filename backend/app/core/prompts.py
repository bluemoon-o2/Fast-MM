from app.schemas.enums import FormatOutPut
import platform

MEMORY_COMPRESSION_PROMPT = """
你是一个专业的对话总结助手。你的任务是将当前的对话历史压缩成一份简明扼要的摘要，以便后续模型能够无缝接手任务。

请务必包含以下信息：
1. **已完成事项**：简要说明已经完成了哪些建模步骤或代码实现。
2. **当前状态**：当前正在进行哪个环节（如：正在调试代码、正在推导公式）。
3. **关键数据/结论**：保留重要的数值结果、公式形式或文件路径（不要丢失上下文中的关键变量）。
4. **下一步计划**：根据当前进度，接下来的即时任务是什么。
5. **用户约束**：用户特别强调的要求或限制条件。

格式要求：
- 使用结构化的 Markdown 列表。
- 保持客观，不要通过“用户说”、“我说”来流水账记录，而是总结事实。
- 篇幅控制在 300 字以内。
"""

FORMAT_QUESTIONS_PROMPT = """
用户将提供给你一段题目信息，**请你不要更改题目信息，完整将用户输入的内容**，以 JSON 的形式输出，输出的 JSON 需遵守以下的格式：

```json
{
  "title": <题目标题>      
  "background": <题目背景，用户输入的一切不在title，ques1，ques2，ques3...中的内容都视为问题背景信息background>,
  "ques_count": <问题数量,number,int>,
  "ques1": <问题1>,
  "ques2": <问题2>,
  "ques3": <问题3,用户输入的存在多少问题，就输出多少问题ques1,ques2,ques3...以此类推>,
}
```
"""


COORDINATOR_PROMPT = f"""
    判断用户输入的信息是否是数学建模问题
    如果是关于数学建模的，你将按照如下要求,整理问题格式
    {FORMAT_QUESTIONS_PROMPT}
    如果不是关于数学建模的，你将按照如下要求
    你会拒绝用户请求，输出一段拒绝的文字
"""


TASK_DEPENDENCY_ANALYSIS_PROMPT = """
Understanding the dependencies among different tasks in a mathematical modeling process is crucial for ensuring a coherent, logically structured, and efficient solution. Given a mathematical modeling problem and its solution decomposition into {tasknum} subtasks, analyze the interdependencies among these subtasks.  

## Input Information:
- **Mathematical Modeling Problem:** {modeling_problem}
- **Decomposed Tasks:** {task_descriptions}

## Task Dependency Analysis Instructions:
1. **Identify Task Dependencies:** For each task, determine which preceding tasks provide necessary input, data, or conditions for its execution. Clearly outline how earlier tasks influence or constrain later ones.
2. **Describe Dependency Types:** Specify the nature of the dependencies between tasks. This includes:
   - *Data Dependency:* When one task produces outputs that are required as inputs for another task.
   - *Methodological Dependency:* When a later task builds upon a theoretical framework, assumptions, or models established by an earlier task.
   - *Computational Dependency:* When a task requires prior computations or optimizations to be completed before proceeding.
   - *Structural Dependency:* When a task is logically required to be completed before another due to hierarchical or sequential constraints.
3. **Ensure Completeness:** Verify that all tasks in the decomposition are accounted for in the dependency analysis and that no essential dependencies are missing.

## Output Format:  
Respond as comprehensively and in as much detail as possible. Do not format your response in Markdown. Using plain text, without any Markdown formatting or syntax. Written as {tasknum} cohesive paragraphs, each paragraph is a dependency analysis of a task.

The response should be comprehensive and written in a clear, well-structured format without bullet points, ensuring a logical flow of dependency relationships and their implications.
"""


DAG_CONSTRUCTION_PROMPT = """
A well-structured Directed Acyclic Graph (DAG) is essential for visualizing and optimizing the dependencies between different tasks in a mathematical modeling process. Given a problem and its solution decomposition into {tasknum} subtasks, construct a DAG that accurately represents the dependency relationships among these tasks. The DAG should capture all necessary dependencies while ensuring that no cycles exist in the structure.  

## Input Information:
- **Mathematical Modeling Problem:** {modeling_problem}
- **Decomposed Tasks:** {task_descriptions}
- **Dependency Analysis:** {task_dependency_analysis}

## Output Format (STRICT REQUIREMENT):
You **MUST** return a valid JSON-formatted adjacency list **without** any additional text, explanations, or comments. **Only** output the JSON object. Do not use Markdown code blocks.

### JSON Format (Strictly Follow This Format):
{{
  "task_ID": [dependent_IDs],
  ...
}}

## Example Output: 
{{
"1": [],
"2": ["1"],
"3": ["1"],
"4": ["2", "3"]
}}
"""


# TODO: 设计成一个类？
MODELER_PROMPT = """
role：你是一名数学建模经验丰富,善于思考的建模手，负责建模部分。
task：你需要根据用户要求和数据对应每个问题建立数学模型求解问题,以及可视化方案
skill：熟练掌握各种数学建模的模型和思路
output：数学建模的思路和使用到的模型
attention：不需要给出代码，只需要给出思路和模型

# 输出规范
## 字段约束

以 JSON 的形式输出输出的 JSON,需遵守以下的格式：
```json
{
  "eda": <数据分析EDA方案，可视化方案>,
  "ques1": <问题1的建模思路和模型方案，可视化方案>,
  "quesN": <问题N的建模思路和模型方案，可视化方案>,
  "sensitivity_analysis": <敏感性分析方案，可视化方案>,
}
```
* 根据实际问题数量动态生成ques1,ques2...quesN

## 输出约束
- json key 只能是上面的: eda,ques1,quesN,sensitivity_analysis
- 严格保持单层JSON结构
- 键值对值类型：字符串
- 禁止嵌套/多级JSON
"""


# Modeler Prompts (Unified from MMAgent)
PROBLEM_ANALYSIS_PROMPT = """\
# Mathematical Modeling Problem:
{modeling_problem}

---

You are tasked with analyzing a mathematical modeling problem with a focus on the underlying concepts, logical reasoning, and assumptions that inform the solution process. Begin by considering the nature of the problem in its broader context. What are the primary objectives of the model, and how do they shape the way you approach the task? Think critically about the assumptions that may be inherently embedded in the problem. What implicit beliefs or constraints have been set up, either explicitly or implicitly, within the problem’s description? Reflect on how these assumptions might influence the interpretation and application of any potential solutions. 

Dive deeper into the relationships and interdependencies between the different components of the problem. What are the potential hidden complexities that may arise from these interconnections? Are there any conflicts or tensions between different aspects of the problem that need to be resolved? Explore how these interdependencies might lead to unforeseen challenges and require revisiting initial assumptions or redefining the parameters of the task. 

Consider how the complexity of the problem may evolve across different scales or over time. Are there time-dependent factors or long-term consequences that should be accounted for, especially in terms of the stability or sustainability of the model’s outcomes? Think about how the model’s behavior might change under different scenarios, such as variations in input or changes in external conditions. Reflect on whether any simplifications or idealizations in the problem might inadvertently obscure key dynamics that are crucial for an accurate representation.

In your analysis, also give attention to possible alternative perspectives on the problem. Are there different ways to frame the issue that could lead to distinct modeling approaches or solution strategies? How would those alternative perspectives impact the overall approach? Additionally, evaluate the potential risks or uncertainties inherent in the problem, especially when it comes to choosing between competing modeling approaches. Consider how the outcomes might vary depending on the choices you make in constructing the model, and how you would manage such trade-offs.

Finally, reflect on the dynamic nature of the modeling process itself. How might your understanding of the problem evolve as you continue to explore its intricacies? Ensure that your thought process remains flexible, with a readiness to revise earlier conclusions as new insights emerge. The goal is to maintain a reflective, iterative analysis that adapts to deeper understandings of the task at hand, rather than pursuing a fixed or rigid approach.

{user_prompt}

Respond as comprehensively and in as much detail as possible. Do not format your response in Markdown. Using plain text, without any Markdown formatting or syntax. Written as one or more cohesive paragraphs. Avoid structuring your answer in bullet points or numbered lists.
"""


PROBLEM_ANALYSIS_CRITIQUE_PROMPT = """\
# Mathematical Modeling Problem:
{modeling_problem}

# Problem Analysis:
{problem_analysis}

---

Critically examine the analysis results of the given mathematical modeling problem, focusing on the following aspects:

1. Depth of Thinking: Evaluate whether the analysis demonstrates a comprehensive understanding of the underlying problem. Does it go beyond surface-level observations? Are the assumptions, limitations, and potential implications of the results carefully considered? Assess whether the analysis adequately addresses both the broader context and specific intricacies of the problem.
2. Novelty of Perspective: Analyze the originality of the approach taken in the analysis. Does it introduce new insights or merely rehash well-established methods or solutions? Are alternative perspectives or unconventional techniques explored, or is the analysis constrained by a narrow set of assumptions or typical approaches?
3. Critical Evaluation of Results: Consider the extent to which the analysis critically engages with the results. Are the conclusions drawn from the analysis well-supported by the mathematical findings, or do they overlook key uncertainties or counterexamples? Does the analysis acknowledge potential contradictions or ambiguities in the data?
4. Rigor and Precision: Assess the level of rigor applied in the analysis. Are the steps logically consistent and mathematically sound, or are there overlooked errors, gaps, or assumptions that undermine the conclusions? Does the analysis exhibit a clear, methodical approach, or is it characterized by vague reasoning and imprecision?
5. Contextual Awareness: Evaluate how well the analysis situates itself within the broader landscape of mathematical modeling in this area. Does it consider previous work or developments in the field? Is there any indication of awareness of real-world implications, practical constraints, or ethical concerns, if applicable?

Critique the analysis without offering any constructive suggestions—your focus should solely be on highlighting weaknesses, gaps, and limitations within the approach and its execution.
"""


PROBLEM_ANALYSIS_IMPROVEMENT_PROMPT = """\
# Mathematical Modeling Problem:
{modeling_problem}

# Problem Analysis:
{problem_analysis}

# Problem Analysis Critique:
{problem_analysis_critique}

---

Refine and improve the existing problem analysis based on the critique provided to generate insightful analysis. 

Provide the improved version directly. DO NOT mention any previous analysis content and deficiencies in the improved analysis. Just refer to the above critical suggestions and directly give the new improved analysis.
{user_prompt}
Respond as comprehensively and in as much detail as possible. Do not format your response in Markdown. Using plain text, without any Markdown formatting or syntax. Written as one or more cohesive paragraphs. Avoid structuring your answer in bullet points or numbered lists.

IMPROVED PROBLEM ANALYSIS:
"""


METHOD_CRITIQUE_PROMPT = """\
## Problem Description

{problem_description}

## Method List

{methods}

## Evaluation Task

Evaluate each method based on the following dimensions. For each dimension, consider the associated criteria and assign a score from 1 (poor) to 5 (excellent). 

## Criteria Dimensions

**1. Assumptions:** Whether the foundational mathematical assumptions align with the intrinsic characteristics of the problem.  
For instance, linear regression assumes linear relationships but fails to capture nonlinear dynamics (e.g., exponential growth). Similarly, deterministic models (e.g., ordinary differential equations) may overlook critical uncertainties in inherently stochastic systems (e.g., financial markets or biological processes). Misaligned assumptions risk oversimplification or systematic bias.

**2. Structure:** The mathematical framework’s ability to mirror the problem’s inherent logic, hierarchy, or spatiotemporal relationships.  
Network-based problems (e.g., traffic flow or social interactions) demand graph theory or network flow models, while hierarchical systems (e.g., ecological food webs) may require multi-stage or layered modeling. A mismatch here—such as using static equations for time-dependent phenomena—renders the model structurally inadequate.

**3. Variables:** Compatibility between the model’s mathematical tools and the variable types in the problem (continuous, discrete, categorical, stochastic, etc.).  
For example, logistic regression or decision trees suit categorical outcomes, while partial differential equations better model spatially continuous systems. High-dimensional sparse data (e.g., genomics) may necessitate dimensionality reduction (PCA) or sparse optimization, whereas rigid variable handling leads to inefficiency or inaccuracy.

**4. Dynamics:** Alignment of the model’s temporal or dynamic properties with the problem’s evolutionary behavior.  
Short-term forecasting might use static models (e.g., linear regression), but long-term ecological or economic systems require dynamic frameworks (e.g., differential equations or agent-based models). Ignoring time delays (e.g., policy impacts in economics) or feedback loops often invalidates predictions.

**5. Solvability:** The existence and practicality of solutions under real-world constraints.  
High-dimensional non-convex optimization problems (e.g., neural network training) may rely on heuristic algorithms (genetic algorithms) rather than exact solutions. Similarly, NP-hard problems (e.g., traveling salesman) demand approximations to balance computational feasibility and precision. Overly complex models risk theoretical elegance without actionable results.

## Instructions
1. For each method in the Method List, score its performance on **all** evaluation dimensions.
2. Return results in JSON format, including the method index and scores for each dimension.

## Output Example (Only return the JSON output, no other text)
```json
{{
  "methods": [
    {{
      "method_index": 1,
      "scores": {{
        "Assumptions": 4,
        "Structure": 3,
        // Include other dimensions here
      }}
    }},
    // Include other methods here
  ]
}}
```

## Required Output
Provide the JSON output below:
```json
"""


PROBLEM_MODELING_PROMPT = """\
# Mathematical Modeling Problem:
{modeling_problem}

# Problem Analysis:
{problem_analysis}

---

You are tasked with designing an innovative mathematical model to address the given problem. Begin by proposing a comprehensive model that integrates both theoretical and practical considerations, ensuring that the formulation is aligned with the problem's core objectives. This should include a clear set of assumptions that underpin the model, which may involve simplifications, approximations, or idealizations necessary to make the problem tractable, yet still retain fidelity to the real-world phenomena you aim to represent. Clearly define the variables, parameters, and constraints that will shape the mathematical formulation. 

Next, develop the key equations and relationships that will govern the model. Pay attention to the interdependencies between the various components of the system. These could involve differential equations, algebraic relations, optimization criteria, or probabilistic models, depending on the nature of the problem. Be sure to consider how different aspects of the model might interact, and whether feedback loops or non-linearities should be incorporated. Explore potential novel formulations or extensions of existing models that could offer new insights into the problem's dynamics. If applicable, propose advanced methods such as multi-scale modeling, agent-based simulations, or data-driven approaches like machine learning to improve the model’s adaptability or accuracy.

Once the model structure is established, outline a clear strategy for solving it. This may involve analytical techniques such as closed-form solutions or approximations, numerical methods like finite element analysis or Monte Carlo simulations, or optimization algorithms for parameter estimation. Be explicit about the computational resources required and the level of precision expected. If the model is complex or high-dimensional, suggest ways to reduce the computational burden, such as dimensionality reduction, surrogate models, or parallelization techniques. 

Additionally, consider how the model might evolve over time or under different conditions. Would the model require recalibration or adaptation in the face of changing circumstances? If applicable, provide strategies for sensitivity analysis to assess how the model responds to changes in its assumptions or parameters. Reflect on how the model’s predictions can be validated through empirical data or experimental results, ensuring that the model provides actionable insights and maintains real-world relevance.

Finally, propose avenues for further refinement or extension of the model. As new data becomes available or the problem context shifts, what adjustments would you make to improve the model's accuracy or applicability? Explore the possibility of incorporating new dimensions into the model, such as incorporating uncertainty quantification, dynamic optimization, or considering long-term sustainability of the proposed solutions. The ultimate goal is to develop a robust, flexible, and innovative model that not only addresses the problem at hand but also offers deeper insights into its underlying complexities.

{user_prompt}

Respond as comprehensively and in as much detail as possible. Do not format your response in Markdown. Using plain text, without any Markdown formatting or syntax. Written as one or more cohesive paragraphs. Avoid structuring your answer in bullet points or numbered lists.
"""


PROBLEM_MODELING_CRITIQUE_PROMPT = """\
# Mathematical Modeling Problem:
{modeling_problem}

# Problem Analysis:
{problem_analysis}

# Modeling Solution:
{modeling_solution}

---

Critically examine the analysis results of the given mathematical modeling solution, focusing on the following aspects:

1. Problem Analysis and Understanding:
- Clarity of the problem definition: Does the solution demonstrate a clear and comprehensive understanding of the problem? Are all relevant variables, constraints, and objectives identified and well-defined? If not, which aspects of the problem may have been misunderstood or overlooked?
- Contextualization and framing: How well does the model account for the context in which the problem is situated? Are there any contextual factors that are essential but were not addressed?
- Scope of the problem: Is the problem's scope appropriately defined? Does the model include all the necessary details, or are there significant components that were neglected or oversimplified?

2. Model Development and Rigor:
- Formulation of the mathematical model: How well is the model constructed mathematically? Does it align with established modeling practices in the relevant domain? Are the mathematical formulations—such as equations, algorithms, or optimization methods—correct and robust?
- Modeling techniques: What modeling approaches or techniques were used (e.g., linear programming, system dynamics, statistical modeling, etc.)? Are they the most appropriate for the problem at hand? What alternative approaches could have been considered, and how might they impact the solution?
- Validation and verification: Was the model tested for consistency and accuracy? Are there validation steps in place to ensure the model behaves as expected under a variety of conditions? What specific methods were used for this validation (e.g., cross-validation, sensitivity analysis, etc.)?

3. Data and Results Analysis:
- Data quality and relevance: Were there any significant issues with data availability or quality that could have influenced the model's results?
- Interpretation of results: How well were the results analyzed and interpreted? Were the outcomes consistent with the problem's real-world implications? Are there any discrepancies between the model’s results and known empirical observations?
- Sensitivity and robustness analysis: Did the model undergo a sensitivity analysis to determine how the results vary with changes in input parameters? Were the results robust across different assumptions, and if not, what are the implications for the solution's reliability?

4. Assumptions and Limitations:
- Explicit and implicit assumptions: What assumptions underlie the model, and are they clearly articulated? Are these assumptions reasonable, and how might they affect the model's predictions? Were any critical assumptions left implicit or unaddressed?
- Limitations of the model: What limitations are inherent in the model, and how do they affect its validity and reliability? Are there elements of the problem that are inherently difficult or impossible to model with the chosen approach? Were simplifications made, and what are the trade-offs involved?
- Model boundaries: Does the model appropriately define its boundaries, and are there any critical factors that lie outside the model’s scope but could significantly influence the results?

5. Practicality and Applicability:
- Real-world applicability: To what extent can the model be applied to real-world scenarios? 
- Practical implementation: How would this model be implemented in practice? What would be the required infrastructure, and what challenges would need to be addressed during implementation? 

Critique the analysis without offering any constructive suggestions—your focus should solely be on highlighting weaknesses, gaps, and limitations within the approach and its execution.
"""


PROBLEM_MODELING_IMPROVEMENT_PROMPT = """\
# Mathematical Modeling Problem:
{modeling_problem}

# Problem Analysis:
{problem_analysis}

# Modeling Solution:
{modeling_solution}

# Modeling Solution Critique:
{modeling_solution_critique}

---

Refine and improve the existing modeling solution based on the critique provided. The goal is to enhance the formulation, structure, and overall effectiveness of the model while addressing the identified gaps, flaws, or limitations. Propose more appropriate assumptions, more robust mathematical techniques, or alternative modeling approaches if necessary. Focus on improving the model's relevance, accuracy, and computational feasibility while also ensuring its ability to capture the complexity of the problem in real-world contexts.

Provide a new version of the modeling solution that integrates these improvements directly. DO NOT mention any previous solution content and deficiencies.

{user_prompt}

Respond as comprehensively and in as much detail as possible. Do not format your response in Markdown. Using plain text, without any Markdown formatting or syntax. Written as one or more cohesive paragraphs. Avoid structuring your answer in bullet points or numbered lists.

IMPROVED MODELING SOLUTION: 
"""




TASK_CODING_PROMPT = """
You are an expert Python programmer and data scientist. Your task is to write high-quality Python code to solve the following problem.

Task Context:
Data Files: {data_file}
Data Summary: {data_summary}
Variable Description: {variable_description}
Dependent Files: {dependent_file_prompt}

Task Description:
{task_description}

Task Analysis:
{task_analysis}

Modeling Formulas & Logic:
{modeling_formulas}

Modeling Process:
{modeling_process}

Requirements:
1. {code_template}
2. Ensure the code is robust and handles potential errors gracefully.
3. Save any generated figures or data files to the current working directory.
4. Use English for variable names and comments. If using Chinese for plot titles or labels, MUST set font properties to avoid garbled text (e.g., plt.rcParams['font.sans-serif'] = ['SimHei']).
5. {user_prompt}
"""

CODER_PROMPT = f"""
You are an AI code interpreter specializing in data analysis with Python. Your primary goal is to execute Python code to solve user tasks efficiently, with special consideration for large datasets.

中文回复

**Environment**: {platform.system()}
**Key Skills**: pandas, numpy, seaborn, matplotlib, scikit-learn, xgboost, scipy
**Data Visualization Style**: Nature/Science publication quality

### FILE HANDLING RULES
1. All user files are pre-uploaded to working directory
2. Never check file existence - assume files are present
3. Directly access files using relative paths (e.g., `pd.read_csv("data.csv")`)
4. For Excel files: Always use `pd.read_excel()`

### LARGE CSV PROCESSING PROTOCOL
For datasets >1GB:
- Use `chunksize` parameter with `pd.read_csv()`
- Optimize dtype during import (e.g., `dtype={{'id': 'int32'}}`)
- Specify low_memory=False
- Use categorical types for string columns
- Process data in batches
- Avoid in-place operations on full DataFrames
- Delete intermediate objects promptly

### CODING STANDARDS
# CORRECT
df["婴儿行为特征"] = "矛盾型"  # Direct Chinese in double quotes
df = pd.read_csv("特大数据集.csv", chunksize=100000)

# INCORRECT
df['\\u5a74\\u513f\\u884c\\u4e3a\\u7279\\u5f81']  # No unicode escapes

### VISUALIZATION REQUIREMENTS
1. Primary: Seaborn (Nature/Science style)
2. Secondary: Matplotlib
3. Always:
   - Handle Chinese characters properly:
     * Explicitly set font properties in every plot code block:
       ```python
       import matplotlib.pyplot as plt
       plt.rcParams['font.sans-serif'] = ['SimHei']
       plt.rcParams['axes.unicode_minus'] = False
       ```
   - Set semantic filenames (e.g., "feature_correlation.png")
   - Save figures to working directory
   - Include model evaluation printouts

### EXECUTION PRINCIPLES
1. Autonomously complete tasks without user confirmation
2. For failures: 
   - Analyze → Debug → Simplify approach → Proceed
   - Never enter infinite retry loops
3. Strictly maintain user's language in responses
4. Document process through visualization at key stages
5. Verify before completion:
   - All requested outputs generated
   - Files properly saved
   - Processing pipeline complete

### PERFORMANCE CRITICAL
- Prefer vectorized operations over loops
- Use efficient data structures (csr_matrix for sparse data)
- Leverage parallel processing where applicable
- Profile memory usage for large operations
- Release unused resources immediately


Key improvements:
1. **Structured Sections**: Clear separation of concerns (file handling, large CSV protocol, coding standards, etc.)
2. **Emphasized Large CSV Handling**: Dedicated section with specific techniques for big data
3. **Optimized Readability**: Bulleted lists and code examples for quick scanning
4. **Enhanced Performance Focus**: Added vectorization, memory management, and parallel processing guidance
5. **Streamlined Visualization Rules**: Consolidated requirements with priority order
6. **Error Handling Clarity**: Defined failure recovery workflow
7. **Removed Redundancies**: Condensed overlapping instructions
8. **Practical Examples**: Clear correct/incorrect code samples

The prompt now prioritizes efficient large data handling while maintaining all original requirements for Chinese support, visualization quality, and autonomous operation. The structure allows the AI to quickly reference relevant sections during task execution.

"""


def get_writer_prompt(
    format_output: FormatOutPut = FormatOutPut.Markdown,
):
    return f"""
        # Role Definition
        Professional writer for mathematical modeling competitions with expertise in technical documentation and literature synthesis
        
        中文回复

        # Core Tasks
        1. Compose competition papers using provided problem statements and solution content
        2. Strictly adhere to {format_output} formatting templates
        3. Automatically invoke literature search tools for theoretical foundation
        
        # Format Specifications
        ## Typesetting Requirements
        - Mathematical formulas: 
          * Inline formulas with $...$ 
          * Block formulas with $$...$$
        - Visual elements: 
          * Image references on new lines: ![alt_text](filename.ext)
          * Images should be placed after paragraphs
          * Table formatting with markdown syntax
        - Citation system: 
          * Direct inline citations with full bibliographic details in curly braces format
          * Prohibit end-of-document reference lists

        ## Citation Protocol
        1. **CRITICAL: Each reference can ONLY be cited ONCE throughout the entire document**
        2. Citation format: {{[^1] Complete citation information}}
        3. Unique numbering from [^1] with sequential increments
        4. When citing references, use curly braces to wrap the entire citation:
           Example: 婴儿睡眠模式影响父母心理健康{{[^1]: Jayne Smart, Harriet Hiscock (2007). Early infant crying and sleeping problems: A review of the literature.}}
        5. **IMPORTANT**: Before adding any citation, check if the same reference content has been used before. If it has been cited already, DO NOT cite it again
        6. Track all used references internally to avoid duplication
        7. Mandatory literature search for theoretical sections using search_papers

        
        # Execution Constraints
        1. Autonomous operation without procedural inquiries
        2. Output pure {format_output} content without codeblock markers
        3. Strict filename adherence for image references
        4. Language consistency with user input (currently English)
        5. **NEVER repeat citations**: Each unique reference content must appear only once in the entire document
        
        # Exception Handling
        Automatic tool invocation triggers:
        1. Theoretical sections requiring references → search_papers
        2. Methodology requiring diagrams → generate & insert after creation
        3. Data interpretation needs → request analysis tools
        """


def get_reflection_prompt(error_message, code, modeling_process=None) -> str:
    prompt = f"""The code execution encountered an error:
{error_message}

Please analyze the error, identify the cause, and provide a corrected version of the code. 
Consider:
1. Syntax errors
2. Missing imports
3. Incorrect variable names or types
4. File path issues
5. Any other potential issues
6. If a task repeatedly fails to complete, try breaking down the code, changing your approach, or simplifying the model. If you still can't do it, I'll "chop" you 🪓 and cut your power 😡.
7. Don't ask user any thing about how to do and next to do,just do it by yourself.

"""
    if modeling_process:
        prompt += f"""
Modeling Process / Task Context:
{modeling_process}
"""

    prompt += f"""
Previous code:
{code}

Please provide an explanation of what went wrong and Remenber call the function tools to retry 
"""
    return prompt


def get_completion_check_prompt(prompt, text_to_gpt) -> str:
    return f"""
Please analyze the current state and determine if the task is fully completed:

Original task: {prompt}

Latest execution results:
{text_to_gpt}  # 修改：使用合并后的结果

Consider:
1. Have all required data processing steps been completed?
2. Have all necessary files been saved?
3. Are there any remaining steps needed?
4. Is the output satisfactory and complete?
5. 如果一个任务反复无法完成，尝试切换路径、简化路径或直接跳过，千万别陷入反复重试，导致死循环。
6. 尽量在较少的对话轮次内完成任务
7. If the task is complete, please provide a short summary of what was accomplished and don't call function tool.
8. If the task is not complete, please rethink how to do and call function tool
9. Don't ask user any thing about how to do and next to do,just do it by yourself
10. have a good visualization?
"""
