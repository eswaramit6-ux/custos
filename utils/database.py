import sqlite3
import pandas as pd
from datetime import datetime
import os

DB_PATH = "custos_data.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            source TEXT DEFAULT 'manual',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS budgets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL UNIQUE,
            monthly_limit REAL NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_name TEXT NOT NULL,
            target_amount REAL NOT NULL,
            current_amount REAL DEFAULT 0,
            deadline TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()

def add_expense(date, amount, category, description="", source="manual"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO expenses (date, amount, category, description, source)
        VALUES (?, ?, ?, ?, ?)
    """, (date, amount, category, description, source))
    conn.commit()
    conn.close()

def get_expenses(limit=100):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM expenses ORDER BY date DESC LIMIT ?",
        conn, params=(limit,)
    )
    conn.close()
    return df

def get_expenses_by_month(year, month):
    conn = get_connection()
    df = pd.read_sql_query(
        "SELECT * FROM expenses WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?",
        conn, params=(str(year), str(month).zfill(2))
    )
    conn.close()
    return df

def get_category_totals(year=None, month=None):
    conn = get_connection()
    if year and month:
        df = pd.read_sql_query("""
            SELECT category, SUM(amount) as total
            FROM expenses
            WHERE strftime('%Y', date) = ? AND strftime('%m', date) = ?
            GROUP BY category ORDER BY total DESC
        """, conn, params=(str(year), str(month).zfill(2)))
    else:
        df = pd.read_sql_query("""
            SELECT category, SUM(amount) as total
            FROM expenses GROUP BY category ORDER BY total DESC
        """, conn)
    conn.close()
    return df

def set_budget(category, monthly_limit):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO budgets (category, monthly_limit)
        VALUES (?, ?)
        ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit
    """, (category, monthly_limit))
    conn.commit()
    conn.close()

def get_budgets():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM budgets", conn)
    conn.close()
    return df

def add_goal(goal_name, target_amount, deadline=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO financial_goals (goal_name, target_amount, deadline)
        VALUES (?, ?, ?)
    """, (goal_name, target_amount, deadline))
    conn.commit()
    conn.close()

def get_goals():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM financial_goals", conn)
    conn.close()
    return df

def delete_expense(expense_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
