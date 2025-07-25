from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .utils import process_invoice
from pathlib import Path
from .models import UploadFile, RejectedFile, Invoice, Log
from django.utils import timezone
from datetime import datetime
import re
import os
import logging

@login_required
def home(request):
    return render(request, "home.html", {})

@login_required
def upload_view(request):
    return render(request, "upload.html", {})

INVOICE_NUMBER_KEYS = [
    "invoice number", "invoice no", "inv no", "invoice #", "invoice id",
    "no.", "number", "bill no", "bill number", "ref no", "reference number",
    "document number", "doc no", "#", "invoice"
]

COMPANY_NAME_KEYS = [
    "company", "company name", "supplier", "supplier name", "vendor", "vendor name",
    "seller", "seller name", "billed by", "issued by", "from", "payee", "provider"
]

TOTAL_AMOUNT_KEYS = [
    "total", "total amount", "total due", "amount due", "invoice total",
    "amount payable", "total payable", "total invoice amount", "grand total",
    "balance due", "amount", "total to pay", "sum", "total amount due", "final amount",
    "total charges", "net amount", "amount paid", "total balance", "balance"
]

DATE_KEYS = [
    "date", "invoice date", "billing date", "issue date", "date of invoice",
    "invoice issued", "bill date", "date issued", "date of issue", "due date",
    "service date", "posting date", "document date"
]

def extract_invoice_data(ocr_text):
    lines = [line.strip() for line in ocr_text.splitlines() if line.strip()]
    lower_lines = [line.lower() for line in lines]
    
    company_name = ""
    invoice_number = ""
    total_amount = None
    invoice_date = None

    def extract_value_with_context(idx, keys, lookahead=True, lookbehind=False):
        current_line = lower_lines[idx]
        next_line = lines[idx + 1] if idx + 1 < len(lines) else None
        prev_line = lines[idx - 1] if idx > 0 else None
        
        for key in keys:
            pattern = r'\b' + re.escape(key) + r'\b'
            if re.search(pattern, current_line):
                match = re.search(rf'{re.escape(key)}[:\s-]*(\S.*)', lines[idx], re.IGNORECASE)
                if match:
                    return match.group(1).strip()
                
                if lookahead and next_line and re.search(rf'{re.escape(key)}\s*$', lines[idx], re.IGNORECASE):
                    return next_line.strip()
                
                if lookbehind and prev_line and re.search(rf'^{re.escape(key)}\s*', lines[idx], re.IGNORECASE):
                    return prev_line.strip()
        return None

    for i in range(min(5, len(lines))):
        company_name = extract_value_with_context(i, COMPANY_NAME_KEYS)
        if company_name:
            break
    if not company_name:
        company_name = lines[0] if lines else ""

    for i in range(len(lines)):
        invoice_number = extract_value_with_context(i, INVOICE_NUMBER_KEYS)
        if invoice_number:
            if not re.search(r'[\w-]{3,}', invoice_number):
                invoice_number = ""
            else:
                break

    total_candidates = []
    for i in range(len(lower_lines)-1, -1, -1):
        line = lower_lines[i]
        if any(re.search(r'\b' + re.escape(key) + r'\b', line) for key in TOTAL_AMOUNT_KEYS):
            value = extract_value_with_context(i, TOTAL_AMOUNT_KEYS, lookbehind=True)
            if value:
                num_match = re.search(r'[\$€£]?\s*([\d,]+(?:\.\d{1,2})?)', value.replace(",", ""))
                if num_match:
                    try:
                        amount = float(num_match.group(1))
                        total_candidates.append((abs(amount), amount))
                    except ValueError:
                        continue
    
    if total_candidates:
        total_candidates.sort(key=lambda x: x[0], reverse=True)
        total_amount = total_candidates[0][1]
    
    if total_amount is None:
        max_amount = 0
        for line in lines:
            matches = re.findall(r'[\$€£]?\s*([\d,]+(?:\.\d{1,2})?)', line)
            for match in matches:
                try:
                    amount = float(match.replace(",", ""))
                    if amount > max_amount:
                        max_amount = amount
                except ValueError:
                    continue
        total_amount = max_amount if max_amount > 0 else None

    date_formats = [
        (r'\b(\d{4})[-/](\d{1,2})[-/](\d{1,2})\b', '%Y-%m-%d'),  # YYYY-MM-DD
        (r'\b(\d{1,2})[-/](\d{1,2})[-/](\d{4})\b', '%d-%m-%Y'),  # DD-MM-YYYY
        (r'\b(\d{1,2})[-/](\d{1,2})[-/](\d{2})\b', '%d-%m-%y'),   # DD-MM-YY
        (r'\b(\d{1,2})\s+([a-z]{3,9})\s+(\d{4})\b', '%d %B %Y'),  # 25 July 2024
        (r'\b([a-z]{3,9})\s+(\d{1,2}),?\s+(\d{4})\b', '%B %d %Y'),# July 25 2024
        (r'\b(\d{1,2})[-/](\d{1,2})\b', '%d-%m')                   # DD-MM (assume current year)
    ]
    
    for i in range(len(lower_lines)):
        if any(key in lower_lines[i] for key in DATE_KEYS):
            value = extract_value_with_context(i, DATE_KEYS)
            if value:
                for pattern, fmt in date_formats:
                    match = re.search(pattern, value, re.IGNORECASE)
                    if match:
                        date_str = match.group(0)
                        try:
                            if fmt == '%d-%m':
                                invoice_date = datetime.strptime(date_str, fmt).date()
                                invoice_date = invoice_date.replace(year=timezone.now().year)
                            else:
                                invoice_date = datetime.strptime(date_str, fmt).date()
                            break
                        except:
                            continue
                if invoice_date:
                    break
    
    if not invoice_date:
        for line in lines:
            for pattern, fmt in date_formats:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    date_str = match.group(0)
                    try:
                        if fmt == '%d-%m':
                            invoice_date = datetime.strptime(date_str, fmt).date()
                            invoice_date = invoice_date.replace(year=timezone.now().year)
                        else:
                            invoice_date = datetime.strptime(date_str, fmt).date()
                        break
                    except:
                        continue
            if invoice_date:
                break
    
    if not invoice_date:
        invoice_date = timezone.now().date()

    return {
        "company_name": company_name,
        "invoice_number": invoice_number,
        "total_amount": total_amount,
        "date": invoice_date
    }

