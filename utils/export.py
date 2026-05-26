"""Export helpers."""

from __future__ import annotations

import io
import json

import pandas as pd


def export_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")


def export_excel(df: pd.DataFrame, meta: dict | None = None) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Données")
        if meta:
            pd.DataFrame([meta]).to_excel(writer, index=False, sheet_name="Meta")
    output.seek(0)
    return output.getvalue()


def export_json(df: pd.DataFrame, meta: dict | None = None) -> bytes:
    payload = {
        "meta": meta or {},
        "data": df.where(pd.notna(df), None).to_dict(orient="records"),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
