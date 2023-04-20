import argparse
import asyncio
import os

import duckdb
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from Entities.Character import Character
from Services.BattleNet import BattleNet


def format_name(name: str) -> str:
    return name.lower().replace(" ", "-").replace("'", '')


async def get_characters(service: BattleNet, realm: str, guild: str) -> list[Character] | None:
    formatted_realm = format_name(realm)
    formatted_guild = format_name(guild)

    guild_data = await service.get_guild_data(formatted_realm, formatted_guild)

    tasks = [
        service.get_character_data(formatted_realm, char['character']['name'].lower())
        for char in guild_data['members']
    ]

    characters: list[Character] = [Character.from_nested_data(data) for data in
                                   await asyncio.gather(*tasks, return_exceptions=True)
                                   if not isinstance(data, Exception)]
    return characters


def insert_character_data(con, character: Character):
    con.execute("""
    INSERT INTO characters (
        id, race, gender, character_class, faction, level,
        active_spec, realm, guild, achievement_points,
        equipped_item_level, average_item_level
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      ON CONFLICT (id)
      DO UPDATE SET
        character_class = EXCLUDED.character_class
    """, (character.id, character.race, character.gender, character.character_class,
          character.faction, character.level, character.active_spec, character.realm,
          character.guild, character.achievement_points, character.equipped_item_level,
          character.average_item_level))


def create_table(con):
    con.execute("""
    CREATE TABLE IF NOT EXISTS characters (
        id INTEGER PRIMARY KEY,
        name TEXT,
        race TEXT,
        gender TEXT,
        character_class TEXT,
        faction TEXT,
        level INTEGER,
        active_spec TEXT,
        realm TEXT,
        guild TEXT,
        achievement_points INTEGER,
        equipped_item_level INTEGER,
        average_item_level INTEGER
    )
    """)


def display_characters(characters):
    console = Console()
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Name")
    table.add_column("Race")
    table.add_column("Class")
    table.add_column("Faction")
    table.add_column("Level")
    table.add_column("Spec")
    table.add_column("Realm")
    table.add_column("Guild")

    for char in characters:
        table.add_row(
            char.name,
            char.race,
            char.character_class,
            char.faction,
            str(char.level),
            char.active_spec,
            char.realm,
            char.guild
        )

    console.print(table)


async def main(arguments: argparse.Namespace):
    load_dotenv()

    # Access the variables and check if they are set
    client_id = os.environ.get('CLIENT_ID')
    client_secret = os.environ.get('CLIENT_SECRET')

    con = duckdb.connect('characters.duckdb')

    create_table(con)

    if not client_id or not client_secret:
        print("Error: CLIENT_ID and CLIENT_SECRET must be set")
    else:
        try:
            service = await BattleNet.create(client_id, client_secret)
            characters = await get_characters(service, arguments.realm, arguments.guild)

            if characters:
                for char in characters:
                    insert_character_data(con, char)
                con.commit()
                display_characters(characters)
        except ValueError as e:
            print(e)
        finally:
            if service is not None:
                await service.close()
            con.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Fetch character information for a given realm and guild.'
    )
    parser.add_argument('realm', type=str, help='The realm name.')
    parser.add_argument('guild', type=str, help='The guild name.')

    args = parser.parse_args()

    asyncio.run(main(args))
