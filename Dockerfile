# =====================================================================
# Dockerfile FunTeach - multi-stage build (builder -> runtime)
# =====================================================================

# ---------- Stage 1: builder ----------
# Tugasnya hanya memasang dependency Python. Stage ini dibuang setelah build,
# jadi alat-alat bantu pemasangan tidak ikut masuk ke image akhir.
# Tag versi spesifik (3.12.7-slim), BUKAN "latest", supaya build selalu konsisten.
FROM python:3.12.7-slim AS builder

# Folder kerja di dalam container
WORKDIR /build

# Salin file dependency DULU, sebelum source code.
# Alasannya layer cache: selama requirements.txt tidak berubah,
# langkah "pip install" di bawah tidak diulang walau kode aplikasi berubah.
# (COPY dipakai, bukan ADD: ADD bisa mengunduh URL dan mengekstrak arsip otomatis,
# jadi COPY lebih jelas dan aman kalau kita cuma menyalin file.)
COPY requirements.txt .

# Pasang dependency ke folder /install (bukan ke sistem) supaya mudah disalin ke stage berikutnya.
# --no-cache-dir: jangan simpan cache pip, supaya ukuran layer kecil.
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ---------- Stage 2: runtime ----------
# Image akhir hanya berisi Python + hasil install + kode aplikasi.
FROM python:3.12.7-slim AS runtime

# ENV: konfigurasi proses Python
#  - PYTHONDONTWRITEBYTECODE=1 : jangan buat file .pyc
#  - PYTHONUNBUFFERED=1        : log langsung tampil di "docker compose logs"
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Ambil hasil install dari stage builder (inilah inti multi-stage)
COPY --from=builder /install /usr/local

# Salin source code aplikasi SETELAH dependency (berubah lebih sering)
COPY app ./app

# Jalankan sebagai user biasa, bukan root (praktik keamanan dasar)
RUN useradd --create-home appuser
USER appuser

# EXPOSE hanya dokumentasi: aplikasi mendengarkan di port 8000 di dalam container.
# Port yang dibuka ke laptop diatur di docker-compose.yml.
EXPOSE 8000

# Exec form (array JSON): uvicorn jadi proses utama dan menerima sinyal stop dengan benar.
# --host 0.0.0.0 supaya bisa diakses dari luar container.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
