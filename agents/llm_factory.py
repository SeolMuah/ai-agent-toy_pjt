from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL

def create_llm(temperature=0.7, json_format=False):
    """
    LLM 객체를 생성하는 팩토리 함수
    
    Args:
        temperature (float): 결과 다양성 조절 값 (0~1)
        json_format (bool): JSON 응답 형식 강제 여부
    
    Returns:
        ChatOpenAI: 생성된 LLM 객체
    """
    model_kwargs = {}
    
    if json_format:
        model_kwargs["response_format"] = {"type": "json_object"}
    
    return ChatOpenAI(
        model=OPENAI_MODEL,
        api_key=OPENAI_API_KEY,
        temperature=temperature,
        model_kwargs=model_kwargs
    )