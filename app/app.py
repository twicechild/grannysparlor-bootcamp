"""
GreenLeaf Recipes — Flask Application
=======================================
A simple recipe sharing platform. This is the application you will deploy.
You do NOT need to modify this file — it is provided complete.

The app exposes:
  - GET  /          → HTML page listing recipes + add form
  - GET  /health    → JSON health check (returns 200 if app + DB are up)
  - GET  /recipes   → JSON list of all recipes
  - POST /recipes   → Create a new recipe (JSON: title, ingredients, instructions)

Database: PostgreSQL
Table: recipes (id, title, ingredients, instructions, created_at)

Configuration via environment variables:
  DB_HOST       — Postgres host (default: localhost)
  DB_PORT       — Postgres port (default: 5432)
  DB_NAME       — Database name (default: greenleaf)
  DB_USER       — Database user (default: greenleaf)
  DB_PASSWORD   — Database password (default: greenleaf)
"""

from __future__ import annotations

import os
import psycopg2
from flask import Flask, jsonify, render_template, request

app = Flask(__name__)


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def get_db_connection():
    """Open a new database connection using environment variables."""
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=os.environ.get("DB_PORT", "5432"),
        dbname=os.environ.get("DB_NAME", "greenleaf"),
        user=os.environ.get("DB_USER", "greenleaf"),
        password=os.environ.get("DB_PASSWORD", "greenleaf"),
    )


def init_db():
    """Create the recipes table if it doesn't exist."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recipes (
            id          SERIAL PRIMARY KEY,
            title       VARCHAR(200) NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            created_at  TIMESTAMPTZ DEFAULT NOW()
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


# ---------------------------------------------------------------------------
# Routes — UI
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Render the recipe list and add form."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, ingredients, instructions, created_at FROM recipes ORDER BY created_at DESC")
    recipes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("index.html", recipes=recipes)


# ---------------------------------------------------------------------------
# Routes — API
# ---------------------------------------------------------------------------

@app.route("/health")
def health():
    """Health check — verifies app and database are responding."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1")
        cur.close()
        conn.close()
        return jsonify(status="ok", database="connected"), 200
    except Exception:
        return jsonify(status="error", database="unreachable"), 503


@app.route("/recipes", methods=["GET"])
def list_recipes():
    """Return all recipes as JSON."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id, title, ingredients, instructions, created_at FROM recipes ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    recipes = [
        {
            "id": row[0],
            "title": row[1],
            "ingredients": row[2],
            "instructions": row[3],
            "created_at": row[4].isoformat() if row[4] else None,
        }
        for row in rows
    ]
    return jsonify(recipes), 200


@app.route("/recipes", methods=["POST"])
def create_recipe():
    """Create a new recipe from JSON body."""
    data = request.get_json()
    if not data or not data.get("title") or not data.get("ingredients") or not data.get("instructions"):
        return jsonify(error="Missing required fields: title, ingredients, instructions"), 400

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO recipes (title, ingredients, instructions) VALUES (%s, %s, %s) RETURNING id, created_at",
        (data["title"], data["ingredients"], data["instructions"]),
    )
    recipe_id, created_at = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return jsonify(id=recipe_id, title=data["title"], created_at=created_at.isoformat()), 201


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

# Initialize the database on import (works with both `python app.py` and gunicorn)
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)