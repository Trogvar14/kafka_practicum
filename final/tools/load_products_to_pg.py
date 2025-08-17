import json, psycopg2, sys

conn = psycopg2.connect("host=localhost dbname=marketplace user=pguser password=pgpass")
cur = conn.cursor()
with open(sys.argv[1] if len(sys.argv)>1 else "data/products.jsonl","r",encoding="utf-8") as f:
    for line in f:
        if not line.strip(): continue
        o = json.loads(line)
        cur.execute("""
            INSERT INTO products(product_id,name,description,category,brand,price,currency)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (product_id) DO UPDATE SET
              name=EXCLUDED.name, description=EXCLUDED.description,
              category=EXCLUDED.category, brand=EXCLUDED.brand,
              price=EXCLUDED.price, currency=EXCLUDED.currency
        """, (o["product_id"], o["name"], o["description"], o["category"], o["brand"], o["price"]["amount"], o["price"]["currency"]))
conn.commit(); cur.close(); conn.close()
print("Loaded.")
