"""
lms/utils/email_utils.py
Send a purchase-confirmation email with the PDF invoice attached.
"""

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .invoice_generator import generate_invoice_pdf
import os, base64


# ── HTML email template ───────────────────────────────────────────────────────
_EMAIL_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Purchase Confirmation</title>
</head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:'Segoe UI',Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f8;padding:32px 0;">
  <tr>
    <td align="center">
      <table width="600" cellpadding="0" cellspacing="0"
             style="background:#ffffff;border-radius:12px;overflow:hidden;
                    box-shadow:0 4px 20px rgba(0,0,0,0.08);max-width:600px;width:100%;">

        <!-- ── Green header ── -->
        <tr>
          <td style="background:linear-gradient(135deg,#4CAF50,#66BB6A);
                     padding:40px 40px 32px;text-align:center;">
            <!-- Checkmark circle -->
            <div style="display:inline-block;width:64px;height:64px;border-radius:50%;
                        background:rgba(255,255,255,0.25);line-height:64px;
                        text-align:center;margin-bottom:16px;">
              <span style="font-size:32px;color:#fff;">✓</span>
            </div>
            <h1 style="margin:0 0 8px;color:#fff;font-size:22px;font-weight:700;">
              Purchase Successful!
            </h1>
            <p style="margin:0;color:rgba(255,255,255,0.9);font-size:14px;">
              Your enrollment is confirmed. Happy learning!
            </p>
          </td>
        </tr>

        <!-- ── Greeting ── -->
        <tr>
          <td style="padding:32px 40px 0;">
            <p style="margin:0;font-size:15px;color:#212121;">
              Hi <strong>{student_name}</strong>,
            </p>
            <p style="margin:12px 0 0;font-size:14px;color:#616161;line-height:1.6;">
              Thank you for your purchase on <strong>{platform_name}</strong>.
              You now have full access to the course below.
              Your invoice is attached to this email as a PDF.
            </p>
          </td>
        </tr>

        <!-- ── Course card ── -->
        <tr>
          <td style="padding:24px 40px;">
            <table width="100%" cellpadding="0" cellspacing="0"
                   style="background:#F1FDF1;border-radius:10px;border:1px solid #C8E6C9;">
              <tr>
                <td style="padding:20px 24px;">
                  <p style="margin:0 0 4px;font-size:11px;text-transform:uppercase;
                             letter-spacing:0.08em;color:#9E9E9E;">Enrolled Course</p>
                  <p style="margin:0;font-size:16px;font-weight:700;color:#212121;">
                    {course_title}
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- ── Order details ── -->
        <tr>
          <td style="padding:0 40px 24px;">
            <table width="100%" cellpadding="0" cellspacing="0">
              <tr>
                <td colspan="2"
                    style="font-size:11px;text-transform:uppercase;letter-spacing:0.08em;
                           color:#9E9E9E;padding-bottom:12px;border-bottom:1px solid #F0F0F0;">
                  Order Details
                </td>
              </tr>
              {detail_rows}
              <!-- Total row -->
              <tr style="background:#E8F5E9;">
                <td style="padding:12px 0;font-size:14px;font-weight:700;color:#212121;">
                  Total Paid
                </td>
                <td style="padding:12px 0;font-size:14px;font-weight:700;
                           color:#2E7D32;text-align:right;">
                  &#8377;{total_amount}
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- ── CTA button ── -->
        <tr>
          <td style="padding:0 40px 32px;text-align:center;">
            <a href="{my_courses_url}"
               style="display:inline-block;background:#4CAF50;color:#fff;
                      text-decoration:none;padding:14px 36px;border-radius:8px;
                      font-size:15px;font-weight:700;">
              Go to My Courses →
            </a>
          </td>
        </tr>

        <!-- ── Footer ── -->
        <tr>
          <td style="background:#F9FBF9;border-top:1px solid #E8F5E9;
                     padding:20px 40px;text-align:center;">
            <p style="margin:0;font-size:12px;color:#9E9E9E;">
              If you have any questions, simply reply to this email.<br>
              © {year} {platform_name}. All rights reserved.
            </p>
          </td>
        </tr>

      </table>
    </td>
  </tr>
</table>
</body>
</html>
"""

_DETAIL_ROW = """
<tr>
  <td style="padding:10px 0;font-size:13px;color:#757575;
             border-bottom:1px solid #F5F5F5;">{label}</td>
  <td style="padding:10px 0;font-size:13px;font-weight:600;
             color:#212121;text-align:right;
             border-bottom:1px solid #F5F5F5;">{value}</td>
