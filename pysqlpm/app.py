from abc import ABC
import argparse
from typing import Any
import getpass

from .database import Database
from .password import Password

class App(ABC):
    db: Database
    password: Password

    def __init__(self, db: Database):
        self.db = db

    def _init_password(self, master: str):
        salt = self.db.fetch_salt()
        iterations = self.db.fetch_iterations()
        self.password = Password(master=master, salt=salt, iterations=iterations)

    def run(self):
        challenge = self.db.fetch_challenge()

        if challenge is None:
            self.db.insert_challenge(self.password.generate_challenge())
        elif not self.password.validate_challenge(challenge):
            raise Exception("Master password is invalid.") 

class CLIApp(App):
    def parse_arguments(self) -> Any:
        parser = argparse.ArgumentParser(description="Password Manager Vault: Manage URLs, Usernames, and Passwords.")

        subparsers = parser.add_subparsers(dest="mode")

        query_parser = subparsers.add_parser("query", help="Query database with search parameters.")
        query_parser.add_argument("-u", "--url", type=str)
        query_parser.add_argument("-n", "--username", type=str)

        add_parser = subparsers.add_parser("add", help="Insert password in database.")
        add_parser.add_argument("-u", "--url", type=str, required=True)
        add_parser.add_argument("-n", "--name", type=str, required=True)
        add_parser.add_argument("-p", "--password", type=str)

        update_parser = subparsers.add_parser("update", help="Update password entry.")
        update_parser.add_argument("old_url", type=str)
        update_parser.add_argument("-u", "--url", type=str)
        update_parser.add_argument("-n", "--username", type=str)
        update_parser.add_argument("-p", "--password", type=str)

        delete_parser = subparsers.add_parser("delete", help="Delete password entry.")
        delete_parser.add_argument("url", type=str)

        return parser.parse_args()

    def run(self):
        args = self.parse_arguments()

        self._init_password(getpass.getpass("Master Password: "))
        App.run(self)

        if args.mode == "query":
            entries = self.db.fetch_accounts(url=args.url, username=args.username)

            for entry in entries:
                decrypted_password = self.password.decrypt(entry.password)

                print(f"[Query] URL: {entry.url}, Username: {entry.username}, Password: {decrypted_password}")
        elif args.mode == "add":
            url = args.url
            username = args.username
            password = args.password

            if password is None:
                password = Password.generate_password(20)

            encrypted_password = self.password.encrypt(password)

            self.db.insert_account(url, username, encrypted_password)

            print(f"[Add] URL: {url}, Username: {username}, Password: {password}")
        elif args.mode == "update":
            url = args.old_url
            new_url = args.url
            username = args.username
            password = args.password

            if not password is None:
                password = self.password.encrypt(password)

            self.db.update_account(url, new_url, username, password)

            print(f"[Update] URL: {url} -> {new_url}, Username: {username}, Password: {password}")
        elif args.mode == "delete":
            url = args.url

            self.db.delete_account(url)

            print(f"[Delete] URL: {url}")
