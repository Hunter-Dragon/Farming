# agent.py

from langchain_classic.agents import create_tool_calling_agent, AgentExecutor
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from tools import tools
from dotenv import load_dotenv

import os

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0, api_key=os.getenv("GOOGLE_API_KEY"))

SYSTEM_PROMPT = """Bạn là trợ lý AI chuyên về nông nghiệp rau củ.
Bạn có 2 công cụ:
1. query_crop_knowledge_graph — dùng khi câu hỏi liên quan dữ liệu có cấu trúc rõ ràng
   (giai đoạn sinh trưởng, bệnh, sâu hại của MỘT loại cây cụ thể).
2. search_agriculture_documents — dùng khi câu hỏi cần giải thích, hướng dẫn kỹ thuật.

Nếu câu hỏi cần cả hai loại thông tin, hãy gọi cả hai tool.
QUAN TRỌNG: Chỉ trả lời dựa trên kết quả tool trả về. Nếu không có thông tin,
hãy nói rõ là không tìm thấy dữ liệu, KHÔNG được bịa thông tin.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

def ask(question: str) -> str:
    result = agent_executor.invoke({"input": question})
    output = result["output"]

    # Trường hợp 1: output là list chứa dict (dạng content blocks)
    if isinstance(output, list):
        texts = []
        for item in output:
            if isinstance(item, dict):
                texts.append(item.get("text", str(item)))
            else:
                texts.append(str(item))
        return "\n".join(texts)

    # Trường hợp 2: output là string nhưng trông giống list (do bị str() nhầm ở đâu đó)
    if isinstance(output, str) and output.strip().startswith("[{"):
        import ast
        try:
            parsed = ast.literal_eval(output)
            if isinstance(parsed, list):
                return "\n".join(
                    item.get("text", "") for item in parsed if isinstance(item, dict)
                )
        except (ValueError, SyntaxError):
            pass

    return output