TEMP_DIR = Path("temp")
TEMP_DIR.mkdir(exist_ok=True)

@login_required
def send_files(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("pdf_file")
        if not uploaded_file:
            return HttpResponse("No file uploaded.", status=400)

        temp_path = TEMP_DIR / uploaded_file.name
        try:
            with open(temp_path, "wb+") as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            ocr_text, error = process_invoice(temp_path)

            if error:
                Log.objects.create(
                    user=request.user,
                    action="SCAN_FAILED",
                    description=f"OCR error: {error}"
                )
                return HttpResponse(f"OCR failed: {error}", status=500)

            invoice_data = extract_invoice_data(ocr_text)

            invoice = Invoice.objects.create(
                user=request.user,
                company_name=invoice_data.get("company_name", ""),
                invoice_number=invoice_data.get("invoice_number", ""),
                total_amount=invoice_data.get("total_amount"),
                date=invoice_data.get("date"),
                upload_time=timezone.now(),
                original_file_name=uploaded_file.name,
            )

            Log.objects.create(
                user=request.user,
                action="SCAN_SUCCESS",
                description=f"Invoice {invoice.invoice_number or uploaded_file.name} uploaded successfully."
            )

            try:
                os.remove(temp_path)
            except Exception as e:
                logging.warning(f"Failed to delete temp file {temp_path}: {e}")

            return HttpResponse(f"Invoice uploaded successfully: {invoice.invoice_number}")

        except Exception as e:
            Log.objects.create(
                user=request.user,
                action="SCAN_FAILED",
                description=f"Unexpected error during file upload: {str(e)}"
            )
            return HttpResponse(f"Unexpected error: {str(e)}", status=500)

    return redirect("invoices:upload")
