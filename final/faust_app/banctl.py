import json
import click
from kafka import KafkaProducer

BOOTSTRAP = ["kafka-a-1:9092","kafka-a-2:9092"]
TOPIC = "banlist_commands"
CAFILE = "/etc/faust/ca.pem"
STATE = "/opt/app/data/banlist.json"

def prod():
    return KafkaProducer(
        bootstrap_servers=BOOTSTRAP,
        security_protocol="SSL",
        ssl_cafile=CAFILE,
        value_serializer=lambda d: json.dumps(d).encode("utf-8"),
    )

def save_local(op, item):
    try:
        with open(STATE, "r") as f:
            st = json.load(f)
    except Exception:
        st = {"banned": []}
    if op == "add":
        if item not in st["banned"]:
            st["banned"].append(item)
    elif op == "remove":
        st["banned"] = [x for x in st["banned"] if x != item]
    with open(STATE, "w") as f:
        json.dump(st, f, ensure_ascii=False, indent=2)

@click.group()
def cli():
    """Управление бан-листом (с записью команды в Kafka)."""

@cli.command("add")
@click.argument("item")
def add(item):
    p = prod()
    p.send(TOPIC, {"op": "add", "item": item})
    p.flush()
    save_local("add", item)
    click.echo(f"Добавлено в бан-лист: {item}")

@cli.command("remove")
@click.argument("item")
def remove(item):
    p = prod()
    p.send(TOPIC, {"op": "remove", "item": item})
    p.flush()
    save_local("remove", item)
    click.echo(f"Убрано из бан-листа: {item}")

@cli.command("list")
def _list():
    try:
        with open(STATE, "r") as f:
            st = json.load(f)
    except Exception:
        st = {"banned": []}
    click.echo("\n".join(st["banned"]) or "(пусто)")

if __name__ == "__main__":
    cli()