# csv_to_rdf.py
import csv
from rdflib import Graph, Namespace, Literal, RDF, RDFS

# ⚠️ Đổi URI này khớp với Ontology IRI thật của bạn trong Protégé
AGRI = Namespace("http://www.semanticweb.org/admin/ontologies/2026/7/untitled-ontology-2#")

g = Graph()
g.bind("agri", AGRI)

def uri(text):
    """Chuyển tên tiếng Việt thành URI hợp lệ (bỏ dấu cách, ký tự đặc biệt)"""
    return text.strip().replace(" ", "_")

with open("crops_data.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        crop_uri = AGRI[uri(row["crop_name"])]
        stage_uri = AGRI[f'{uri(row["crop_name"])}_{uri(row["growth_stage"])}']
        disease_uri = AGRI[uri(row["disease"])]
        pest_uri = AGRI[uri(row["pest"])]
        soil_uri = AGRI[uri(row["soil_type"])]
        climate_uri = AGRI[uri(row["climate"])]
        season_uri = AGRI[uri(row["season"])]
        fertilizer_uri = AGRI[uri(row["fertilizer"])]

        # Crop
        g.add((crop_uri, RDF.type, AGRI[row["crop_type"]]))  # gán đúng subclass
        g.add((crop_uri, RDFS.label, Literal(row["crop_name"], lang="vi")))

        # GrowthStage
        g.add((stage_uri, RDF.type, AGRI.GrowthStage))
        g.add((stage_uri, RDFS.label, Literal(row["growth_stage"], lang="vi")))
        g.add((stage_uri, AGRI.durationDays, Literal(int(row["stage_duration"]))))
        g.add((crop_uri, AGRI.hasGrowthStage, stage_uri))

        # Disease
        g.add((disease_uri, RDF.type, AGRI.Disease))
        g.add((disease_uri, RDFS.label, Literal(row["disease"], lang="vi")))
        g.add((crop_uri, AGRI.susceptibleTo, disease_uri))

        # Pest
        g.add((pest_uri, RDF.type, AGRI.Pest))
        g.add((pest_uri, RDFS.label, Literal(row["pest"], lang="vi")))
        g.add((crop_uri, AGRI.attackedBy, pest_uri))

        # SoilType
        g.add((soil_uri, RDF.type, AGRI.SoilType))
        g.add((soil_uri, RDFS.label, Literal(row["soil_type"], lang="vi")))
        g.add((crop_uri, AGRI.requiresSoil, soil_uri))

        # ClimateCondition
        g.add((climate_uri, RDF.type, AGRI.ClimateCondition))
        g.add((climate_uri, RDFS.label, Literal(row["climate"], lang="vi")))

        # Season
        g.add((season_uri, RDF.type, AGRI.Season))
        g.add((season_uri, RDFS.label, Literal(row["season"], lang="vi")))
        g.add((crop_uri, AGRI.plantedInSeason, season_uri))

        # FertilizerType
        g.add((fertilizer_uri, RDF.type, AGRI.FertilizerType))
        g.add((fertilizer_uri, RDFS.label, Literal(row["fertilizer"], lang="vi")))
        g.add((disease_uri, AGRI.treatedWith, fertilizer_uri))

g.serialize(destination="crops_data.ttl", format="turtle")
print(f"Đã tạo {len(g)} triples từ {reader.line_num - 1} dòng dữ liệu")