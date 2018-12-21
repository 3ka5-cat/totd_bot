#!/usr/bin/env python
import click

import bot.import_data as import_data


@click.group()
def cmds():
    pass


@cmds.command()
@click.argument('tips_file', type=click.Path(exists=True))
def import_tips(tips_file):
    import_data.import_tips(tips_file)


if __name__ == '__main__':
    cmds()
