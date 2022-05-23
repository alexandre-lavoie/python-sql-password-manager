from pysqlpm.app import CLIApp
from pysqlpm.database import PostgresDatabase, SqliteDatabase

def main():
    # db = PostgresDatabase(name="VaultDB", user="postgres", password="****")
    db = SqliteDatabase(file="vault.db")

    app = CLIApp(db=db)

    app.run()

if __name__ == "__main__":
    main()
