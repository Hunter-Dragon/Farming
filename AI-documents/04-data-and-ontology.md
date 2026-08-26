# 04. Dữ liệu & Ontology

## Nguồn dữ liệu gốc

### `crops_data.csv` (583 dòng, mỗi dòng = 1 (cây, giai đoạn) )

Cột: `crop_name, crop_type, growth_stage, stage_duration, disease, pest,
soil_type, climate, season, fertilizer`.

- `crop_name`: tên tiếng Việt, ví dụ "Cà chua". Repo có **~190 loại cây/giống**
  khác nhau (nhiều biến thể như "Bí đỏ", "Bí đỏ hồ lô", "Bí đỏ bánh xe"...).
- `crop_type`: một trong `FruitVegetable`, `LeafyVegetable`, `RootVegetable`
  — khớp với 3 subclass OWL của `Crop` trong ontology.
- Mỗi cây có nhiều dòng (mỗi dòng = 1 giai đoạn sinh trưởng khác nhau,
  ví dụ Cà chua có 5 dòng: Nảy mầm/Thắt thân/Ra hoa/Đậu quả/Thu hoạch).
- `disease`, `pest`, `soil_type`, `climate`, `season`, `fertilizer` gắn theo
  từng dòng (từng giai đoạn) — nghĩa là về mặt dữ liệu, một cây có thể có
  giá trị disease/pest khác nhau ở mỗi giai đoạn (xem ví dụ Cà chua: giai
  đoạn "Ra hoa" ghi bệnh "Bệnh sương mai", giai đoạn "Thu hoạch" ghi bệnh
  "Bệnh đốm lá" — đều được coi là bệnh mà cây "susceptibleTo" nói chung khi
  chuyển sang RDF, không phân biệt theo giai đoạn).

### `docs/*.txt` (6 file, mỗi file 1 loại cây)

`ky-thuat-bap-cai.txt`, `ky-thuat-ca-chua.txt`, `ky-thuat-ca-rot.txt`,
`ky-thuat-dua-leo.txt`, `ky-thuat-rau-muong.txt`, `ky-thuat-su-hao.txt`.
Văn bản kỹ thuật canh tác dạng đoạn văn (không cấu trúc), ~13-15 dòng/file,
mỗi file phủ: điều kiện đất/khí hậu, các giai đoạn sinh trưởng (mô tả bằng
lời), bệnh/sâu hại phổ biến nhất + cách phòng trừ, thời gian thu hoạch và
dấu hiệu nhận biết.

**Chỉ 6/190 loại cây trong CSV có tài liệu kỹ thuật tương ứng** — đây là
giới hạn thực tế của kho RAG hiện tại, quan trọng khi viết phần "Dataset"
hoặc "Limitations" của bài báo: KG có phạm vi (coverage) rộng hơn nhiều so
với RAG.

## Ontology (`agri-ontology.ttl`)

Định dạng OWL/Turtle, namespace
`http://www.semanticweb.org/admin/ontologies/2026/7/untitled-ontology-2#`
(alias `agri:`), soạn bằng Protégé (OWL API).

### Classes

- `Crop` (superclass) với 3 subclass rời nhau (disjoint):
  `FruitVegetable`, `LeafyVegetable`, `RootVegetable`.
- `GrowthStage`, `Disease`, `Pest`, `SoilType`, `ClimateCondition`,
  `Season`, `FertilizerType` — tất cả disjoint với nhau và với `Crop`.

### Object Properties (domain → range)

| Property | Domain | Range |
|---|---|---|
| `hasGrowthStage` | Crop | GrowthStage |
| `susceptibleTo` | Crop | Disease |
| `attackedBy` | Crop | Pest |
| `requiresSoil` | Crop | SoilType |
| `plantedInSeason` | Crop | Season |
| `treatedWith` | Disease | FertilizerType |

### Data Properties

| Property | Domain | Range |
|---|---|---|
| `durationDays` | GrowthStage | xsd:integer |
| `optimalTemperature` | Crop | xsd:float (**định nghĩa trong ontology nhưng không thấy được set giá trị trong `csv_to_rdf.py`** — trường mồ côi, chưa có dữ liệu) |
| `harvestYield` | ClimateCondition | xsd:float (**tương tự — định nghĩa nhưng chưa dùng**) |

## Sinh RDF từ CSV (`csv_to_rdf.py`)

- Chuyển mỗi dòng CSV thành các triples: gán `rdf:type` crop theo đúng
  subclass (`crop_type`), gắn `rdfs:label` (có `@vi` language tag) cho mọi
  entity, tạo URI bằng cách thay khoảng trắng bằng `_` (hàm `uri()`).
- URI của `GrowthStage` được ghép `{crop}_{stage}` để tránh trùng giữa các
  cây có cùng tên giai đoạn (ví dụ "Nảy mầm" của Cà chua và Bắp cải là 2
  entity RDF khác nhau).
- URI của `Disease`, `Pest`, `SoilType`, `Climate`, `Season`,
  `FertilizerType` **không** ghép theo crop — nghĩa là nếu 2 cây cùng bị
  "Bệnh thối nhũn" thì đó là **cùng một** URI Disease (chia sẻ entity), có
  ý nghĩa ngữ nghĩa: tri thức về bệnh là dùng chung, không nhân bản theo
  từng cây.
- Chạy `python csv_to_rdf.py` để tạo/ghi đè `crops_data.ttl`, in ra tổng số
  triples.

## Truy vấn thực tế (SPARQL, qua `schema.py` + `sparql_client.py`)

GraphQL hiện chỉ expose 2 field:
- `Crop.growthStages` → SPARQL SELECT theo `hasGrowthStage` +
  `durationDays`.
- `Crop.diseases` → SPARQL SELECT theo `susceptibleTo`.

Có sẵn `Query.allCrops` (list toàn bộ tên cây có `rdf:type agri:Crop`)
nhưng **chưa có tool nào trong `tools.py` gọi tới `allCrops`** — Agent hiện
tại luôn cần biết tên cây cụ thể để truy vấn, không tự liệt kê được danh
sách cây hỗ trợ.

Không có resolver cho `attackedBy` (Pest), `requiresSoil`, `plantedInSeason`,
`treatedWith` dù dữ liệu RDF có đầy đủ — nếu bài báo muốn minh họa khả
năng "toàn diện" của ontology, cần làm rõ đây là phần dữ liệu có sẵn nhưng
pipeline truy vấn hiện tại (GraphQL → Agent) chưa khai thác hết.
