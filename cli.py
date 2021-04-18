"""Access the database."""
import sys

import boto3


if __name__ == "__main__":
    cloudformation = boto3.client("cloudformation")
    table_name = next(e["Value"] for e in cloudformation.list_exports()["Exports"]  # noqa
                      if e["Name"] == "roster-table")

    dynamodb = boto3.resource("dynamodb")
    roster_table = dynamodb.Table(table_name)

    if sys.argv[-1] == "put":
        roster_table.put_item(Item={
            "Pokemon": "Charmander",
            "Index": "0"
        })
    else:
        results = roster_table.scan()
        print([repr(item) for item in results["Items"]])
