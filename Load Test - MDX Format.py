import json
 
with open("excel_mdx_queries.json", encoding="utf-8-sig") as f:
    data = json.load(f)
 
converted = [{"query": e["Query"]} for e in data if e.get("Query")]
 
with open("excel_mdx_queries_converted.json", "w", encoding="utf-8") as f:
    json.dump(converted, f, indent=2)
 
print(f"{len(converted)} requêtes converties")