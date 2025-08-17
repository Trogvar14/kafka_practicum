import click, psycopg2, json, uuid
from confluent_kafka import Producer

P = Producer({
    "bootstrap.servers":"localhost:19092",
    "security.protocol":"ssl",
    "ssl.ca.location":"certs/ca.crt",
    "client.id":"client-cli",
})

def log_query(user_id, q):
    evt = {"user_id":user_id, "query":q}
    P.produce("client.queries", key=user_id.encode(), value=json.dumps(evt).encode()); P.flush(1)

@click.group()
def cli(): pass

@cli.command()
@click.option("--user", "user_id", default=lambda: str(uuid.uuid4())[:8])
@click.argument("name", nargs=-1, required=True)
def search(user_id, name):
    q = " ".join(name)
    log_query(user_id, q)
    conn = psycopg2.connect("host=localhost dbname=marketplace user=pguser password=pgpass")
    cur = conn.cursor()
    cur.execute("SELECT product_id,name,category,brand,price,currency FROM products WHERE name ILIKE %s ORDER BY similarity(name,%s) DESC LIMIT 10", (f"%{q}%", q))
    rows = cur.fetchall(); cur.close(); conn.close()
    click.echo(f"User={user_id}, query='{q}'")
    for r in rows:
        click.echo(f"- [{r[0]}] {r[1]} | {r[2]} / {r[3]} — {r[4]} {r[5]}")

@cli.command()
@click.option("--user","user_id", required=True, help="user id из поиска")
def recs(user_id):
    # Рекоммендации складываются аналитикой в таблицу recommendations
    conn = psycopg2.connect("host=localhost dbname=marketplace user=pguser password=pgpass")
    cur = conn.cursor()
    cur.execute("SELECT items FROM recommendations WHERE user_id=%s ORDER BY ts DESC LIMIT 1", (user_id,))
    row = cur.fetchone(); cur.close(); conn.close()
    if not row:
        click.echo("Пока нет рекомендаций. Попробуй выполнить поиск, подождать аналитику.")
    else:
        items = row[0]
        click.echo(f"Рекомендации для {user_id}:")
        for it in items:
            click.echo(f"- {it['product_id']}: {it['name']}")
if __name__=="__main__":
    cli()
