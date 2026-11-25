import csv
import io
import re
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "opendatabcn_NP-NASIA_Consolats-csv.csv"


def _clean(value):
    return (value or "").lstrip("\ufeff").strip()


def _country_from_title(title):
    title = re.sub(r"\s+", " ", title).strip()
    if not title or title in {"Oficina Consular", "Secretaria General dels Cos Consolar a Barcelona"}:
        return "No especificado"
    for country in ("Costa d'Ivori", "Estats Units d'Amèrica", "Regne Unit"):
        if country.casefold() in title.casefold():
            return country

    title = re.sub(r"^(?:Consolat(?: General)?(?: Honorari)?|Representació Diplomàtica)\s*", "", title, flags=re.IGNORECASE)
    connectors = re.compile(
        r"de la República(?: de)?\s+|de la Federació de\s+|del Gran Ducat de\s+|del Regne(?: de)?\s+|de les\s+|dels\s+|del\s+|de\s+|d['’]",
        re.IGNORECASE,
    )
    matches = list(connectors.finditer(title))
    if matches:
        country = title[matches[-1].end():].strip()
        if country:
            return country
    return title.strip()


def load_consulates():
    """Read the Barcelona consulates dataset and expose fields used by the UI."""
    records = []
    raw = DATA_FILE.read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        encoding = "utf-16"
    else:
        encoding = "utf-8-sig"
    csv_text = io.StringIO(raw.decode(encoding), newline="")
    reader = csv.reader(csv_text)
    try:
        headers = [_clean(value) for value in next(reader, [])]
        for values in reader:
            # The source has an extra modification timestamp at column 7.
            # Remove it so addresses, contact details, and coordinates line up with the headers.
            if (len(values) == len(headers) + 1 and len(values) > 6
                    and re.match(r"^\d{4}-\d\d-\d\dT", values[6])):
                values.pop(6)
            row = {
                _clean(key): _clean(value)
                for key, value in zip(headers, values)
            }
            title = row.get("institution_id") or row.get("institution_name") or row.get("name") or "Consulado sin nombre"
            street = " ".join(part for part in (row.get("addresses_road_name", ""), row.get("addresses_start_street_number", "")) if part)
            records.append({
                "id": row.get("register_id", ""),
                "country": _country_from_title(title),
                "address": street or "Dirección no disponible",
                "district": row.get("addresses_district_name", "") or "Sin distrito",
                "postal_code": row.get("addresses_zip_code", ""),
                "phone": row.get("values_value", ""),
            })
    finally:
        csv_text.close()
    return records


def get_districts(records):
    return sorted({record["district"] for record in records if record["district"] != "Sin distrito"})


def get_countries(records):
    return sorted({record["country"] for record in records})
