"""
PyLedger Utils - PII masking (Phase 4)
Prevents leaking emails/phones/IBANs in logs, PDFs and exports.
"""

import re


def mask_email(email: str) -> str:
    if not email or "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        return f"{local[0]}***@{domain}"
    return f"{local[0]}***{local[-1]}@{domain}"


def mask_phone(phone: str) -> str:
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) < 4:
        return "***"
    return f"***-***-{digits[-4:]}"


def mask_iban(iban: str) -> str:
    s = re.sub(r"\s", "", iban or "")
    if len(s) < 8:
        return "***"
    return f"{s[:4]} **** **** {s[-4:]}"


def mask_dict(data: dict, keys=("email", "phone", "iban", "password")) -> dict:
    out = dict(data)
    for k in keys:
        if k in out and out[k]:
            if k == "email":
                out[k] = mask_email(str(out[k]))
            elif k == "phone":
                out[k] = mask_phone(str(out[k]))
            elif k == "iban":
                out[k] = mask_iban(str(out[k]))
            else:
                out[k] = "***"
    return out
