import os
import json
import asyncio
from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile, HTTPException
from icecream import ic
from pydantic import BaseModel
import litellm
import requests

from app.core.workflow import FastMMWorkFlow
from app.schemas.enums import CompTemplate, FormatOutPut
from app.utils.log_util import logger
from app.services.redis_manager import redis_manager
from app.schemas.request import Problem, ExampleRequest, MMBenchRequest
from app.schemas.response import SystemMessage
from app.utils.common_utils import (
    create_task_id,
    create_work_dir,
    get_current_files,
    md_2_docx,
)
from app.core.utils.mmbench_loader import MMBenchLoader
from app.core.evaluation.evaluator import MMBenchEvaluator
from app.config.setting import settings

router = APIRouter()


class ValidateApiKeyRequest(BaseModel):
    api_key: str
    base_url: str = "https://api.openai.com/v1"
    model_id: str
    provider: str = "openai"


class ValidateOpenalexEmailRequest(BaseModel):
    email: str


class ValidateOpenalexEmailResponse(BaseModel):
    valid: bool
    message: str


class ValidateApiKeyResponse(BaseModel):
    valid: bool
    message: str


class SaveApiConfigRequest(BaseModel):
    coordinator: dict
    modeler: dict
    coder: dict
    writer: dict
    openalex_email: str


@router.post("/save-api-config")
async def save_api_config(request: SaveApiConfigRequest):
    """
    保存验证成功的 API 配置到 settings
    """
    try:
        # 更新各个模块的设置
        if request.coordinator:
            settings.COORDINATOR_API_KEY = request.coordinator.get("apiKey", "")
            settings.COORDINATOR_MODEL = request.coordinator.get("modelId", "")
            settings.COORDINATOR_BASE_URL = request.coordinator.get("baseUrl", "")

        if request.modeler:
            settings.MODELER_API_KEY = request.modeler.get("apiKey", "")
            settings.MODELER_MODEL = request.modeler.get("modelId", "")
            settings.MODELER_BASE_URL = request.modeler.get("baseUrl", "")

        if request.coder:
            settings.CODER_API_KEY = request.coder.get("apiKey", "")
            settings.CODER_MODEL = request.coder.get("modelId", "")
            settings.CODER_BASE_URL = request.coder.get("baseUrl", "")

        if request.writer:
            settings.WRITER_API_KEY = request.writer.get("apiKey", "")
            settings.WRITER_MODEL = request.writer.get("modelId", "")
            settings.WRITER_BASE_URL = request.writer.get("baseUrl", "")

        if request.openalex_email:
            settings.OPENALEX_EMAIL = request.openalex_email

        return {"success": True, "message": "配置保存成功"}
    except Exception as e:
        logger.error(f"保存配置失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")


