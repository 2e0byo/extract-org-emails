from itertools import chain
from pathlib import Path
from subprocess import run
from typing import Iterable, Optional

import click
from orgparse import load
from orgparse.extra import Table
from orgparse.node import OrgNode


def find_module(root: OrgNode, title: str, subheading: str = None):
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


def make_table(section: OrgNode):
    return Table(section.body.strip().splitlines())


def process_module(root, title: str, subheading: str) -> Iterable[str]:
    mod = find_module(root, title, subheading)
    tables = (make_table(x) for x in mod[1:] if x.heading.lower() == "students")
    return chain.from_iterable(extract_emails(t) for t in tables)


def find_registers(root: OrgNode):
    return [make_table(x) for x in root[1:] if x.heading.lower().strip() == "students"]


def get_seminars(row: dict):
    seminars = []
    for k in row.keys():
        try:
            int(k)
            seminars.append(k)
        except (TypeError, ValueError):
            pass
    return seminars


def get_missed(row: dict, seminars: list, skip: int):
    return len([1 for k in seminars if not row[k].strip() and int(k) > skip])


def get_slackers(register: Table, skip: int, thresh: int = 2):
    dicts = register.as_dicts
    first = next(iter(dicts))
    seminars = get_seminars(first)
    return (
        row | dict(Missed=missed, Emailed=has_emailed(row["Email"]))
        for row in chain((first,), dicts)
        if not row[seminars[-1]].strip()
        if (missed := get_missed(row, seminars, skip)) >= thresh
    )


def get_all_slackers(root: OrgNode, skip: int, thresh: int = 2):
    return chain.from_iterable(
        get_slackers(x, skip, thresh) for x in find_registers(root)
    )


def has_emailed(email: str) -> str:
    """Find out if the student emailed me in the last two weeks."""
    querystr = f"f:{email} date:14d..now"
    out = run(
        ["mu", "find", querystr, "-f", "s"], capture_output=True, encoding="utf8"
    ).stdout.splitlines()
    return f"{out[0]} ({len(out)})" if out else ""


def format_table(rows: list[dict], keys: list = None):
    if not isinstance(rows, list):
        rows = list(rows)

    keys = keys or list(rows[0].keys())
    rows = list(rows)
    widths = {k: max(chain((len(str(r[k])) for r in rows), [len(k)])) for k in keys}
    header = [
        "|" + "|".join(f" {k:<{widths[k]}} " for k in keys) + "|",
        "|" + "|".join("-" * (widths[k] + 2) for k in keys) + "|",
    ]
    lines = ["|" + "|".join(f" {r[k]:<{widths[k]}} " for k in keys) + "|" for r in rows]
    return "\n".join(chain(header, lines))


common = {}


@click.group()
@click.argument("path")
@click.argument("module")
@click.option("--subheading", help="Subheading to narrow search.")
def cli(path: str, module: str, subheading: Optional[str]):
    common["root"] = load(Path(path).expanduser().resolve())
    common["module"] = module
    common["subheading"] = subheading


@cli.command()
def emails():
    emails = process_module(common["root"], common["module"], common["subheading"])
    print("Bcc:", ", ".join(emails))


@cli.command()
@click.argument("skip")
@click.option("--thresh", help="Threshold.", default="2")
@click.option("--bcc/--no-bcc", help="Generate bcc", default=False)
def slackers(skip: str, thresh: str, bcc: bool = None):
    module = find_module(common["root"], common["module"], common["subheading"])
    slackers = get_all_slackers(module, int(skip), int(thresh))
    if not bcc:
        print(format_table(slackers, ("Name", "Surname", "Email", "Missed", "Emailed")))
    else:
        print("Bcc: " + ",".join(x["Email"] for x in slackers))


if __name__ == "__main__":
    cli()
