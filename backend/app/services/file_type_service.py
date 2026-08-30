import os

from sqlalchemy.orm import Session

from app.models.file_type import FileType


CATEGORY_RULES = {
    "document": {
        ".pdf",
        ".doc",
        ".docx",
        ".txt",
        ".rtf",
        ".odt",
    },
    "spreadsheet": {
        ".xls",
        ".xlsx",
        ".csv",
        ".ods",
    },
    "presentation": {
        ".ppt",
        ".pptx",
        ".odp",
    },
    "image": {
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".webp",
        ".bmp",
        ".svg",
    },
    "archive": {
        ".zip",
        ".rar",
        ".7z",
        ".tar",
        ".gz",
    },
    "code": {
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".java",
        ".c",
        ".cpp",
        ".cs",
        ".html",
        ".css",
        ".json",
        ".xml",
        ".sql",
    },
}


NAME_HINTS = {
    "invoice": "finance",
    "receipt": "finance",
    "payment": "finance",
    "expense": "finance",
    "budget": "finance",
    "salary": "finance",
    "contract": "legal",
    "agreement": "legal",
    "policy": "legal",
    "nda": "legal",
    "resume": "hr",
    "cv": "hr",
    "candidate": "hr",
    "employee": "hr",
    "attendance": "hr",
    "meeting": "meeting",
    "minutes": "meeting",
    "agenda": "meeting",
    "report": "report",
    "summary": "report",
    "analysis": "report",
    "design": "design",
    "mockup": "design",
    "wireframe": "design",
}


def get_all_file_types(db: Session):
    return (
        db.query(FileType)
        .filter(FileType.is_active == True)
        .order_by(FileType.name.asc())
        .all()
    )


def classify_file(
    file_name: str,
    mime_type: str | None = None,
):
    clean_name = os.path.basename(
        file_name or ""
    ).strip()

    if not clean_name:
        raise ValueError("Invalid file name")

    lower_name = clean_name.lower()
    extension = os.path.splitext(
        lower_name
    )[1]

    normalized_mime = (
        mime_type or ""
    ).strip().lower()

    # --------------------------------------------------------
    # Strongest signal: semantic keywords in file name
    # --------------------------------------------------------
    for keyword, category in NAME_HINTS.items():
        if keyword in lower_name:
            return {
                "file_name": clean_name,
                "extension": extension,
                "mime_type": mime_type,
                "category": category,
                "confidence": 0.95,
                "reason": (
                    f"File name contains the "
                    f"keyword '{keyword}'"
                ),
            }

    # --------------------------------------------------------
    # MIME type classification
    # --------------------------------------------------------
    if normalized_mime.startswith("image/"):
        return {
            "file_name": clean_name,
            "extension": extension,
            "mime_type": mime_type,
            "category": "image",
            "confidence": 0.92,
            "reason": "Detected from image MIME type",
        }

    if normalized_mime.startswith("video/"):
        return {
            "file_name": clean_name,
            "extension": extension,
            "mime_type": mime_type,
            "category": "video",
            "confidence": 0.92,
            "reason": "Detected from video MIME type",
        }

    if normalized_mime.startswith("audio/"):
        return {
            "file_name": clean_name,
            "extension": extension,
            "mime_type": mime_type,
            "category": "audio",
            "confidence": 0.92,
            "reason": "Detected from audio MIME type",
        }

    if normalized_mime == "application/pdf":
        return {
            "file_name": clean_name,
            "extension": extension,
            "mime_type": mime_type,
            "category": "document",
            "confidence": 0.90,
            "reason": "Detected from PDF MIME type",
        }

    # --------------------------------------------------------
    # Extension classification
    # --------------------------------------------------------
    for category, extensions in CATEGORY_RULES.items():
        if extension in extensions:
            return {
                "file_name": clean_name,
                "extension": extension,
                "mime_type": mime_type,
                "category": category,
                "confidence": 0.85,
                "reason": (
                    f"Detected from file extension "
                    f"'{extension}'"
                ),
            }

    return {
        "file_name": clean_name,
        "extension": extension,
        "mime_type": mime_type,
        "category": "other",
        "confidence": 0.50,
        "reason": (
            "No strong filename, MIME, or "
            "extension rule matched"
        ),
    }


FOLDER_NAMES = {
    "finance": "Finance",
    "legal": "Legal",
    "hr": "HR",
    "meeting": "Meetings",
    "report": "Reports",
    "design": "Design",
    "document": "Documents",
    "spreadsheet": "Spreadsheets",
    "presentation": "Presentations",
    "image": "Images",
    "video": "Videos",
    "audio": "Audio",
    "archive": "Archives",
    "code": "Code",
    "other": "Other",
}


def suggest_file_organization(
    db: Session,
    file_record,
    user_id: int,
):
    from app.models.folder import Folder

    classification = classify_file(
        file_name=file_record.file_name,
        mime_type=file_record.file_type,
    )

    category = classification["category"]

    folder_name = FOLDER_NAMES.get(
        category,
        category.replace("_", " ").title(),
    )

    existing_folder = (
        db.query(Folder)
        .filter(
            Folder.owner_id == user_id,
            Folder.parent_id.is_(None),
            Folder.name.ilike(folder_name),
        )
        .first()
    )

    if existing_folder:
        reason = (
            f"{classification['reason']}. "
            f"Matching folder '{existing_folder.name}' "
            "already exists."
        )
    else:
        reason = (
            f"{classification['reason']}. "
            f"Suggested folder '{folder_name}' "
            "does not exist yet."
        )

    return {
        "file_id": file_record.id,
        "file_name": file_record.file_name,
        "category": category,
        "confidence": classification["confidence"],
        "recommended_folder_id": (
            existing_folder.id
            if existing_folder
            else None
        ),
        "recommended_folder_name": (
            existing_folder.name
            if existing_folder
            else folder_name
        ),
        "folder_exists": existing_folder is not None,
        "reason": reason,
    }