@router.post("/validate-api-key", response_model=ValidateApiKeyResponse)
async def validate_api_key(request: ValidateApiKeyRequest):
    """
    验证 API Key 的有效性
    """
    try:
        model = request.model_id
        
        # 智能判断 Provider 前缀
        # 1. Ollama 特殊处理
        if request.provider == "ollama":
            if not model.startswith("ollama/"):
                model = f"ollama/{model}"
        
        # 2. 如果提供了自定义 Base URL (且不是 OpenAI 官方)，通常是 OpenAI 兼容接口
        # 包括 DashScope Compatible, DeepSeek, SiliconFlow, LocalAI 等
        # Anthropic 和 Azure 有自己的协议，不强制转为 openai/
        elif (
            request.base_url 
            and request.base_url.strip() 
            and "api.openai.com" not in request.base_url
            and request.provider not in ["anthropic", "azure", "gemini", "vertex_ai"]
        ):
            # 强制使用 openai/ 前缀以走 OpenAI 兼容协议
            if not model.startswith("openai/"):
                model = f"openai/{model}"
                
        # 3. 其他情况，如果指定了 Provider 且不是 openai/custom，尝试加上前缀
        # 例如 dashscope/qwen-turbo (走原生 SDK)
        elif request.provider and request.provider not in ["openai", "custom"] and "/" not in model:
            model = f"{request.provider}/{model}"

        # 使用 litellm 发送测试请求
        await litellm.acompletion(
            model=model,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=1,
            api_key=request.api_key,
            base_url=request.base_url
            if request.base_url and request.base_url != "https://api.openai.com/v1"
            else None,
        )

        return ValidateApiKeyResponse(valid=True, message="✓ 模型 API 验证成功")
    except Exception as e:
        error_msg = str(e)

        # 解析不同类型的错误
        if "401" in error_msg or "Unauthorized" in error_msg:
            return ValidateApiKeyResponse(valid=False, message="✗ API Key 无效或已过期")
        elif "404" in error_msg or "Not Found" in error_msg:
            return ValidateApiKeyResponse(
                valid=False, message="✗ 模型 ID 不存在或 Base URL 错误"
            )
        elif "429" in error_msg or "rate limit" in error_msg.lower() or "ratelimit" in error_msg.lower() or "quota" in error_msg.lower():
            return ValidateApiKeyResponse(
                valid=False, message="✗ 请求过于频繁或额度不足(Rate Limit/Quota)"
            )
        elif "403" in error_msg or "Forbidden" in error_msg:
            return ValidateApiKeyResponse(
                valid=False, message="✗ API 权限不足或账户余额不足"
            )
        else:
            # truncate to avoid too long message but keep enough info
            return ValidateApiKeyResponse(
                valid=False, message=f"✗ 验证失败: {error_msg[:100]}..."
            )


@router.post("/validate-openalex-email", response_model=ValidateOpenalexEmailResponse)
async def validate_openalex_email(request: ValidateOpenalexEmailRequest):
    """
    验证 OpenAlex Email 的有效性
    """
    try:
        response = requests.get(
            f"https://api.openalex.org/works?mailto={request.email}"
        )
        logger.debug(f"OpenAlex Email 验证响应: {response}")
        response.raise_for_status()
        return ValidateOpenalexEmailResponse(
            valid=True, message="✓ OpenAlex Email 验证成功"
        )
    except Exception as e:
        return ValidateOpenalexEmailResponse(
            valid=False, message=f"✗ OpenAlex Email 验证失败: {str(e)}"
        )


@router.post("/mmbench")
async def mmbenchModeling(
    request: MMBenchRequest,
    background_tasks: BackgroundTasks,
):
    task_id = create_task_id()
    work_dir = create_work_dir(task_id)
    
    loader = MMBenchLoader()
    try:
        ques_all, dataset_files = loader.load_problem(request.task_id)
        loader.copy_dataset(dataset_files, work_dir)
    except Exception as e:
        logger.error(f"Failed to load MMBench task {request.task_id}: {e}")
        raise HTTPException(status_code=404, detail=f"Failed to load task: {e}")

    # 存储任务ID
    await redis_manager.set(f"task_id:{task_id}", task_id)

    logger.info(f"Adding background task for task_id: {task_id}")
    # 将任务添加到后台执行
    background_tasks.add_task(
        run_modeling_task_async,
        task_id,
        ques_all,
        request.comp_template,
        request.format_output,
    )
    return {"task_id": task_id, "status": "processing"}


@router.post("/evaluate/{task_id}")
async def evaluate_task(task_id: str, background_tasks: BackgroundTasks):
    """
    Manually trigger MMBench evaluation for a completed task.
    """
    work_dir = create_work_dir(task_id)
    eval_context_path = os.path.join(work_dir, "evaluation_context.json")
    
    if not os.path.exists(eval_context_path):
        # Fallback: try to reconstruct if json doesn't exist? 
        # Or just fail if workflow didn't finish properly.
        # But wait, we might have partial results.
        # For now, require the context file which means workflow finished successfully.
        raise HTTPException(status_code=404, detail="Evaluation context not found. Has the task finished?")

    try:
        with open(eval_context_path, "r", encoding="utf-8") as f:
            evaluation_data = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load evaluation context: {e}")

    # Run evaluation in background
    background_tasks.add_task(run_evaluation_async, task_id, work_dir, evaluation_data)
    
    return {"task_id": task_id, "status": "evaluation_started"}


