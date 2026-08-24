# schema.py
import strawberry
from sparql_client import run_sparql

@strawberry.type
class GrowthStage:
    name: str
    duration_days: int

@strawberry.type
class Disease:
    name: str

@strawberry.type
class Crop:
    name: str

    @strawberry.field
    def growth_stages(self) -> list[GrowthStage]:
        rows = run_sparql(f'''
            SELECT ?stageLabel ?duration WHERE {{
                ?crop rdfs:label "{self.name}"@vi .
                ?crop agri:hasGrowthStage ?stage .
                ?stage rdfs:label ?stageLabel ;
                       agri:durationDays ?duration .
            }}
        ''')
        return [
            GrowthStage(name=r["stageLabel"]["value"], duration_days=int(r["duration"]["value"]))
            for r in rows
        ]

    @strawberry.field
    def diseases(self) -> list[Disease]:
        rows = run_sparql(f'''
            SELECT ?diseaseLabel WHERE {{
                ?crop rdfs:label "{self.name}"@vi .
                ?crop agri:susceptibleTo ?disease .
                ?disease rdfs:label ?diseaseLabel .
            }}
        ''')
        return [Disease(name=r["diseaseLabel"]["value"]) for r in rows]

@strawberry.type
class Query:
    @strawberry.field
    def crop(self, name: str) -> Crop:
        return Crop(name=name)

    @strawberry.field
    def all_crops(self) -> list[Crop]:
        rows = run_sparql('''
            SELECT ?label WHERE {
                ?crop a agri:Crop ; rdfs:label ?label .
            }
        ''')
        return [Crop(name=r["label"]["value"]) for r in rows]

schema = strawberry.Schema(query=Query)