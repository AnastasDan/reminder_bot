import asyncio

import typer
from models import init_db

cli = typer.Typer()


@cli.command()
def db_init_models():
    """Инициализирует базу данных, создавая необходимые модели."""
    asyncio.run(init_db())
    print("Done")


if __name__ == "__main__":
    cli()
