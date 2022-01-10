from itertools import chain
from pathlib import Path
from typing import Iterable, Optional

import click
from orgparse import load
from orgparse.extra import Table


def find_module(root, title: str, subheading: str = None):
    title = title.lower()
    candidates = (x for x in root[1:] if x.heading.lower() == title)
    if subheading:
        subheading = subheading.lower()
        return next(
            x
            for candidate in candidates
            for x in candidate
            if subheading in x.heading.lower()
        )
    else:
        return next(candidates)


def extract_emails(table: Table) -> Iterable[str]:
    header, *others = table.rows
    email_col = [x.lower().strip() for x in header].index("email")
    return (row[email_col].strip() for row in others if "@" in row[email_col])


def process_module(root, title: str, subheading: str) -> Iterable[str]:
    mod = find_module(root, title, subheading)
    tables = (
        Table(x.body.strip().splitlines())
        for x in mod[1:]
        if x.heading.lower() == "students"
    )
    return chain.from_iterable(extract_emails(t) for t in tables)


@click.command()
@click.argument("path")
@click.argument("module")
@click.option("--subheading", help="Subheading to narrow search.")
def main(path: str, module: str, subheading: Optional[str]):
    root = load(Path(path).expanduser().resolve())
    emails = process_module(root, module, subheading)
    print("Bcc:", ", ".join(emails))


if __name__ == "__main__":
    main()
