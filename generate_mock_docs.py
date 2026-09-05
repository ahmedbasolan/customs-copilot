from fpdf import FPDF
import os

OUTPUT_DIR = "mock_docs"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class DocPDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def create_bill_of_lading():
    pdf = DocPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "BILL OF LADING", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "B/L Number: SH-2026-00487", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Date: 28 Aug 2026", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Shipper
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "SHIPPER", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "Guangzhou Bright Electronics Co., Ltd.", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Unit 1205, Tower B, Tianhe Tech Park", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Guangzhou, Guangdong, China 510620", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Consignee
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "CONSIGNEE", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "Al Noor Trading FZE", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Office 304, Building 6, Jebel Ali Free Zone", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Dubai, UAE", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "TRN: 100234567800003", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Container details
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "CONTAINER DETAILS", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "Container No: MSCU4567892", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Seal No: CN-883421", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Size/Type: 40 HC", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Ports
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "PORT INFORMATION", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "Port of Loading: Shanghai, China (CNSHA)", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Port of Discharge: Jebel Ali, Dubai, UAE (AEJEA)", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Vessel: MV PACIFIC STAR V.2609E", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Voyage No: 2609E", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Weight
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "WEIGHT & MEASUREMENT", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "Gross Weight: 18,500.00 KGS", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Net Weight: 16,200.00 KGS", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Volume: 58.40 CBM", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Packages
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "PACKAGES", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "120 PALLETS", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Marks & Numbers
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "MARKS & NUMBERS", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "ANT/DXB/2609-001", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "MADE IN CHINA", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "C/NO. 1-120", new_x="LMARGIN", new_y="NEXT")

    pdf.output(os.path.join(OUTPUT_DIR, "bill_of_lading.pdf"))


def create_commercial_invoice():
    pdf = DocPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "COMMERCIAL INVOICE", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "Invoice No: INV-2026-GB-00892", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Date: 27 Aug 2026", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Payment Terms: T/T 30 days after B/L date", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Seller
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "SELLER", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "Guangzhou Bright Electronics Co., Ltd.", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Unit 1205, Tower B, Tianhe Tech Park", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Guangzhou, Guangdong, China 510620", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Buyer
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "BUYER", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "Al Noor Trading FZE", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Office 304, Building 6, Jebel Ali Free Zone", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Dubai, UAE", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "TRN: 100234567800003", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Line items
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "DESCRIPTION OF GOODS", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(8, 7, "Item", border=1)
    pdf.cell(60, 7, "Description", border=1)
    pdf.cell(20, 7, "HS Code", border=1)
    pdf.cell(15, 7, "Qty", border=1)
    pdf.cell(25, 7, "Unit Price", border=1)
    pdf.cell(30, 7, "Amount (USD)", border=1)
    pdf.cell(22, 7, "Origin", border=1)
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    items = [
        ("1", "LED Panel Light 600x600mm 48W", "9405.42", "500", "USD 28.50", "USD 14,250.00", "China"),
        ("2", "LED Downlight 12W Round", "9405.42", "2000", "USD 6.80", "USD 13,600.00", "China"),
        ("3", "LED Street Light 150W IP65", "9405.42", "200", "USD 45.00", "USD 9,000.00", "China"),
    ]
    for item in items:
        pdf.cell(8, 7, item[0], border=1)
        pdf.cell(60, 7, item[1], border=1)
        pdf.cell(20, 7, item[2], border=1)
        pdf.cell(15, 7, item[3], border=1)
        pdf.cell(25, 7, item[4], border=1)
        pdf.cell(30, 7, item[5], border=1)
        pdf.cell(22, 7, item[6], border=1)
        pdf.ln()

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "TOTAL INVOICE VALUE: USD 36,850.00", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "Currency: United States Dollar (USD)", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "COUNTRY OF ORIGIN: China", new_x="LMARGIN", new_y="NEXT")

    pdf.output(os.path.join(OUTPUT_DIR, "commercial_invoice.pdf"))


def create_packing_list():
    pdf = DocPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "PACKING LIST", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 8, "PL No: PL-2026-GB-00892", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Date: 27 Aug 2026", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "Reference: INV-2026-GB-00892 / B/L SH-2026-00487", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Shipper/Consignee
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "SHIPPER", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "Guangzhou Bright Electronics Co., Ltd., China", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "CONSIGNEE", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "Al Noor Trading FZE, Dubai, UAE", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Items
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "PACKING DETAILS", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(8, 7, "Item", border=1)
    pdf.cell(55, 7, "Description", border=1)
    pdf.cell(15, 7, "Qty", border=1)
    pdf.cell(20, 7, "Packages", border=1)
    pdf.cell(25, 7, "Gross Wt (KGS)", border=1)
    pdf.cell(25, 7, "Net Wt (KGS)", border=1)
    pdf.cell(22, 7, "CBM", border=1)
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    items = [
        ("1", "LED Panel Light 600x600mm 48W", "500", "50 pallets", "6,800.00", "5,920.00", "22.50"),
        ("2", "LED Downlight 12W Round", "2000", "40 pallets", "4,200.00", "3,680.00", "16.80"),
        ("3", "LED Street Light 150W IP65", "200", "30 pallets", "7,500.00", "6,600.00", "19.10"),
    ]
    for item in items:
        pdf.cell(8, 7, item[0], border=1)
        pdf.cell(55, 7, item[1], border=1)
        pdf.cell(15, 7, item[2], border=1)
        pdf.cell(20, 7, item[3], border=1)
        pdf.cell(25, 7, item[4], border=1)
        pdf.cell(25, 7, item[5], border=1)
        pdf.cell(22, 7, item[6], border=1)
        pdf.ln()

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "TOTALS", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "Total Packages: 120 PALLETS", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Total Gross Weight: 18,500.00 KGS", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Total Net Weight: 16,200.00 KGS", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "Total Volume: 58.40 CBM", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # Marks & Numbers
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, "MARKS & NUMBERS", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 7, "ANT/DXB/2609-001", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "MADE IN CHINA", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 7, "C/NO. 1-120", new_x="LMARGIN", new_y="NEXT")

    pdf.output(os.path.join(OUTPUT_DIR, "packing_list.pdf"))


if __name__ == "__main__":
    create_bill_of_lading()
    create_commercial_invoice()
    create_packing_list()
    print(f"Created 3 mock documents in {OUTPUT_DIR}/")
