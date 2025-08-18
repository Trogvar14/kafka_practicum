import json
import os
import click
from confluent_kafka import Producer

BOOT = os.getenv("KAFKA_BOOTSTRAP", "kafka-a-1:9092,kafka-a-2:9092")
CA    = os.getenv("SSL_CAFILE", "/etc/faust/ca.pem")

def prod():
    return Producer({
        "bootstrap.servers": BOOT,
        "security.protocol": "SSL",
        "ssl.ca.location": CA,
        "client.id": "banctl",
    })

def send_cmd(op: str, name: str):
    p = prod()
    value = json.dumps({"op": op, "name": name})
    p.produce("banlist-cmds", value=value.encode("utf-8"))
    p.flush()

@click.group()
def cli(): ...

@cli.command("add")
@click.argument("name")
def add(name):
    send_cmd("add", name)
    click.echo(f"Added to ban: {name}")

@cli.command("remove")
@click.argument("name")
def remove(name):
    send_cmd("remove", name)
    click.echo(f"Removed from ban: {name}")

if __name__ == "__main__":
    cli()
