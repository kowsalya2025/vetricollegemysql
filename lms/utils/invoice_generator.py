"""
lms/utils/invoice_generator.py
Generate a professional PDF invoice for course purchases.
"""
import io
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics

try:
    pdfmetrics.registerFont(
        TTFont("Unicode", "C:/Windows/Fonts/arial.ttf")
    )
    pdfmetrics.registerFont(
        TTFont("Unicode-Bold", "C:/Windows/Fonts/arialbd.ttf")
    )
    print("Arial fonts registered successfully")
except Exception as e:
    print("Font registration failed:", e)  # Fall back gracefully if path differs on the deployment server

# Use these aliases throughout — swap back to Helvetica if registration failed
def _font(bold=False):
    name = "Unicode-Bold" if bold else "Unicode"
    return name if name in pdfmetrics.getRegisteredFontNames() else (
        "Helvetica-Bold" if bold else "Helvetica"
    )

# ── Brand colours ────────────────────────────────────────────────────────────
GREEN       = colors.HexColor("#4CAF50")
DARK_GREEN  = colors.HexColor("#2E7D32")
LIGHT_GREEN = colors.HexColor("#E8F5E9")
GREY_TEXT   = colors.HexColor("#757575")
DARK_TEXT   = colors.HexColor("#212121")
WHITE       = colors.white


def _s(name, base_styles, **kw):
    """Shortcut to create a named ParagraphStyle."""
    return ParagraphStyle(name, parent=base_styles["Normal"], **kw)


