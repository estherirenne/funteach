"""
Logika "Cek Materi" FunTeach.
"""
import json
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

# Batas jumlah kata per kalimat untuk tiap jenjang.
# Ini patokan kasar, silakan ubah sesuai pengalaman mengajar kamu.
MAX_WORDS = {"sd_pemula": 10, "sd_lanjut": 15, "smp_sma": 20}

# Kata penghubung yang sering membuat kalimat jadi berlapis-lapis
CONNECTORS = {
    "yang", "sehingga", "karena", "dimana", "agar",
    "supaya", "sedangkan", "namun", "tetapi", "serta",
}

# Kamus istilah coding -> padanan sederhana (diisi di app/data/glossary.json)
with open(DATA_DIR / "glossary.json", encoding="utf-8") as f:
    GLOSSARY = json.load(f)


def split_sentences(text):
    """Pisahkan teks menjadi kalimat: di tanda baca akhir kalimat atau baris baru."""
    parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
    return [p.strip() for p in parts if p.strip()]


def analyze(text, jenjang):
    """Periksa tiap kalimat dan kembalikan hasil analisis berupa dictionary."""
    limit = MAX_WORDS[jenjang]
    sentences = []

    for raw in split_sentences(text):
        # Kalimat yang diawali tanda * dianggap PENTING oleh instruktur
        important = raw.startswith("*")
        sentence = raw.lstrip("*").strip()

        # Hitung kata. Pola ini membuat kata ulang seperti "berkali-kali" dihitung satu kata.
        words = re.findall(r"\w+(?:-\w+)*", sentence.lower())
        issues = []

        # Aturan 1: kalimat kepanjangan
        if len(words) > limit:
            issues.append(
                f"Terlalu panjang: {len(words)} kata (batas {limit}). Coba dipecah."
            )

        # Aturan 2: terlalu banyak kata penghubung
        connectors = [w for w in words if w in CONNECTORS]
        if len(connectors) >= 2:
            issues.append("Banyak kata penghubung. Coba jadikan dua kalimat.")

        # Aturan 3: kata sulit yang ada di glossary
        hard_terms = [
            {"kata": term, "padanan": meaning}
            for term, meaning in GLOSSARY.items()
            if re.search(rf"\b{re.escape(term)}\b", sentence.lower())
        ]

        sentences.append({
            "kalimat": sentence,
            "jumlah_kata": len(words),
            "penting": important,
            "masalah": issues,
            "kata_sulit": hard_terms,
        })

    return {
        "total_kalimat": len(sentences),
        "kalimat_bermasalah": sum(1 for s in sentences if s["masalah"]),
        "poin_penting": [s["kalimat"] for s in sentences if s["penting"]],
        "kalimat": sentences,
    }
