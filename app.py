import streamlit as st
st.set_page_config(page_title="Vyhodnocení laboratorního deníku")
st.write("Streamlit import OK")
import pandas as pd
st.write("Pandas import OK")
import pdfplumber
st.write("pdfplumber import OK")
import io
st.write("io import OK")
from openpyxl import load_workbook
st.write("openpyxl import OK")
from difflib import SequenceMatcher

st.title("Vyhodnocení laboratorního deníku")

pdf_file = st.file_uploader("Nahraj laboratorní deník (PDF)", type="pdf")
xlsx_file = st.file_uploader("Nahraj soubor Klíč.xlsx", type="xlsx")

def extract_text_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        return "\n".join(page.extract_text() or "" for page in pdf.pages)

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def contains_similar(text, keyword, threshold=0.4):
    text = text.lower()
    keyword = keyword.lower()
    if keyword in text:
        return True
    return similar(text, keyword) >= threshold

def count_matches_advanced(text, konstrukce, zkouska_raw, stanice_raw):
    st.markdown(f"---\n🔍 **Konstrukce:** `{konstrukce}`")
    st.markdown(f"🔍 **Zkoušky:** `{zkouska_raw}`")
    st.markdown(f"🔍 **Staničení:** `{stanice_raw}`")
    druhy_zk = [z.strip().lower() for z in str(zkouska_raw).split(",") if z.strip()]
    staniceni = [s.strip().lower() for s in str(stanice_raw).split(",") if s.strip()]
    match_count = 0
    for line in text.splitlines():
        columns = line.split()
        col_8 = columns[7] if len(columns) >= 8 else ""
        col_11 = columns[10] if len(columns) >= 11 else ""
        col_14 = columns[13] if len(columns) >= 14 else ""

        text_stanice = col_8.lower()
        text_konstrukce = col_11.lower()
        text_zkouska = col_14.lower()

        konstrukce_ok = contains_similar(text_konstrukce, konstrukce)
        stanice_ok = any(s in text_stanice for s in staniceni)
        zkouska_ok = any(z in text_zkouska for z in druhy_zk)

        debug_status = f"⛔ | konstrukce_ok={konstrukce_ok}, zkouska_ok={zkouska_ok}, stanice_ok={stanice_ok}"

        if konstrukce_ok and zkouska_ok and stanice_ok:
            match_count += 1
            st.markdown(f"✅ **Shoda nalezena:** `Staničení: {text_stanice}` | `Konstrukce: {text_konstrukce}` | `Zkouška: {text_zkouska}`")
        else:
            st.markdown(f"{debug_status} → `Staničení: {text_stanice}` | `Konstrukce: {text_konstrukce}` | `Zkouška: {text_zkouska}`")
    st.markdown(f"**Celkem nalezeno:** `{match_count}` záznamů")
    return match_count
