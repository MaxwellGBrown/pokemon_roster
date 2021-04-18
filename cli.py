"""Access the database."""
import cmd
import json
import random
import string

import boto3


def _index(pool=string.hexdigits):
    return "".join(random.choice(pool) for _ in range(8))


def _ivs():
    ivs = input("ivs (HP/Atk/Def/SpA/SpD/Spe):")
    hp, atk, de, spa, spd, spe = ivs.split("/")
    return {
        "HP": hp,
        "Attack": atk,
        "Defense": de,
        "Special Attack": spa,
        "Special Defense": spd,
        "Speed": spe
    }


def _evs():
    evs = input("evs (HP/Atk/Def/SpA/SpD/Spe):")
    hp, atk, de, spa, spd, spe = evs.split("/")
    return {
        "HP": hp,
        "Attack": atk,
        "Defense": de,
        "Special Attack": spa,
        "Special Defense": spd,
        "Speed": spe
    }


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
            self._print(json.dumps(item, indent=2))

    def do_insert(self, pokemon):
        """Begin an insert for this record."""
        self._table.put_item(Item={
            "Pokemon": pokemon,
            "Index": _index(),
            "nickname": input("nickname: "),
            "ability": input("ability: "),
            "nature": input("nature: "),
            "ivs": _ivs(),
            "evs": _evs(),
            "moves": [input(f"move {i}: ") for i in range(4)]
        })


if __name__ == "__main__":
    cloudformation = boto3.client("cloudformation")
    table_name = next(e["Value"] for e in cloudformation.list_exports()["Exports"]  # noqa
                      if e["Name"] == "roster-table")

    shell = RosterCmd(table_name)
    shell.cmdloop()
