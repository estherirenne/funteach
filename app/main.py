"""
FunTeach - asisten persiapan mengajar untuk calon instruktur coding anak.
Endpoint API + halaman web sederhana, dengan data disimpan di PostgreSQL.
"""
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from . import db
from .analyzer import analyze

STATIC_DIR = Path(__file__).parent / "static"

Jenjang = Literal["sd_pemula", "sd_lanjut", "smp_sma"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dijalankan sekali saat aplikasi start: pastikan tabel database sudah ada
    db.init_db()
    yield


app = FastAPI(title="FunTeach", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# ---------------- Model input (validasi otomatis oleh FastAPI/Pydantic) ----------------
# Input yang tidak valid (kosong, jenjang salah) otomatis dibalas status 422.
class AnalyzeIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)  # spasi di awal/akhir dibuang
    judul: str = Field(min_length=1, max_length=100)
    isi: str = Field(min_length=1)
    jenjang: Jenjang


class StudentIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    nama: str = Field(min_length=1, max_length=100)
    jenjang: Jenjang


class NoteIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    jenis: Literal["perkembangan", "ditingkatkan", "dipertahankan"]
    isi: str = Field(min_length=1, max_length=1000)


# ---------------- Halaman web ----------------
@app.get("/", include_in_schema=False)
def home():
    return FileResponse(STATIC_DIR / "index.html")


# ---------------- Health check ----------------
@app.get("/health")
def health():
    return {"status": "ok"}  # 200 OK


# ---------------- Cek Materi ----------------
@app.post("/lessons/analyze", status_code=201)
def analyze_lesson(body: AnalyzeIn):
    """Analisis naskah materi, lalu simpan ringkasannya ke database (POST = tulis data -> 201)."""
    result = analyze(body.isi, body.jenjang)
    saved = db.save_lesson(
        body.judul, body.isi, body.jenjang,
        result["total_kalimat"], result["kalimat_bermasalah"],
    )
    return {
        "id": saved["id"],
        "created_at": saved["created_at"],
        "judul": body.judul,
        "jenjang": body.jenjang,
        **result,
    }


@app.get("/lessons")
def get_lessons():
    """Riwayat analisis materi (GET = baca data -> 200)."""
    return db.list_lessons()


# ---------------- Catatan Murid ----------------
@app.post("/students", status_code=201)
def add_student(body: StudentIn):
    return db.create_student(body.nama, body.jenjang)


@app.get("/students")
def get_students():
    return db.list_students()


@app.post("/students/{student_id}/notes", status_code=201)
def add_student_note(student_id: int, body: NoteIn):
    if db.get_student(student_id) is None:
        raise HTTPException(status_code=404, detail="Murid tidak ditemukan")
    return db.add_note(student_id, body.jenis, body.isi)


@app.get("/students/{student_id}/notes")
def get_student_notes(student_id: int):
    if db.get_student(student_id) is None:
        raise HTTPException(status_code=404, detail="Murid tidak ditemukan")
    return db.list_notes(student_id)
