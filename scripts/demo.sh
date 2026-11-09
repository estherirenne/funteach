#!/usr/bin/env bash
# Skrip bukti untuk Soal 2d: uji endpoint dan status code.
# Jalankan setelah aplikasi hidup:  bash scripts/demo.sh
# Ambil screenshot terminalnya untuk laporan PDF.

BASE="${BASE:-http://localhost:8000}"

echo "== 1. GET /health (harapan: 200) =="
curl -i "$BASE/health"
echo; echo

echo "== 2. POST /lessons/analyze (harapan: 201) =="
curl -i -X POST "$BASE/lessons/analyze" \
  -H "Content-Type: application/json" \
  -d '{"judul":"Perulangan","isi":"Perulangan adalah cara menyuruh komputer mengulang perintah yang sama sehingga kita tidak perlu menulisnya berkali-kali. *Ingat, perulangan bikin kode lebih singkat.","jenjang":"sd_pemula"}'
echo; echo

echo "== 3. POST /lessons/analyze dengan isi kosong (harapan: 422) =="
curl -i -X POST "$BASE/lessons/analyze" \
  -H "Content-Type: application/json" \
  -d '{"judul":"Kosong","isi":"","jenjang":"sd_pemula"}'
echo; echo

echo "== 4. POST /students (harapan: 201) =="
RESP=$(curl -s -X POST "$BASE/students" \
  -H "Content-Type: application/json" \
  -d '{"nama":"Murid Dummy","jenjang":"sd_pemula"}')
echo "$RESP"
# Ambil id murid dari respons JSON
ID=$(echo "$RESP" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2)
echo; echo

echo "== 5. POST /students/$ID/notes (harapan: 201) =="
curl -i -X POST "$BASE/students/$ID/notes" \
  -H "Content-Type: application/json" \
  -d '{"jenis":"perkembangan","isi":"Sudah paham urutan perintah dasar."}'
echo; echo

echo "== 6. GET /students (harapan: 200) =="
curl -i "$BASE/students"
echo