async def run_evaluation_async(task_id: str, work_dir: str, evaluation_data: dict):
    try:
        evaluator = MMBenchEvaluator(task_id)
        await redis_manager.publish_message(
            task_id,
            SystemMessage(content="正在进行 MMBench 评估..."),
        )
        await evaluator.evaluate_solution(evaluation_data, work_dir)
        await redis_manager.publish_message(
            task_id,
            SystemMessage(content="MMBench 评估完成", type="success"),
        )
    except Exception as e:
        logger.error(f"MMBench Evaluation failed: {e}")
        await redis_manager.publish_message(
            task_id,
            SystemMessage(content=f"MMBench 评估失败: {e}", type="error"),
        )


@router.get("/examples-list")
async def get_examples_list():
    """
    Get list of available examples including MMBench problems.
    """
    mmbench_path = os.path.join("app", "core", "data", "MMBench", "problem")
    mmbench_examples = []
    
    if os.path.exists(mmbench_path):
        files = os.listdir(mmbench_path)
        # Sort by year descending, then problem letter
        # Filename format: YYYY_L.json (e.g., 2021_C.json)
        files.sort(key=lambda x: x.replace(".json", ""), reverse=True)
        
        for file in files:
            if file.endswith(".json"):
                try:
                    bench_id = file.replace(".json", "")
                    parts = bench_id.split("_")
                    year = parts[0]
                    problem = parts[1] if len(parts) > 1 else ""
                    
                    mmbench_examples.append({
                        "id": bench_id,
                        "title": f"{year} MCM/ICM Problem {problem}",
                        "source": f"MMBench/{bench_id}",
                        "description": f"Mathematical modeling problem {problem} from the {year} MCM/ICM competition.",
                        "year": year,
                        "type": "MCM/ICM",
                        "tags": ["Math Modeling", f"Year {year}", f"Problem {problem}"]
                    })
                except Exception as e:
                    logger.error(f"Error parsing filename {file}: {e}")
                    continue

    return {
        "mmbench": mmbench_examples
    }


