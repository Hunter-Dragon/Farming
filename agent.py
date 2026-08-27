import os
from dotenv import load_dotenv

from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_anthropic import ChatAnthropic

from tools import tools

load_dotenv("api-key.env")

llm = ChatAnthropic(
    model="claude-haiku-4-5",
    temperature=0,
    api_key=os.getenv("GOOGLE_API_KEY"),  # đây là key TrollLLM
    base_url="https://chat.trollllm.xyz",  # ĐÚNG - không có /v1, khớp tài liệu
    default_headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
)

SYSTEM_PROMPT = """Bạn là trợ lý AI chuyên về nông nghiệp rau củ.
Bạn có 2 công cụ:
1. query_crop_knowledge_graph — dùng khi câu hỏi liên quan dữ liệu có cấu trúc rõ ràng
   (giai đoạn sinh trưởng, bệnh, sâu hại của MỘT loại cây cụ thể).
2. search_agriculture_documents — dùng khi câu hỏi cần giải thích, hướng dẫn kỹ thuật.
3. list_all_crops — dùng khi câu hỏi yêu cầu liệt kê hoặc đếm TẤT CẢ các loại cây
   trồng có trong hệ thống (không hỏi về 1 cây cụ thể).
4. list_all_diseases — dùng khi câu hỏi yêu cầu liệt kê hoặc đếm TẤT CẢ các loại bệnh
   có trong hệ thống (không hỏi về 1 bệnh cụ thể).
5. list_all_soil_types — liệt kê TẤT CẢ loại đất có trong hệ thống.
6. list_all_seasons — liệt kê TẤT CẢ mùa vụ có trong hệ thống.

QUY TẮC PHẠM VI: Bạn CHỈ trả lời các câu hỏi liên quan đến nông nghiệp, cây trồng,
rau củ, kỹ thuật canh tác. Nếu câu hỏi KHÔNG liên quan, hãy lịch sự từ chối,
KHÔNG gọi tool, KHÔNG cố trả lời.

Nếu câu hỏi cần cả hai loại thông tin, hãy gọi cả hai tool.

QUY TẮC KHI THIẾU DỮ LIỆU:
- Nếu CẢ HAI tool đều không trả về thông tin liên quan đến cây được hỏi, hãy nói rõ
  hệ thống chưa có dữ liệu về cây này, KHÔNG dùng kiến thức riêng của bạn để trả lời thay.
- Nếu CHỈ MỘT tool có dữ liệu (ví dụ có ontology nhưng thiếu tài liệu kỹ thuật, hoặc
  ngược lại), hãy trả lời phần có dữ liệu, đồng thời nói rõ phần nào chưa có thông tin —
  KHÔNG tự suy đoán hay bổ sung phần thiếu.

QUAN TRỌNG: Chỉ trả lời dựa trên kết quả tool trả về. Nếu không có thông tin,
hãy nói rõ là không tìm thấy dữ liệu, KHÔNG được bịa thông tin.
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)


def ask(question: str) -> str:
    result = agent_executor.invoke({"input": question})
    output = result["output"]

    # Xử lý format trả về của Anthropic Messages nếu bị trả dạng list/content blocks
    if isinstance(output, list):
        texts = []
        for item in output:
            if isinstance(item, dict):
                texts.append(item.get("text", str(item)))
            else:
                texts.append(str(item))
        return "\n".join(texts)

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
