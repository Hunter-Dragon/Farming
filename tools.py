# tools.py
from langchain.tools import tool
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from hybrid_retriever import hybrid_search

# Client gọi GraphQL API đã dựng ở Bước 2
transport = RequestsHTTPTransport(url="http://localhost:8001/graphql")
gql_client = Client(transport=transport, fetch_schema_from_transport=True)

@tool
def query_crop_knowledge_graph(crop_name: str) -> str:
    """Dùng tool này khi cần tra cứu thông tin CÓ CẤU TRÚC về một loại cây trồng cụ thể:
    giai đoạn sinh trưởng, bệnh dễ mắc, sâu hại. Input là tên cây trồng bằng tiếng Việt,
    ví dụ 'Cà chua'."""
    query = gql(f'''
        query {{
            crop(name: "{crop_name}") {{
                growthStages {{ name durationDays }}
                diseases {{ name }}
            }}
        }}
    ''')
    result = gql_client.execute(query)
    return str(result)

@tool
def search_agriculture_documents(question: str) -> str:
    """Dùng tool này khi câu hỏi cần thông tin GIẢI THÍCH, HƯỚNG DẪN KỸ THUẬT
    không có sẵn dạng cấu trúc rõ ràng (VD: cách chăm sóc, kỹ thuật canh tác chi tiết).
    Input là câu hỏi gốc của người dùng."""
    chunks = hybrid_search(question)
    return "\n---\n".join(chunks)

tools = [query_crop_knowledge_graph, search_agriculture_documents]