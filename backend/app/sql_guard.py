import re
ALLOWED_TABLES={"business_metrics"}
ALLOWED_FUNCTIONS={"sum","count","avg","min","max"}
BLOCKED=re.compile(r"\b(insert|update|delete|drop|alter|create|truncate|grant|revoke|copy|call|execute|vacuum|attach|pragma|set|reset|listen|notify)\b",re.I)
def validate_readonly_sql(sql: str) -> str:
    q=sql.strip().rstrip(";")
    if not re.match(r"^select\b",q,re.I): raise ValueError("Only a single SELECT query is permitted")
    if len(re.findall(r"\bselect\b",q,re.I)) != 1: raise ValueError("Nested queries are not permitted")
    if BLOCKED.search(q) or "--" in q or "/*" in q or ";" in q: raise ValueError("Unsafe SQL rejected")
    tables={x.lower() for x in re.findall(r"\b(?:from|join)\s+([a-zA-Z_][a-zA-Z0-9_]*)",q,re.I)}
    if not tables or not tables.issubset(ALLOWED_TABLES): raise ValueError("Query references a non-allowlisted table")
    functions={x.lower() for x in re.findall(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",q)}
    if not functions.issubset(ALLOWED_FUNCTIONS): raise ValueError("Query contains a non-allowlisted function")
    if not re.search(r"\blimit\s+\d+\b",q,re.I): q += " LIMIT 100"
    return q
