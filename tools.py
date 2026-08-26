# tools.py
from langchain.tools import tool
from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport
from hybrid_retriever import hybrid_search

import json

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
    return json.dumps(result, ensure_ascii=False)

@tool
def search_agriculture_documents(question: str) -> str:
    """Dùng tool này khi câu hỏi cần thông tin GIẢI THÍCH, HƯỚNG DẪN KỸ THUẬT
    không có sẵn dạng cấu trúc rõ ràng (VD: cách chăm sóc, kỹ thuật canh tác chi tiết).
    Input là câu hỏi gốc của người dùng."""
    chunks = hybrid_search(question)
    return "\n---\n".join(chunks)

@tool
def list_all_diseases() -> str:
    """Dùng khi câu hỏi yêu cầu liệt kê tất cả các loại bệnh có trong hệ thống."""
    query = gql('''
        query { allDiseases { name } }
    ''')
    result = gql_client.execute(query)
    return json.dumps(result, ensure_ascii=False)

@tool
def list_all_crops() -> str:
    """Dùng tool này khi câu hỏi yêu cầu liệt kê TẤT CẢ các loại cây trồng có trong
    hệ thống, hoặc hỏi có bao nhiêu loại cây trồng trong dữ liệu."""
    query = gql('''
        query {
            allCrops {
                name
            }
        }
    ''')
    result = gql_client.execute(query)
    return json.dumps(result, ensure_ascii=False)

@tool
def list_all_soil_types() -> str:
    """Dùng khi câu hỏi yêu cầu liệt kê tất cả các loại đất có trong hệ thống."""
    query = gql('''
        query { allSoilTypes }
    ''')
    result = gql_client.execute(query)
    return json.dumps(result, ensure_ascii=False)

@tool
def list_all_seasons() -> str:
    """Dùng khi câu hỏi yêu cầu liệt kê tất cả các mùa vụ có trong hệ thống."""
    query = gql('''
        query { allSeasons }
    ''')
    result = gql_client.execute(query)
    return json.dumps(result, ensure_ascii=False)

tools = [query_crop_knowledge_graph, search_agriculture_documents, list_all_diseases, list_all_crops, list_all_soil_types, list_all_seasons]