# FunTeach

Aplikasi web untuk calon instruktur coding anak: memeriksa kerumitan kalimat materi sesuai jenjang murid,
menyorot poin penting, dan menyimpan catatan perkembangan tiap murid.

> Projek UTS COMP6991031 - Cloud Services. Berjalan penuh di localhost dengan Docker Compose.

**Tautan:** Artikel: _(isi setelah publish)_ | Video YouTube: _(isi setelah upload)_

## Mengapa projek ini? (TODO: tulis ulang dengan kata-katamu sendiri)

_Contoh kerangka:_ Saya akan menjadi coding instructor untuk anak SD-SMA. Saya sering kesulitan memilih kata dan
cenderung memakai kalimat yang terlalu kompleks saat menjelaskan. FunTeach membantu saya menyiapkan materi
sebelum mengajar dan mencatat perkembangan tiap murid supaya tidak tertukar.

## Fitur

- **Cek Materi:** menandai kalimat yang terlalu panjang untuk jenjang murid, kalimat dengan banyak kata penghubung,
  dan istilah sulit beserta padanan sederhananya (dari `app/data/glossary.json`).
- **Poin penting:** kalimat yang diawali tanda `*` disorot dan dikumpulkan sebagai daftar poin yang wajib diulang.
- **Catatan Murid:** catatan perkembangan, hal yang perlu ditingkatkan, dan hal yang perlu dipertahankan.
- **Riwayat:** daftar pemeriksaan materi yang pernah dilakukan.

Catatan: aplikasi ini berbasis aturan sederhana (hitung kata dan cocokkan kata kunci), **bukan AI**.

## Arsitektur

```
Browser --> http://localhost:8000
              |
              v
        [ app  (FastAPI, port 8000) ] --- network: funteach-net --- [ db (PostgreSQL 16) ] -- volume: pgdata
                                                                      [ adminer (8080) ]  (profile "tools")
```

| Service | Image | Port ke laptop | Keterangan |
|---|---|---|---|
| app | build dari `Dockerfile` (multi-stage) | 8000 | FastAPI + halaman web |
| db | postgres:16.4-alpine | tidak dibuka | data di named volume `pgdata`, ada healthcheck |
| adminer | adminer:4.8.1 | 8080 | hanya jalan dengan profile `tools` |

## Cara menjalankan

Prasyarat: Docker Desktop.

```bash
git clone https://github.com/estherirenne/funteach.git
cd funteach
cp .env.example .env        # lalu ganti POSTGRES_PASSWORD di file .env
docker compose up -d --build
```

Buka http://localhost:8000

Untuk menyalakan Adminer (opsional): `docker compose --profile tools up -d`, buka http://localhost:8080
(sistem: PostgreSQL, server: `db`, user/password/database sesuai `.env`).

## Endpoint

| Method | Path | Status |
|---|---|---|
| GET | `/health` | 200 |
| POST | `/lessons/analyze` | 201 (422 jika input tidak valid) |
| GET | `/lessons` | 200 |
| POST | `/students` | 201 |
| GET | `/students` | 200 |
| POST | `/students/{id}/notes` | 201 (404 jika murid tidak ada) |
| GET | `/students/{id}/notes` | 200 |

Dokumentasi interaktif: http://localhost:8000/docs. Skrip uji: `bash scripts/demo.sh`.

## Uji persistensi

```bash
docker compose down        # hapus container, volume TETAP ada
docker compose up -d       # data murid dan riwayat masih ada
docker compose down -v     # hapus container DAN volume: data hilang
```

## Screenshot

_(tambahkan: halaman aplikasi, `docker compose ps`, hasil curl 200/201/422, uji persistensi)_

## Catatan data pribadi

Aplikasi menyimpan nama murid dan catatan. Untuk demo ini hanya dipakai **data dummy**. Untuk pemakaian nyata,
perlu memperhatikan UU No. 27 Tahun 2022 tentang Pelindungan Data Pribadi (khususnya data anak) dan kebijakan
tempat mengajar. Tidak ada secret yang di-commit: `.env` di-ignore Git, yang tersedia hanya `.env.example`.

## Sumber dan atribusi

Memakai library dan image open-source: FastAPI, Uvicorn, Pydantic, psycopg, PostgreSQL, Adminer.
Dataset/glossary dibuat sendiri.

## AI Usage Declaration

_(TODO: sesuaikan dengan yang benar-benar kamu lakukan)_

- **Alat yang dipakai:** Claude (Anthropic).
- **Bagian yang dibantu:** brainstorming ide projek, kerangka awal kode (FastAPI, analyzer, lapisan database,
  halaman web), kerangka Dockerfile dan docker-compose.yml, serta debugging.
- **Bagian yang saya kerjakan/ubah sendiri:** _(tulis: isi glossary, aturan batas kata, pengujian, screenshot, video, artikel, dll.)_
- **Contoh prompt utama:** _(tempel 2-3 prompt aslimu, misalnya "bantu brainstorming ide projek untuk tugas ini", "buatkan kerangka Dockerfile multi-stage")_
- Saya telah membaca dan mampu menjelaskan setiap baris Dockerfile dan docker-compose.yml.
