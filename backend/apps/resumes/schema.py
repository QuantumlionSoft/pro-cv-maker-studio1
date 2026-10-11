"""Versioned CV content schema.

The server is the only place that decides what is stored. Unknown keys are dropped,
text is length-limited and stripped of control characters, URLs are limited to
http/https, colours must be hex, and image references must belong to the owner.
"""
import re
import secrets
from urllib.parse import urlparse

from rest_framework.exceptions import ValidationError

SCHEMA_VERSION = 1
MAX_ITEMS = 40
MAX_LONG_TEXT = 4000
MAX_TEXT = 1000
CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
ITEM_ID_RE = re.compile(r"[^A-Za-z0-9_-]")
FONTS = ["Inter", "Roboto", "Poppins", "Open Sans", "Lato", "Montserrat", "Merriweather"]
HEADER_ALIGN = {"left", "center", "right"}


def default_design():
    return {
        "font": "Inter",
        "colorAccent": "#3b82f6",
        "colorHeaderBg": "#1e293b",
        "colorHeaderText": "#ffffff",
        "colorSidebarBg": "#f1f5f9",
        "colorSidebarText": "#334155",
        "educationInSidebar": False,
        "headerAlign": "left",
        "nameSize": 32,
        "headingSize": 16,
        "textSize": 13,
        "photoSize": 140,
        "qrSize": 80,
        "newPageForExtras": True,
    }


def empty_content():
    return {
        "schemaVersion": SCHEMA_VERSION,
        "personal": {
            "firstName": "",
            "middleName": "",
            "lastName": "",
            "title": "",
            "email": "",
            "phone": "",
            "location": "",
            "website": "",
            "linkedin": "",
            "github": "",
            "photoId": None,
            "showQr": False,
            "qrLink": "",
        },
        "summary": "",
        "experience": [],
        "education": [],
        "skills": [],
        "languages": [],
        "technologies": [],
        "projects": [],
        "certifications": [],
        "references": [],
    }


def _err(path, message):
    return ValidationError({"content": [f"{path}: {message}"]})


def _text(value, path, max_len=200):
    if value is None:
        return ""
    if not isinstance(value, str):
        raise _err(path, "must be text.")
    value = CONTROL_RE.sub("", value).strip()
    if len(value) > max_len:
        raise _err(path, f"must be at most {max_len} characters.")
    return value


def _email(value, path):
    value = _text(value, path, 254)
    if value and not EMAIL_RE.match(value):
        raise _err(path, "is not a valid email address.")
    return value


def _url(value, path):
    value = _text(value, path, 500)
    if not value:
        return ""
    if "://" not in value:
        if ":" in value.split("/", 1)[0]:
            # e.g. "javascript:alert(1)" or "mailto:x": refuse rather than prefixing https://
            raise _err(path, "must be an http or https link.")
        value = "https://" + value
    parsed = urlparse(value)
    if parsed.scheme not in ("http", "https") or not parsed.netloc or any(c.isspace() for c in value):
        raise _err(path, "must be an http or https link.")
    return value


def _color(value, path, default):
    if value in (None, ""):
        return default
    if not isinstance(value, str) or not COLOR_RE.match(value):
        raise _err(path, "must be a #RRGGBB colour.")
    return value.lower()


def _int(value, path, low, high, default):
    if value is None:
        return default
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise _err(path, "must be a whole number.")
    if not low <= number <= high:
        raise _err(path, f"must be between {low} and {high}.")
    return number


def _media(value, owned):
    """Image references are kept only if they point at an asset the owner actually has."""
    if value in (None, ""):
        return None
    try:
        media_id = int(value)
    except (TypeError, ValueError):
        return None
    return media_id if owned(media_id) else None


def _item_id(raw, seen):
    value = ITEM_ID_RE.sub("", str(raw or ""))[:40] or secrets.token_hex(6)
    while value in seen:
        value = secrets.token_hex(6)
    seen.add(value)
    return value


def _items(value, path, builder, owned):
    if value is None:
        return []
    if not isinstance(value, list):
        raise _err(path, "must be a list.")
    if len(value) > MAX_ITEMS:
        raise _err(path, f"can contain at most {MAX_ITEMS} entries.")
    seen = set()
    result = []
    for index, raw in enumerate(value):
        if not isinstance(raw, dict):
            raise _err(f"{path}[{index}]", "must be an object.")
        item = builder(raw, f"{path}[{index}]", owned)
        item["id"] = _item_id(raw.get("id"), seen)
        result.append(item)
    return result


def _personal(raw, owned):
    p = "personal"
    return {
        "firstName": _text(raw.get("firstName"), f"{p}.firstName", 100),
        "middleName": _text(raw.get("middleName"), f"{p}.middleName", 100),
        "lastName": _text(raw.get("lastName"), f"{p}.lastName", 100),
        "title": _text(raw.get("title"), f"{p}.title", 120),
        "email": _email(raw.get("email"), f"{p}.email"),
        "phone": _text(raw.get("phone"), f"{p}.phone", 40),
        "location": _text(raw.get("location"), f"{p}.location", 120),
        "website": _url(raw.get("website"), f"{p}.website"),
        "linkedin": _text(raw.get("linkedin"), f"{p}.linkedin", 100),
        "github": _text(raw.get("github"), f"{p}.github", 100),
        "photoId": _media(raw.get("photoId"), owned),
        "showQr": bool(raw.get("showQr")),
        "qrLink": _url(raw.get("qrLink"), f"{p}.qrLink"),
    }


