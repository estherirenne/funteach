"""
Koneksi dan query PostgreSQL (memakai psycopg 3).
Konfigurasi dibaca dari environment (diisi docker compose dari file .env).
"""
import os
import time

import psycopg
from psycopg.rows import dict_row

# Struktur tabel. "IF NOT EXISTS" membuat aman dijalankan berulang kali.
SCHEMA = """
CREATE TABLE IF NOT EXISTS lessons (
    id SERIAL PRIMARY KEY,
    judul TEXT NOT NULL,
    isi TEXT NOT NULL,
    jenjang TEXT NOT NULL,
    total_kalimat INT NOT NULL,
    kalimat_bermasalah INT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS students (
    id SERIAL PRIMARY KEY,
    nama TEXT NOT NULL,
    jenjang TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS student_notes (
    id SERIAL PRIMARY KEY,
    student_id INT NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    jenis TEXT NOT NULL CHECK (jenis IN ('perkembangan', 'ditingkatkan', 'dipertahankan')),
    isi TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
"""


def get_conn():
    """Buka koneksi baru. Host default 'db' = NAMA SERVICE di docker-compose.yml (bukan localhost)."""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        dbname=os.getenv("POSTGRES_DB"),
        row_factory=dict_row,  # hasil query berupa dictionary, mudah diubah ke JSON
    )


def init_db(retries=30, delay=2):
    """Buat tabel saat aplikasi start. Diulang beberapa kali kalau database belum siap."""
    last_error = None
    for _ in range(retries):
        try:
            # "with" memastikan koneksi ditutup, dan perubahan di-commit kalau tidak ada error
            with get_conn() as conn:
                conn.execute(SCHEMA)
            return
        except psycopg.OperationalError as e:
            last_error = e
            time.sleep(delay)
    raise RuntimeError(f"Database tidak bisa dihubungi: {last_error}")


# ---------------- Pelajaran (lessons) ----------------
def save_lesson(judul, isi, jenjang, total_kalimat, kalimat_bermasalah):
    with get_conn() as conn:
        # Tanda %s adalah parameter: nilai dikirim terpisah dari SQL (mencegah SQL injection)
        row = conn.execute(
            """
            INSERT INTO lessons (judul, isi, jenjang, total_kalimat, kalimat_bermasalah)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id, created_at
            """,
            (judul, isi, jenjang, total_kalimat, kalimat_bermasalah),
        ).fetchone()
    return row


def list_lessons(limit=20):
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT id, judul, jenjang, total_kalimat, kalimat_bermasalah, created_at
            FROM lessons ORDER BY id DESC LIMIT %s
            """,
            (limit,),
        ).fetchall()


# ---------------- Murid (students) ----------------
def create_student(nama, jenjang):
    with get_conn() as conn:
        return conn.execute(
            "INSERT INTO students (nama, jenjang) VALUES (%s, %s) "
            "RETURNING id, nama, jenjang, created_at",
            (nama, jenjang),
        ).fetchone()


def list_students():
    with get_conn() as conn:
        return conn.execute(
            "SELECT id, nama, jenjang, created_at FROM students ORDER BY nama"
        ).fetchall()


def get_student(student_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT id, nama, jenjang, created_at FROM students WHERE id = %s",
            (student_id,),
        ).fetchone()


# ---------------- Catatan murid (student_notes) ----------------
def add_note(student_id, jenis, isi):
    with get_conn() as conn:
        return conn.execute(
            "INSERT INTO student_notes (student_id, jenis, isi) VALUES (%s, %s, %s) "
            "RETURNING id, student_id, jenis, isi, created_at",
            (student_id, jenis, isi),
        ).fetchone()


def list_notes(student_id):
    with get_conn() as conn:
        return conn.execute(
            "SELECT id, jenis, isi, created_at FROM student_notes "
            "WHERE student_id = %s ORDER BY id DESC",
            (student_id,),
        ).fetchall()
