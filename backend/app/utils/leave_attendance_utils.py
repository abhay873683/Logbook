import csv
import io
import time


_CACHE = {}
_RATE_LIMIT = {}


def cache_get(key, ttl=60):
    item = _CACHE.get(key)

    if not item:
        return None

    created_at, value = item

    if time.time() - created_at > ttl:
        _CACHE.pop(key, None)
        return None

    return value


def cache_set(key, value):
    _CACHE[key] = (
        time.time(),
        value,
    )


def cache_clear():
    _CACHE.clear()


def check_export_rate_limit(
    user_id,
    limit=10,
    window=60,
):
    now = time.time()

    history = _RATE_LIMIT.get(
        user_id,
        []
    )

    history = [
        timestamp
        for timestamp in history
        if now - timestamp < window
    ]

    if len(history) >= limit:
        _RATE_LIMIT[user_id] = history
        return False

    history.append(now)
    _RATE_LIMIT[user_id] = history

    return True


def build_csv(
    headers,
    rows,
):
    output = io.StringIO()

    writer = csv.writer(output)
    writer.writerow(headers)

    for row in rows:
        writer.writerow(row)

    return output.getvalue()


def escape_pdf_text(value):
    return str(value).replace(
        "\\",
        "\\\\",
    ).replace(
        "(",
        "\\(",
    ).replace(
        ")",
        "\\)",
    )


def build_simple_pdf(
    title,
    lines,
):
    text_commands = [
        "BT",
        "/F1 16 Tf",
        "50 790 Td",
        f"({escape_pdf_text(title)}) Tj",
        "/F1 9 Tf",
    ]

    for line in lines[:55]:
        text_commands.extend([
            "0 -14 Td",
            f"({escape_pdf_text(line)[:110]}) Tj",
        ])

    text_commands.append("ET")

    stream = "\n".join(
        text_commands
    ).encode("latin-1", errors="replace")

    objects = []

    objects.append(
        b"<< /Type /Catalog /Pages 2 0 R >>"
    )

    objects.append(
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>"
    )

    objects.append(
        b"<< /Type /Page /Parent 2 0 R "
        b"/MediaBox [0 0 612 842] "
        b"/Resources << /Font << /F1 5 0 R >> >> "
        b"/Contents 4 0 R >>"
    )

    objects.append(
        b"<< /Length "
        + str(len(stream)).encode()
        + b" >>\nstream\n"
        + stream
        + b"\nendstream"
    )

    objects.append(
        b"<< /Type /Font /Subtype /Type1 "
        b"/BaseFont /Helvetica >>"
    )

    pdf = bytearray(
        b"%PDF-1.4\n"
    )

    offsets = [0]

    for index, obj in enumerate(
        objects,
        start=1,
    ):
        offsets.append(
            len(pdf)
        )

        pdf.extend(
            f"{index} 0 obj\n".encode()
        )
        pdf.extend(obj)
        pdf.extend(
            b"\nendobj\n"
        )

    xref = len(pdf)

    pdf.extend(
        f"xref\n0 {len(objects) + 1}\n".encode()
    )

    pdf.extend(
        b"0000000000 65535 f \n"
    )

    for offset in offsets[1:]:
        pdf.extend(
            f"{offset:010d} 00000 n \n".encode()
        )

    pdf.extend(
        (
            "trailer\n"
            f"<< /Size {len(objects)+1} /Root 1 0 R >>\n"
            "startxref\n"
            f"{xref}\n"
            "%%EOF"
        ).encode()
    )

    return bytes(pdf)