</tr>
"""


def send_purchase_confirmation_email(order_data: dict) -> None:
    """
    Send a styled HTML confirmation email with a PDF invoice attached.

    `order_data` must contain all keys required by `generate_invoice_pdf`
    plus:
        my_courses_url  – absolute URL to the "My Courses" page
        year            – current year (for footer copyright)
    """
    import datetime
    platform      = order_data.get("platform_name", "EduLearn LMS")
    student_email = order_data["student_email"]
    student_name  = order_data["student_name"]
    year          = order_data.get("year", datetime.date.today().year)

    # ── Build detail rows ──────────────────────────────────────────────────────
    rows_html = ""
    rows = [
        ("Order Number",    f"#{order_data['order_id']}"),
        ("Order Date",      order_data["order_date"]),
        ("Payment Method",  order_data["payment_method"]),
        ("Status",          "Confirmed ✓"),
    ]
    if order_data.get("is_discounted"):
        rows += [
            ("Original Price",   f"\u20b9{float(order_data['course_price']):,.2f}"),
            ("Discount",         f"-\u20b9{float(order_data['discount_amount']):,.2f}"),
        ]
    rows += [
        ("Subtotal",  f"\u20b9{float(order_data['base_price']):,.2f}"),
        ("GST (18%)", f"\u20b9{float(order_data['tax_amount']):,.2f}"),
    ]
    for label, value in rows:
        rows_html += _DETAIL_ROW.format(label=label, value=value)

    html_body = _EMAIL_HTML.format(
        student_name  = student_name,
        platform_name = platform,
        course_title  = order_data["course_title"],
        detail_rows   = rows_html,
        total_amount  = f"{float(order_data['total_amount']):,.2f}",
        my_courses_url= order_data.get("my_courses_url", "#"),
        year          = year,
    )

    # ── Plain-text fallback ────────────────────────────────────────────────────
    text_body = (
        f"Hi {student_name},\n\n"
        f"Thank you for purchasing '{order_data['course_title']}' on {platform}.\n\n"
        f"Order No. : #{order_data['order_id']}\n"
        f"Date       : {order_data['order_date']}\n"
        f"Total Paid : \u20b9{float(order_data['total_amount']):,.2f}\n\n"
        "Your invoice is attached as a PDF.\n\n"
        f"Go to My Courses: {order_data.get('my_courses_url', '')}\n\n"
        f"— {platform} Team"
    )

 # ── Generate PDF ───────────────────────────────────────────────────────────
    pdf_bytes = generate_invoice_pdf(order_data)

    subject    = f"[{platform}] Purchase Confirmed – #{order_data['order_id']}"
    from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@example.com")

    # ── Use SendGrid on Render, Django SMTP locally ────────────────────────────
    api_key = os.environ.get("SENDGRID_API_KEY")

    if api_key:
        # ── RENDER: SendGrid Web API ──────────────────────────────────────────
        import sendgrid
        from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

        sg_mail = Mail(
            from_email         = from_email,
            to_emails          = student_email,
            subject            = subject,
            html_content       = html_body,
            plain_text_content = text_body,
        )
        encoded_pdf = base64.b64encode(pdf_bytes).decode()
        sg_mail.add_attachment(Attachment(
            file_content = FileContent(encoded_pdf),
            file_name    = FileName(f"Invoice_{order_data['order_id']}.pdf"),
            file_type    = FileType("application/pdf"),
            disposition  = Disposition("attachment"),
        ))
        try:
            sg = sendgrid.SendGridAPIClient(api_key=api_key)
            response = sg.send(sg_mail)
            print(f"Email sent via SendGrid! Status: {response.status_code}")
        except Exception as e:
            print(f"SendGrid failed: {e}")

    else:
        # ── LOCAL: Django SMTP (Gmail) ────────────────────────────────────────
        msg = EmailMultiAlternatives(
            subject    = subject,
            body       = text_body,
            from_email = from_email,
            to         = [student_email],
        )
        msg.attach_alternative(html_body, "text/html")
        msg.attach(
            filename = f"Invoice_{order_data['order_id']}.pdf",
            content  = pdf_bytes,
            mimetype = "application/pdf",
        )
        msg.send(fail_silently=False)
        print("Email sent via Django SMTP!")

#     # ── Generate PDF ───────────────────────────────────────────────────────────
#     pdf_bytes = generate_invoice_pdf(order_data)

#     # ── Compose & send email via SendGrid HTTP API ─────────────────────────────
 
# # ── Compose & send email ───────────────────────────────────────────────────────
#     subject = f"[{platform}] Purchase Confirmed – #{order_data['order_id']}"
#     from_email = getattr(settings, "DEFAULT_FROM_EMAIL", f"noreply@{platform.lower().replace(' ', '')}.com")

#     msg = EmailMultiAlternatives(
#         subject    = subject,
#         body       = text_body,
#         from_email = from_email,
#         to         = [student_email],
#     )
#     msg.attach_alternative(html_body, "text/html")
#     msg.attach(
#         filename     = f"Invoice_{order_data['order_id']}.pdf",
#         content      = pdf_bytes,
#         mimetype     = "application/pdf",
#     )
#     msg.send(fail_silently=False)