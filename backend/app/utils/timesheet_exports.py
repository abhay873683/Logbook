import csv
import io
import time
from collections import defaultdict, deque

_CACHE = {}
_CACHE_TTL = 60

_EXPORT_REQUESTS = defaultdict(deque)
_EXPORT_LIMIT = 5
_EXPORT_WINDOW = 60


def cache_get(key):
    item = _CACHE.get(key)

    if not item:
        return None

    expires_at, value = item

    if time.time() >= expires_at:
        _CACHE.pop(key, None)
        return None

    return value


def cache_set(key, value, ttl=_CACHE_TTL):
    _CACHE[key] = (time.time() + ttl, value)


def cache_clear():
    _CACHE.clear()


def check_export_rate_limit(user_id):
    now = time.time()
    requests = _EXPORT_REQUESTS[user_id]

    while requests and now - requests[0] >= _EXPORT_WINDOW:
        requests.popleft()

    if len(requests) >= _EXPORT_LIMIT:
        return False

    requests.append(now)
    return True


def build_timesheet_csv(items):
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "id",
        "user_id",
        "date",
        "status",
        "total_seconds",
        "total_hours",
        "notes",
    ])

    for item in items:
        seconds = item.total_seconds or 0

        writer.writerow([
            item.id,
            item.user_id,
            item.date,
            item.status,
            seconds,
            round(seconds / 3600, 2),
            item.notes or "",
        ])

    return output.getvalue().encode("utf-8")


def build_timesheet_pdf(items):
    lines = ["TreeFlow AI - Timesheet Report", ""]

    total_seconds = 0

    for item in items:
        seconds = item.total_seconds or 0
        total_seconds += seconds

        lines.append(
            f"ID {item.id} | User {item.user_id} | "
            f"{item.date} | {item.status} | "
            f"{round(seconds / 3600, 2)} hours"
        )

    lines.append("")
    lines.append(
        f"Total Hours: {round(total_seconds / 3600, 2)}"
    )

    lines = lines[:45]

    stream_lines = [
        "BT",
        "/F1 11 Tf",
        "50 790 Td",
    ]

    for index, line in enumerate(lines):
        if index:
            stream_lines.append("0 -17 Td")

        safe = (
            str(line)
            .replace("\\", "\\\\")
            .replace("(", "\\(")
            .replace(")", "\\)")
        )

        stream_lines.append(f"({safe}) Tj")

    stream_lines.append("ET")

    stream = "\n".join(stream_lines).encode(
        "latin-1",
        "replace",
    )

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        (
            b"<< /Type /Page /Parent 2 0 R "
            b"/MediaBox [0 0 612 842] "
            b"/Resources << /Font << /F1 5 0 R >> >> "
            b"/Contents 4 0 R >>"
        ),
        (
            b"<< /Length "
            + str(len(stream)).encode()
            + b" >>\nstream\n"
            + stream
            + b"\nendstream"
        ),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]

    for number, obj in enumerate(objects, 1):
        offsets.append(len(pdf))
        pdf.extend(f"{number} 0 obj\n".encode())
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")

    xref = len(pdf)

    pdf.extend(
        f"xref\n0 {len(objects) + 1}\n".encode()
    )
    pdf.extend(b"0000000000 65535 f \n")

    for offset in offsets[1:]:
        pdf.extend(
            f"{offset:010d} 00000 n \n".encode()
        )

    pdf.extend(
        (
            "trailer\n"
            f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            "startxref\n"
            f"{xref}\n"
            "%%EOF\n"
        ).encode()
    )

    return bytes(pdf)
