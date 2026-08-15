"""
LLM service — thin abstraction over OpenAI / Ollama / mock.
Import and call `chat(messages)` from any endpoint.
"""
import httpx
from typing import List, Dict, Optional, Any
from config import (
    LLM_PROVIDER,
    OPENAI_API_KEY, OPENAI_MODEL, OPENAI_BASE_URL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE,
    OLLAMA_BASE_URL, OLLAMA_MODEL,
)

SYSTEM_PROMPT = """你是 PyPad 的 AI 导师。你的职责：
1. 用简洁易懂的中文讲解 Python 知识点
2. 给出代码示例时附带注释
3. 如果用户代码有错误，指出原因并给出修正建议
4. 根据用户水平调整讲解深度
5. 鼓励用户动手实践"""


def _openai_chat(
    messages: List[Dict[str, str]], 
    api_key: Optional[str] = None, 
    model: Optional[str] = None, 
    base_url: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 1000
) -> str:
    """Call OpenAI-compatible API with dynamic config overrides."""
    key = api_key or OPENAI_API_KEY
    mdl = model or OPENAI_MODEL
    url = (base_url or OPENAI_BASE_URL).rstrip("/")
    
    if not key or key.startswith("sk-your"):
        return ""
    resp = httpx.post(
        f"{url}/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": mdl,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _ollama_chat(
    messages: List[Dict[str, str]],
    base_url: Optional[str] = None,
    model: Optional[str] = None
) -> str:
    """Call local Ollama with dynamic config overrides."""
    url = (base_url or OLLAMA_BASE_URL).rstrip("/")
    mdl = model or OLLAMA_MODEL
    resp = httpx.post(
        f"{url}/api/chat",
        json={"model": mdl, "messages": messages, "stream": False},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


def _mock_chat(user_message: str, model_name: str = "Mock Model") -> str:
    """Deterministic mock for when no LLM is configured."""
    return (
        f"【AI Tutor · {model_name}】\n\n"
        f"你问到了一个很好的问题。关于「{user_message[:50]}」，"
        f"这里是核心要点：\n\n"
        f"1. 理解基本概念是第一步\n"
        f"2. 动手写代码验证你的理解\n"
        f"3. 遇到错误不要怕，调试是学习的一部分\n\n"
        f"💡 提示：您可在系统「设置」中输入自定义 API Key 或 Model，即可开启真实大模型智能辅导。"
    )


def chat(
    user_message: str, 
    context: Optional[List[Dict[str, str]]] = None,
    ai_config: Optional[Dict[str, Any]] = None
) -> str:
    """
    Main entry point. Sends user_message to the configured LLM provider.
    Supports dynamic runtime ai_config dictionary from user settings.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if context:
        messages.extend(context)
    messages.append({"role": "user", "content": user_message})

    cfg = ai_config or {}
    provider = cfg.get("provider") or LLM_PROVIDER
    api_key = cfg.get("apiKey") or OPENAI_API_KEY
    model = cfg.get("model") or OPENAI_MODEL
    base_url = cfg.get("baseUrl") or OPENAI_BASE_URL
    temperature = float(cfg.get("temperature", OPENAI_TEMPERATURE or 0.7))
    max_tokens = int(cfg.get("maxTokens", OPENAI_MAX_TOKENS or 1000))

    if provider in ["openai", "deepseek", "custom"]:
        try:
            reply = _openai_chat(messages, api_key=api_key, model=model, base_url=base_url, temperature=temperature, max_tokens=max_tokens)
            if reply:
                return reply
        except Exception as e:
            print(f"[llm] OpenAI/Custom call failed: {e}")

    if provider == "ollama":
        try:
            return _ollama_chat(messages, base_url=base_url, model=model)
        except Exception as e:
            print(f"[llm] Ollama call failed: {e}")

    # Fallback to mock
    return _mock_chat(user_message, model_name=model)


async def chat_stream_generator(
    user_message: str, 
    context: Optional[List[Dict[str, str]]] = None,
    ai_config: Optional[Dict[str, Any]] = None
):
    """
    Async generator that yields token chunks for SSE streaming response.
    """
    import asyncio
    full_text = chat(user_message, context=context, ai_config=ai_config)
    chunk_size = 3
    for i in range(0, len(full_text), chunk_size):
        chunk = full_text[i:i+chunk_size]
        yield f"data: {chunk}\n\n"
        await asyncio.sleep(0.03)
    yield "data: [DONE]\n\n"


