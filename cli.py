"""Access the database."""
import cmd
import decimal
import json
import random
import string

import boto3


def _index(pool=string.hexdigits):
    return "".join(random.choice(pool) for _ in range(8))


STATS = ("HP", "Attack", "Defense", "Special Attack", "Special Defense", "Speed")  # noqa


def _statline(value="ivs", maximum=31):
    statline = input(f"{value} (HP/Atk/Def/SpA/SpD/Spe):")
    split_statline = statline.split("/")
    stats = ((stat, int(value)) for stat, value in zip(STATS, split_statline)
             if value.isdigit())
    return dict(stats)


def _moves():
    moves = {}
    for num in range(1, 5):
        move = input(f"Move {num}: ")
        acquired = input(f"Uncheck move (y)? ").lower() != "y"
        moves[move] = acquired

    return moves


def _default(node):
    if isinstance(node, decimal.Decimal):
        return int(node)
    return json.JSONDecoder.encode(node)


def _pretty(item):
    """Pretty print a record from DynamoDB."""
    ivs = "IVs: \n"
    for stat, value in item.get("ivs", {}).items():
        ivs += f"  {value} {stat}\n"

    evs = "EVs: \n"
    for stat, value in item.get("evs", {}).items():
        evs += f"  {value} {stat}\n"

    moves = "\n"
    for move, acquired in item.get("moves", {}).items():
        moves += f"  [{'x' if acquired else ' '}] {move}\n"

    return f"""
-------------------------------------------------------------------------------
{item['Pokemon']} - {item.get('Index')}
{item.get('nickname', item['Pokemon'])}

Ability: {item.get('ability')}
Nature: {item.get('nature')}
{ivs}
{evs}
{moves}
"""


class RosterCmd(cmd.Cmd):
    """Shell for reading pokemon roster."""

    def __init__(self, tablename):
        """Instantiate with name of table to connect to."""
        dynamodb = boto3.resource("dynamodb")
        self._table = dynamodb.Table(table_name)
        super().__init__()

    def _print(self, *args, **kwargs):
        """Print to self.stdout."""
        kwargs = {
            **kwargs,
            "file": self.stdout,
        }
        print(*args, **kwargs)

    def do_scan(self, arg):
        """Scan the table for pokemon entries."""
        results = self._table.scan()
        for item in results["Items"]:
            self._print(_pretty(item))

    # TODO Find a more intiutive way to hand-enter this data
    def do_insert(self, pokemon):
        """Begin an insert for this record."""
        while input(f"Insert a new record for \"{pokemon}\" (y?): ") == "y":
            self._table.put_item(Item={
                "Pokemon": pokemon,  # TODO Validate against a list
                "Index": _index(),
                "nickname": input("nickname: "),
                "ability": input("ability: "),  # TODO Validate against a list
                "nature": input("nature: "),  # TODO Validate against a list
                "ivs": _statline("ivs", 31),
                "evs": _statline("evs", 255),
                # TODO does order of moves matter?
                "moves": _moves(),
                "egg_moves": input("egg moves (,-delim): ").split(","),
            })

    def do_query(self, pokemon):
        """Query for a pokemon."""
        results = self._table.query(
            Select="ALL_ATTRIBUTES",
            KeyConditionExpression="Pokemon = :pokemon AND #index > :index",
            ExpressionAttributeNames={
                "#index": "Index",
            },
            ExpressionAttributeValues={
                ":pokemon": pokemon,
                ":index": "0",
            }
        )

        for item in results["Items"]:
            self._print(_pretty(item))


if __name__ == "__main__":
    cloudformation = boto3.client("cloudformation")
    table_name = next(e["Value"] for e in cloudformation.list_exports()["Exports"]  # noqa
                      if e["Name"] == "roster-table")

    shell = RosterCmd(table_name)
    shell.cmdloop()
