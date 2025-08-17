import ssl
import faust

# --- SSL для подключения к Kafka (корневой PEM) ---
def ssl_ctx() -> ssl.SSLContext:
    return ssl.create_default_context(cafile="/etc/faust/ca.pem")

# --- Faust App ---
app = faust.App(
    "banlist-filter",
    broker="kafka://kafka-a-1:9092,kafka-a-2:9092",   # строго строка, не список!
    value_serializer="json",
    broker_credentials=ssl_ctx(),
)

# --- Топики ---
products = app.topic("products")                # вход: товары от магазинов
allowed  = app.topic("products_allowed")        # выход: разрешённые товары
ban_cmds = app.topic("banlist_commands")        # вход: команды управления бан-листом

# Храним бан-лист в Table: ключ — normalized имя/sku товара, значение — True
banlist = app.Table("banlist", default=bool)

def norm(s: str) -> str:
    return (s or "").strip().lower()

# --- Агент управления бан-листом ---
@app.agent(ban_cmds)
async def handle_ban_cmds(stream):
    async for msg in stream:
        # ожидаем {"op": "add"|"remove", "item": "название или sku"}
        op   = (msg or {}).get("op")
        item = norm((msg or {}).get("item", ""))
        if not item:
            continue
        if op == "add":
            banlist[item] = True
            app.log.info("BAN ADD: %r", item)
        elif op == "remove":
            banlist.pop(item, None)
            app.log.info("BAN REMOVE: %r", item)

# --- Агент фильтрации товаров ---
@app.agent(products)
async def filter_products(stream):
    async for p in stream:
        # ожидаем json с хотя бы name или sku
        name = norm((p or {}).get("name", ""))
        sku  = norm((p or {}).get("sku", ""))
        key  = name or sku
        if not key:
            continue
        if banlist.get(key, False):
            app.log.info("BLOCKED: %s", key)
            continue
        await allowed.send(value=p)
        app.log.debug("ALLOWED: %s", key)