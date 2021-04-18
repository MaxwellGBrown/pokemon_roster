"""Access the database."""
import cmd
import json
import sys

import boto3




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
        print(arg)
        print(dir(self))

        results = self._table.scan()
        for item in results["Items"]:
            print(json.dumps(item, indent=2))

    def do_insert(self, pokemon):
        """Begin an insert for this record."""
        index = input("Index >>> ")
        self._table.put_item(Item={
            "Pokemon": pokemon,
            "Index": index
        })


if __name__ == "__main__":
    cloudformation = boto3.client("cloudformation")
    table_name = next(e["Value"] for e in cloudformation.list_exports()["Exports"]  # noqa
                      if e["Name"] == "roster-table")

    shell = RosterCmd(table_name)
    shell.cmdloop()
