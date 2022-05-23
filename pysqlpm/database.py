from abc import ABC, abstractmethod
from typing import Any, List, Optional

from .password import Password

class DatabaseEntry:
    raw: List[Any]

    def __init__(self, raw: List[Any]=None, entry: "DatabaseEntry"=None):
        if raw:
            self.raw = raw

        if entry:
            self.raw = entry.raw

class PasswordEntry(DatabaseEntry):
    @property
    def url(self) -> str:
        return self.raw[0]

    @property
    def username(self) -> str:
        return self.raw[1]

    @property
    def password(self) -> str:
        return self.raw[2]

class Database(ABC):
    def __init__(self):
        self._initialize()

    @abstractmethod
    def execute(self, statement: str, *arguments: List[Any]) -> List[DatabaseEntry]:
        return None

    def _initialize(self) -> None:
        self.execute("CREATE TABLE IF NOT EXISTS Vault(url varchar(255), username varchar(255), password varchar(255))")
        self.execute("CREATE TABLE IF NOT EXISTS Config(key varchar(255), value varchar(255))")

    def _fetch_config(self, key: str) -> Optional[str]:
        entries = self.execute("SELECT value FROM Config WHERE key=?", key)

        if len(entries) == 0:
            return None

        return entries[0].raw[0]

    def fetch_challenge(self) -> Optional[str]:
        return self._fetch_config("challenge")

    def fetch_salt(self) -> Optional[str]:
        salt = self._fetch_config("salt")

        if not salt is None:
            return salt

        salt = Password.generate_salt()

        self.insert_salt(salt)

        return salt

    def fetch_iterations(self) -> Optional[int]:
        iterations = self._fetch_config("iterations")

        if not iterations is None:
            return int(iterations)

        iterations = 1000

        self.insert_iterations(iterations)

        return iterations

    def _insert_config(self, key: str, value: str):
        self.execute("INSERT INTO Config(key,value) VALUES (?,?)", key, value)

    def insert_challenge(self, challenge: str):
        self._insert_config("challenge", challenge)

    def insert_salt(self, salt: str):
        self._insert_config("salt", salt)

    def insert_iterations(self, iterations: int):
        self._insert_config("iterations", iterations)

    def fetch_accounts(self, url: str=None, username: str=None) -> List[PasswordEntry]:
        conditions = []

        if not url is None:
            conditions.append(("url", url))

        if not username is None:
            conditions.append(("username", username))

        query = "SELECT * FROM Vault"

        if len(conditions) > 0:
            query += " WHERE "
            query += " AND ".join(f"{label}=?" for label, value in conditions)

        return [PasswordEntry(entry=entry) for entry in self.execute(query, *[value for label, value in conditions])]

    def insert_account(self, url: str, username: str, encrypted_password: str) -> bool:
        return self.execute("INSERT INTO Vault(url, username, password) VALUES (?, ?, ?)", url, username, encrypted_password)

    def update_account(self, url: str, new_url: str=None, username: str=None, encrypted_password: str=None) -> bool:
        if username is None and encrypted_password is None:
            return None

        result = True

        if not username is None:
            self.execute("UPDATE Vault SET username=? WHERE url=?", username, url)

        if not encrypted_password is None:
            self.execute("UPDATE Vault SET password=? WHERE url=?", encrypted_password, url)

        if not new_url is None:
            self.execute("UPDATE Vault SET url=? WHERE url=?", new_url, url)

        return result

    def delete_account(self, url: str) -> bool:
        result = True

        self.execute("DELETE FROM Vault WHERE url=?", url)

        return result

import psycopg2

class PostgresDatabase(Database):
    connection: "psycopg2.connection"

    def __init__(self, name: str, user: str, password: str):
        self.connection = psycopg2.connect(f"dbname={name} user={user} password={password}")
        Database.__init__(self)

    def __del__(self):
       self.connection.commit()
       self.connection.close()

    def execute(self, statement: str, *arguments: List[Any]) -> List[DatabaseEntry]:
        cursor = self.connection.cursor()
        cursor.execute(statement, arguments)
        result = cursor.fetchall()
        cursor.close()

        return [DatabaseEntry(raw=data) for data in result]

import sqlite3

class SqliteDatabase(Database):
    connection: sqlite3.Connection

    def __init__(self, file: str):
        self.connection = sqlite3.connect(file)
        Database.__init__(self)

    def __del__(self):
        self.connection.commit()
        self.connection.close()

    def execute(self, statement: str, *arguments: List[Any]) -> List[DatabaseEntry]:
        cursor = self.connection.cursor()
        cursor.execute(statement, arguments)
        result = cursor.fetchall()
        cursor.close()

        return [DatabaseEntry(raw=data) for data in result]