@router.post("/example")
async def exampleModeling(
    example_request: ExampleRequest,
    background_tasks: BackgroundTasks,
):
    task_id = create_task_id()
    work_dir = create_work_dir(task_id)

    # Handle MMBench sources
    if example_request.source.startswith("MMBench/"):
        bench_id = example_request.source.split("/")[-1]  # e.g., 2021_C
        
        # 1. Get Problem Text
        problem_json_path = os.path.join("app", "core", "data", "MMBench", "problem", f"{bench_id}.json")
        ques_all = ""
        if os.path.exists(problem_json_path):
            try:
                import json
                with open(problem_json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    # Combine background and requirement
                    parts = []
                    if data.get("background"):
                        parts.append(f"## Background\n{data.get('background')}")
                    if data.get("problem_requirement"):
                        parts.append(f"## Requirement\n{data.get('problem_requirement')}")
                    ques_all = "\n\n".join(parts)
            except Exception as e:
                logger.error(f"Error reading MMBench problem file: {e}")
        
        if not ques_all.strip():
            ques_all = f"Please solve the problem {bench_id} using the provided data files."

        # 2. Copy Data Files
        dataset_dir = os.path.join("app", "core", "data", "MMBench", "dataset", bench_id)
        if os.path.exists(dataset_dir):
            # Copy all files from dataset directory
            for root, dirs, files in os.walk(dataset_dir):
                for file in files:
                    src_file = os.path.join(root, file)
                    # Calculate relative path to keep structure if needed, or just flat copy
                    # For simplicity and Agent compatibility, flat copy to work_dir is usually better 
                    # unless name conflicts. MMBench usually has unique files.
                    dst_file = os.path.join(work_dir, file)
                    try:
                        with open(src_file, "rb") as src, open(dst_file, "wb") as dst:
                            dst.write(src.read())
                    except Exception as e:
                        logger.error(f"Failed to copy file {file}: {e}")
        else:
            logger.warning(f"Dataset directory not found: {dataset_dir}")

    else:
        # Existing logic for standard examples
        example_dir = os.path.join("app", "example", "example", example_request.source)
        ic(example_dir)
        try:
            with open(os.path.join(example_dir, "questions.txt"), "r", encoding="utf-8") as f:
                ques_all = f.read()
        except FileNotFoundError:
             ques_all = "No question description found."

        current_files = get_current_files(example_dir, "data")
        for file in current_files:
            src_file = os.path.join(example_dir, file)
            dst_file = os.path.join(work_dir, file)
            with open(src_file, "rb") as src, open(dst_file, "wb") as dst:
                dst.write(src.read())

    # 存储任务ID
    await redis_manager.set(f"task_id:{task_id}", task_id)

    logger.info(f"Adding background task for task_id: {task_id}")
    # 将任务添加到后台执行
    background_tasks.add_task(
        run_modeling_task_async,
        task_id,
        ques_all,
        CompTemplate.CHINA,
        FormatOutPut.Markdown,
    )
    return {"task_id": task_id, "status": "processing"}


@router.post("/modeling")
async def modeling(
    background_tasks: BackgroundTasks,
    ques_all: str = Form(...),  # 从表单获取
    comp_template: CompTemplate = Form(...),  # 从表单获取
    format_output: FormatOutPut = Form(...),  # 从表单获取
    files: list[UploadFile] = File(default=None),
):
    task_id = create_task_id()
    work_dir = create_work_dir(task_id)

    # 如果有上传文件，保存文件
    if files:
        logger.info(f"开始处理上传的文件，工作目录: {work_dir}")
        for file in files:
            try:
                data_file_path = os.path.join(work_dir, file.filename)
                logger.info(f"保存文件: {file.filename} -> {data_file_path}")

                # 确保文件名不为空
                if not file.filename:
                    logger.warning("跳过空文件名")
                    continue

                content = await file.read()
                if not content:
                    logger.warning(f"文件 {file.filename} 内容为空")
                    continue

                with open(data_file_path, "wb") as f:
                    f.write(content)
                logger.info(f"成功保存文件: {data_file_path}")

            except Exception as e:
                logger.error(f"保存文件 {file.filename} 失败: {str(e)}")
                raise HTTPException(
                    status_code=500, detail=f"保存文件 {file.filename} 失败: {str(e)}"
                )
    else:
        logger.warning("没有上传文件")

    # 存储任务ID
    await redis_manager.set(f"task_id:{task_id}", task_id)

    logger.info(f"Adding background task for task_id: {task_id}")
    # 将任务添加到后台执行
    background_tasks.add_task(
        run_modeling_task_async, task_id, ques_all, comp_template, format_output
    )
    return {"task_id": task_id, "status": "processing"}


async def run_modeling_task_async(
    task_id: str,
    ques_all: str,
    comp_template: CompTemplate,
    format_output: FormatOutPut,
):
    logger.info(f"run modeling task for task_id: {task_id}")

    problem = Problem(
        task_id=task_id,
        ques_all=ques_all,
        comp_template=comp_template,
        format_output=format_output,
    )

    # 发送任务开始状态
    await redis_manager.publish_message(
        task_id,
        SystemMessage(content="任务开始处理"),
    )

    # 给一个短暂的延迟，确保 WebSocket 有机会连接
    await asyncio.sleep(1)

    # 创建任务并等待它完成
    task = asyncio.create_task(FastMMWorkFlow().execute(problem))
    # 设置超时时间（比如 300 分钟）
    await asyncio.wait_for(task, timeout=3600 * 5)

    # 发送任务完成状态
    await redis_manager.publish_message(
        task_id,
        SystemMessage(content="任务处理完成", type="success"),
    )
    # 转换md为docx
    md_2_docx(task_id)