def generate_invoice_pdf(order_data: dict) -> bytes:
    """
    Build a PDF invoice and return the raw bytes.

    Required keys in `order_data`:
        order_id, order_date, payment_method,
        student_name, student_email,
        course_title, course_price (float),
        is_discounted (bool), discount_amount (float),
        base_price (float), tax_amount (float), total_amount (float),
        platform_name (optional, default "Vetri Digital College")
    """
    buffer = io.BytesIO()
    platform = order_data.get("platform_name", "Vetri Digital College")

    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=15 * mm,
        bottomMargin=20 * mm,
    )
    W = doc.width

    FONT      = _font(bold=False)
    FONT_BOLD = _font(bold=True)

    # ── Paragraph style factory ──────────────────────────────────────────────
    S = {
        "brand":  _s("brand",  styles, fontSize=22, textColor=GREEN,      fontName=FONT_BOLD),
        "tagline":_s("tagline",styles, fontSize=8,  textColor=GREY_TEXT,  fontName=FONT),
        "invoice":_s("invoice",styles, fontSize=18, textColor=DARK_TEXT,  fontName=FONT_BOLD, alignment=TA_RIGHT),
        "label":  _s("label",  styles, fontSize=8,  textColor=GREY_TEXT,  fontName=FONT),
        "value":  _s("value",  styles, fontSize=9,  textColor=DARK_TEXT,  fontName=FONT_BOLD),
        "normal": _s("normal", styles, fontSize=9,  textColor=DARK_TEXT,  fontName=FONT),
        "th":     _s("th",     styles, fontSize=8,  textColor=WHITE,      fontName=FONT_BOLD),
        "th_r":   _s("th_r",   styles, fontSize=8,  textColor=WHITE,      fontName=FONT_BOLD, alignment=TA_RIGHT),
        "th_c":   _s("th_c",   styles, fontSize=8,  textColor=WHITE,      fontName=FONT_BOLD, alignment=TA_CENTER),
        "cell_c": _s("cell_c", styles, fontSize=9,  textColor=DARK_TEXT,  fontName=FONT,      alignment=TA_CENTER),
        "cell_r": _s("cell_r", styles, fontSize=9,  textColor=DARK_TEXT,  fontName=FONT,      alignment=TA_RIGHT),
        "footer": _s("footer", styles, fontSize=7,  textColor=GREY_TEXT,  fontName=FONT,      alignment=TA_CENTER),
        "thanks": _s("thanks", styles, fontSize=9,  textColor=GREY_TEXT,  fontName=FONT,      alignment=TA_CENTER),
    }

    story = []

    # ─────────────────────────────────────────────────────────────────────────
    # 1. HEADER (brand left | INVOICE right)
    # ─────────────────────────────────────────────────────────────────────────
    hdr = Table(
        [[Paragraph(platform, S["brand"]), Paragraph("INVOICE", S["invoice"])]],
        colWidths=[W * 0.5, W * 0.5],
    )
    hdr.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(hdr)
    story.append(Paragraph("Online Learning Platform", S["tagline"]))
    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width="100%", thickness=2, color=GREEN, spaceAfter=6 * mm))

    # ─────────────────────────────────────────────────────────────────────────
    # 2. ORDER META (left: order info | right: bill-to)
    # ─────────────────────────────────────────────────────────────────────────
    def meta_block(rows):
        data = [
            [Paragraph(lbl, S["label"]), Paragraph(str(val), S["value"])]
            for lbl, val in rows
        ]
        t = Table(data, colWidths=[32 * mm, 55 * mm])
        t.setStyle(TableStyle([
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING",    (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        return t

    left_meta = meta_block([
        ("Invoice No.",    f"#{order_data['order_id']}"),
        ("Date",           order_data["order_date"]),
        ("Payment Method", order_data["payment_method"]),
        ("Status",         "Paid \u2713"),
    ])
    right_meta = meta_block([
        ("Bill To", order_data["student_name"]),
        ("Email",   order_data["student_email"]),
    ])

    meta_tbl = Table([[left_meta, right_meta]], colWidths=[W * 0.5, W * 0.5])
    meta_tbl.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP")]))
    story.append(meta_tbl)
    story.append(Spacer(1, 6 * mm))

    # ─────────────────────────────────────────────────────────────────────────
    # 3. LINE-ITEMS TABLE
    # ─────────────────────────────────────────────────────────────────────────
    col_w = [W * 0.55, W * 0.15, W * 0.15, W * 0.15]

    # ₹ — U+20B9 Indian Rupee Sign (rendered correctly with DejaVu font)
    def rupee(amount: float) -> str:
        return f"\u20b9{amount:,.2f}"

    items_data = [
        # Header row
        [
            Paragraph("DESCRIPTION", S["th"]),
            Paragraph("QTY",         S["th_c"]),
            Paragraph("UNIT PRICE",  S["th_r"]),
            Paragraph("AMOUNT",      S["th_r"]),
        ],
        # Single item row
        [
            Paragraph(order_data["course_title"],                    S["normal"]),
            Paragraph("1",                                           S["cell_c"]),
            Paragraph(rupee(order_data["course_price"]),             S["cell_r"]),
            Paragraph(rupee(order_data["course_price"]),             S["cell_r"]),
        ],
    ]

    items_tbl = Table(items_data, colWidths=col_w, repeatRows=1)
    items_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0),  GREEN),
        ("ROWBACKGROUND", (0, 1), (-1, 1),  LIGHT_GREEN),
        ("GRID",          (0, 0), (-1, -1), 0.5, colors.HexColor("#E0E0E0")),
        ("TOPPADDING",    (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(items_tbl)
    story.append(Spacer(1, 4 * mm))

    # ─────────────────────────────────────────────────────────────────────────
    # 4. TOTALS BLOCK (right-aligned)
    # ─────────────────────────────────────────────────────────────────────────
    tw        = W * 0.45
    col_left  = tw * 0.55
    col_right = tw * 0.45

    def price_row(label, amount, red=False, highlight=False):
        txt_color = WHITE if highlight else (colors.HexColor("#E53935") if red else DARK_TEXT)
        fn = FONT_BOLD if highlight else FONT
        fs = 10 if highlight else 9
        lp = _s(f"lbl_{label}", styles, fontSize=fs, textColor=txt_color, fontName=fn)
        rp = _s(f"amt_{label}", styles, fontSize=fs, textColor=txt_color, fontName=fn, alignment=TA_RIGHT)
        return [Paragraph(label, lp), Paragraph(amount, rp)]

    totals_rows = []
    if order_data.get("is_discounted"):
        totals_rows.append(price_row(
            "Original Price", rupee(float(order_data["course_price"]))
        ))
        totals_rows.append(price_row(
            "Discount", f"-{rupee(float(order_data['discount_amount']))}", red=True
        ))
    totals_rows.append(price_row("Subtotal",   rupee(float(order_data["base_price"]))))
    totals_rows.append(price_row("GST (18%)",  rupee(float(order_data["tax_amount"]))))
    totals_rows.append(price_row(
        "TOTAL PAID", rupee(float(order_data["total_amount"])), highlight=True
    ))

    last_idx   = len(totals_rows) - 1
    totals_tbl = Table(totals_rows, colWidths=[col_left, col_right])
    totals_tbl.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0),          (-1, -1),       4),
        ("BOTTOMPADDING", (0, 0),          (-1, -1),       4),
        ("LEFTPADDING",   (0, 0),          (-1, -1),       10),
        ("RIGHTPADDING",  (0, 0),          (-1, -1),       10),
        ("LINEABOVE",     (0, last_idx),   (-1, last_idx), 1.5, GREEN),
        ("BACKGROUND",    (0, last_idx),   (-1, last_idx), GREEN),
    ]))

    # Push totals block to the right side
    wrapper = Table([[None, totals_tbl]], colWidths=[W - tw, tw])
    wrapper.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(wrapper)
    story.append(Spacer(1, 10 * mm))

    # ─────────────────────────────────────────────────────────────────────────
    # 5. FOOTER
    # ─────────────────────────────────────────────────────────────────────────
    story.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GREEN, spaceAfter=4 * mm))
    story.append(Paragraph(
        f"Thank you for your purchase, {order_data['student_name']}! "
        "We wish you a great learning experience.",
        S["thanks"]
    ))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        f"Questions? Reply to this email or visit our Help Center. \u2014 {platform}",
        S["footer"]
    ))

    doc.build(story)
    return buffer.getvalue()