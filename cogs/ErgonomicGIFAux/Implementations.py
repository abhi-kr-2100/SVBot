"""Implementations of commands in the ErgonomicGIF cog."""


from os import getenv
from random import choice

import psycopg2


def create_tables(users_table: str, registrations_table: str):
    """Create the required tables if they don't exist."""

    con = psycopg2.connect(getenv('DATABASE_URL'), sslmode='require')
    cur = con.cursor()

    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {users_table} (
            id          SERIAL PRIMARY KEY,
            member_id   BIGINT UNIQUE NOT NULL
        );
        """
    )

    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {registrations_table} (
            id          SERIAL PRIMARY KEY,
            keyword     VARCHAR(100) NOT NULL,
            url         VARCHAR(100) NOT NULL,
            user_id     INT NOT NULL,

            FOREIGN KEY (user_id) REFERENCES {users_table}(id)
                ON DELETE CASCADE
        );
        """
    )

    con.commit()

    cur.close()
    con.close()


def get_uid(users_table: str, member_id: int):
    """Return the id of row of the member with ID member_id on Discord."""

    con = psycopg2.connect(getenv('DATABASE_URL'), sslmode='require')
    cur = con.cursor()

    cur.execute(
        f"""
        INSERT INTO {users_table} (member_id) VALUES (%s)
        ON CONFLICT (member_id) DO NOTHING;
        """,
        (member_id,)
    )

    cur.execute(
        f"SELECT id FROM {users_table} WHERE member_id = %s", (member_id,)
    )

    con.commit()

    uid = cur.fetchone()[0]

    cur.close()
    con.close()

    return uid


def create_registration(regs_table: str, uid: int, key: str, url: str):
    """Create a registration for the given user."""

    con = psycopg2.connect(getenv('DATABASE_URL'), sslmode='require')
    cur = con.cursor()

    cur.execute(
        f"""
        INSERT INTO {regs_table} (keyword, url, user_id) VALUES (%s, %s, %s)
        """,
        (key, url, uid)
    )

    con.commit()

    cur.close()
    con.close()


def get_gif_url(regs_table: str, uid: int, key: str):
    """Get the GIF URL for the given key created by the given user."""

    con = psycopg2.connect(getenv('DATABASE_URL'), sslmode='require')
    cur = con.cursor()

    cur.execute(
        f"SELECT url FROM {regs_table} WHERE user_id = %s AND keyword = %s",
        (uid, key)
    )

    results = cur.fetchall()
    if not results:
        return None
    
    return choice(results)[0]