def _experience(raw, path, owned):
    return {
        "company": _text(raw.get("company"), f"{path}.company", 160),
        "position": _text(raw.get("position"), f"{path}.position", 160),
        "location": _text(raw.get("location"), f"{path}.location", 120),
        "start": _text(raw.get("start"), f"{path}.start", 40),
        "end": _text(raw.get("end"), f"{path}.end", 40),
        "current": bool(raw.get("current")),
        "description": _text(raw.get("description"), f"{path}.description", MAX_LONG_TEXT),
        "logoId": _media(raw.get("logoId"), owned),
    }


def _education(raw, path, owned):
    return {
        "school": _text(raw.get("school"), f"{path}.school", 160),
        "degree": _text(raw.get("degree"), f"{path}.degree", 200),
        "gpa": _text(raw.get("gpa"), f"{path}.gpa", 40),
        "start": _text(raw.get("start"), f"{path}.start", 40),
        "end": _text(raw.get("end"), f"{path}.end", 40),
        "logoId": _media(raw.get("logoId"), owned),
    }


def _level_item(raw, path, owned):
    return {
        "name": _text(raw.get("name"), f"{path}.name", 100),
        "level": _int(raw.get("level"), f"{path}.level", 10, 100, 50),
    }


def _name_item(raw, path, owned):
    return {"name": _text(raw.get("name"), f"{path}.name", 100)}


def _project(raw, path, owned):
    return {
        "name": _text(raw.get("name"), f"{path}.name", 160),
        "description": _text(raw.get("description"), f"{path}.description", MAX_TEXT),
        "link": _url(raw.get("link"), f"{path}.link"),
        "showQr": bool(raw.get("showQr")),
    }


def _certification(raw, path, owned):
    return {
        "name": _text(raw.get("name"), f"{path}.name", 160),
        "issuer": _text(raw.get("issuer"), f"{path}.issuer", 160),
        "link": _url(raw.get("link"), f"{path}.link"),
        "showQr": bool(raw.get("showQr")),
    }


def _reference(raw, path, owned):
    return {
        "name": _text(raw.get("name"), f"{path}.name", 120),
        "position": _text(raw.get("position"), f"{path}.position", 120),
        "company": _text(raw.get("company"), f"{path}.company", 120),
        "email": _email(raw.get("email"), f"{path}.email"),
        "phone": _text(raw.get("phone"), f"{path}.phone", 40),
    }


def normalize_content(raw, owned):
    """Return a clean copy of CV content. `owned(media_id) -> bool` checks ownership."""
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValidationError({"content": ["Content must be an object."]})
    personal_raw = raw.get("personal") or {}
    if not isinstance(personal_raw, dict):
        raise _err("personal", "must be an object.")
    return {
        "schemaVersion": SCHEMA_VERSION,
        "personal": _personal(personal_raw, owned),
        "summary": _text(raw.get("summary"), "summary", MAX_LONG_TEXT),
        "experience": _items(raw.get("experience"), "experience", _experience, owned),
        "education": _items(raw.get("education"), "education", _education, owned),
        "skills": _items(raw.get("skills"), "skills", _level_item, owned),
        "languages": _items(raw.get("languages"), "languages", _level_item, owned),
        "technologies": _items(raw.get("technologies"), "technologies", _name_item, owned),
        "projects": _items(raw.get("projects"), "projects", _project, owned),
        "certifications": _items(raw.get("certifications"), "certifications", _certification, owned),
        "references": _items(raw.get("references"), "references", _reference, owned),
    }


def normalize_design(raw):
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValidationError({"design": ["Design must be an object."]})
    d = default_design()
    font = raw.get("font", d["font"])
    if font not in FONTS:
        raise ValidationError({"design": [f"Unknown font: {font}"]})
    align = raw.get("headerAlign", d["headerAlign"])
    if align not in HEADER_ALIGN:
        raise ValidationError({"design": ["headerAlign must be left, center or right."]})
    return {
        "font": font,
        "colorAccent": _color(raw.get("colorAccent"), "design.colorAccent", d["colorAccent"]),
        "colorHeaderBg": _color(raw.get("colorHeaderBg"), "design.colorHeaderBg", d["colorHeaderBg"]),
        "colorHeaderText": _color(raw.get("colorHeaderText"), "design.colorHeaderText", d["colorHeaderText"]),
        "colorSidebarBg": _color(raw.get("colorSidebarBg"), "design.colorSidebarBg", d["colorSidebarBg"]),
        "colorSidebarText": _color(raw.get("colorSidebarText"), "design.colorSidebarText", d["colorSidebarText"]),
        "educationInSidebar": bool(raw.get("educationInSidebar", d["educationInSidebar"])),
        "headerAlign": align,
        "nameSize": _int(raw.get("nameSize"), "design.nameSize", 24, 48, d["nameSize"]),
        "headingSize": _int(raw.get("headingSize"), "design.headingSize", 12, 24, d["headingSize"]),
        "textSize": _int(raw.get("textSize"), "design.textSize", 10, 18, d["textSize"]),
        "photoSize": _int(raw.get("photoSize"), "design.photoSize", 80, 200, d["photoSize"]),
        "qrSize": _int(raw.get("qrSize"), "design.qrSize", 50, 120, d["qrSize"]),
        "newPageForExtras": bool(raw.get("newPageForExtras", d["newPageForExtras"])),
    }
