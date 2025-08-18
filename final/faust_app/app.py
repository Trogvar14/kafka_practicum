import os
import ssl
import faust

class Product(faust.Record, serializer="json"):
    id: str
    name: str
    price: float
    shop_id: str = ""

class BanCmd(faust.Record, serializer="json"):
    op: str   # add|remove|list
    name: str = ""

BROKER = os.getenv("FAUST_BROKER", "kafka://kafka-a-1:9092,kafka-a-2:9092")
CAFILE = os.getenv("FAUST_SSL_CAFILE", "/etc/faust/ca.pem")
CHECK_HOST = os.getenv("FAUST_SSL_CHECK_HOSTNAME", "true").lower() == "true"

def build_ssl_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context(cafile=CAFILE)
    if not CHECK_HOST:
        ctx.check_hostname = False
    return ctx

ssl_ctx = build_ssl_ctx()

app = faust.App(
    "banlist-filter",
    broker=BROKER,                 # ВАЖНО: обычный kafka://
    broker_credentials=ssl_ctx,    # допустимо передавать ssl.SSLContext
)
# TLS для aiokafka
app.conf.producer_client_kwargs = {"security_protocol": "SSL", "ssl_context": ssl_ctx}
app.conf.consumer_client_kwargs = {"security_protocol": "SSL", "ssl_context": ssl_ctx}
# если вдруг будет ошибка по hostname/SAN — можно на время ослабить проверку:
# app.conf.ssl_check_hostname = False
# app.conf.ssl_endpoint_identification_algorithm = ""

products_topic = app.topic("shop.products.raw", value_type=Product)
ban_cmds_topic = app.topic("shop.banned", value_type=BanCmd)
filtered_topic = app.topic("shop.products.filtered", value_type=Product)

banlist = app.Table("banlist", key_type=str, value_type=bool, default=False, partitions=1)

@app.agent(ban_cmds_topic)
async def handle_ban_cmds(stream):
    async for cmd in stream:
        op = (cmd.op or "").lower()
        name = (cmd.name or "").strip()
        if op == "add" and name:
            banlist[name] = True
            print(f"[banlist] add: {name}")
        elif op == "remove" and name:
            banlist.pop(name, None)
            print(f"[banlist] remove: {name}")
        elif op == "list":
            print("[banlist] current:", [k for k, v in banlist.items() if v])
        else:
            print("[banlist] unknown cmd:", cmd)

@app.agent(products_topic)
async def filter_products(stream):
    async for p in stream:
        if not banlist.get(p.name, False):
            await filtered_topic.send(value=p)
        else:
            print(f"[filter] blocked banned product: {p.name}")
