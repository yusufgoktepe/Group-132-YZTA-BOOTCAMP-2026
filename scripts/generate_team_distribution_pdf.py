from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


OUTPUT_DIR = Path("artifacts")
PDF_PATH = OUTPUT_DIR / "ekip-gorev-dagilimi.pdf"
FONT_REGULAR = "ArialUnicodeCM"
FONT_BOLD = "ArialUnicodeCMBold"


NAVY = colors.HexColor("#102B49")
BLUE = colors.HexColor("#2E74B5")
SLATE = colors.HexColor("#52606D")
LIGHT = colors.HexColor("#F0F4F8")
LIGHTER = colors.HexColor("#F8FAFC")
MID = colors.HexColor("#D9E1E8")
TEXT = colors.HexColor("#2D2D2D")


def build_styles():
    pdfmetrics.registerFont(TTFont(FONT_REGULAR, r"C:\Windows\Fonts\arial.ttf"))
    pdfmetrics.registerFont(TTFont(FONT_BOLD, r"C:\Windows\Fonts\arialbd.ttf"))
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="TitleCM",
            parent=styles["Title"],
            fontName=FONT_BOLD,
            fontSize=23,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=6,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubtitleCM",
            parent=styles["Normal"],
            fontName=FONT_REGULAR,
            fontSize=12,
            textColor=SLATE,
            alignment=TA_CENTER,
            spaceAfter=14,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionCM",
            parent=styles["Heading1"],
            fontName=FONT_BOLD,
            fontSize=15,
            textColor=BLUE,
            spaceBefore=10,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SubSectionCM",
            parent=styles["Heading2"],
            fontName=FONT_BOLD,
            fontSize=12,
            textColor=NAVY,
            spaceBefore=8,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="BodyCM",
            parent=styles["Normal"],
            fontName=FONT_REGULAR,
            fontSize=10.5,
            leading=14,
            textColor=TEXT,
            spaceAfter=5,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallCM",
            parent=styles["Normal"],
            fontName=FONT_REGULAR,
            fontSize=9,
            textColor=SLATE,
            leading=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CalloutCM",
            parent=styles["Normal"],
            fontName=FONT_REGULAR,
            fontSize=10.5,
            leading=14,
            textColor=NAVY,
            alignment=TA_CENTER,
        )
    )
    return styles


def bullet_list(items, style):
    return ListFlowable(
        [ListItem(Paragraph(item, style), leftIndent=8) for item in items],
        bulletType="bullet",
        start="circle",
        bulletFontName=FONT_REGULAR,
        bulletFontSize=8,
        leftIndent=18,
        bulletOffsetY=1,
        spaceAfter=4,
    )


def number_list(items, style):
    return ListFlowable(
        [ListItem(Paragraph(item, style), leftIndent=8) for item in items],
        bulletType="1",
        leftIndent=18,
        bulletOffsetY=1,
        spaceAfter=4,
    )


def team_table(styles):
    data = [
        ["Kişi", "Ana Sorumluluk", "Temel Odak"],
        ["Kişi 1", "Proje yönetimi / Product", "Backlog, sprint planı, user flow, demo senaryosu"],
        ["Kişi 2", "Mobil geliştirme 1", "Expo yapısı, navigation, onboarding, profil ekranı"],
        ["Kişi 3", "Mobil geliştirme 2 + entegrasyon", "Öneriler, detay, kaydedilenler, backend bağlantısı"],
        ["Kişi 4", "Backend / API", "FastAPI, endpointler, veri modelleri, response yapıları"],
        ["Kişi 5", "AI / veri + dokümantasyon desteği", "Recommendation scoring, sentetik veri, test verileri, README desteği"],
    ]
    wrapped = []
    for ridx, row in enumerate(data):
        wrapped_row = []
        for cell in row:
            st = styles["BodyCM"] if ridx else styles["SmallCM"]
            if ridx == 0:
                wrapped_row.append(Paragraph(f"<b>{cell}</b>", st))
            else:
                wrapped_row.append(Paragraph(cell, st))
        wrapped.append(wrapped_row)

    table = Table(wrapped, colWidths=[0.9 * inch, 2.05 * inch, 3.05 * inch], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHTER]),
                ("BOX", (0, 0), (-1, -1), 0.75, MID),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, MID),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def role_block(title, items, styles):
    parts = [Paragraph(title, styles["SubSectionCM"]), bullet_list(items, styles["BodyCM"])]
    return parts


def add_page(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT_REGULAR, 9)
    canvas.setFillColor(SLATE)
    canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, doc.pagesize[1] - 0.55 * inch, "CampusMatch AI | Ekip Planı")
    canvas.drawCentredString(doc.pagesize[0] / 2, 0.55 * inch, "Group 132 - YZTA Bootcamp 2026")
    canvas.restoreState()


def build_pdf():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    styles = build_styles()
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=letter,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=0.85 * inch,
    )

    story = [
        Paragraph("CampusMatch AI", styles["TitleCM"]),
        Paragraph("Ekip Görev Dağılımı ve Çalışma Planı", styles["SubtitleCM"]),
    ]

    callout = Table(
        [[Paragraph("Amaç: Projeyi ana hatlara bölmek, 5 kişilik ekip içinde sorumlulukları netleştirmek ve Sprint 2 sürecinde paralel ama kontrollü bir ilerleme sağlamak.", styles["CalloutCM"])]],
        colWidths=[6.1 * inch],
        hAlign="CENTER",
    )
    callout.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT),
                ("BOX", (0, 0), (-1, -1), 0.5, MID),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    story.extend([callout, Spacer(1, 0.18 * inch)])

    story.append(Paragraph("Projenin Ana Hatları", styles["SectionCM"]))
    story.append(
        bullet_list(
            [
                "Ürün ve proje yönetimi",
                "Mobil uygulama geliştirme",
                "Backend ve API geliştirme",
                "AI / recommendation ve veri tarafı",
                "Dokümantasyon, test ve demo hazırlığı",
            ],
            styles["BodyCM"],
        )
    )

    story.append(Paragraph("Önerilen Ekip Dağılımı", styles["SectionCM"]))
    story.extend([team_table(styles), Spacer(1, 0.16 * inch)])

    story.append(Paragraph("Rol Bazlı Sorumluluklar", styles["SectionCM"]))
    role_sections = [
        ("1. Proje Yönetimi / Product", [
            "Backlog yönetimi ve görev dağılımı",
            "Sprint planlama ve öncelik sıralama",
            "User flow ve MVP kapsamını güncel tutma",
            "Demo senaryosu ve ekip koordinasyonu",
        ]),
        ("2. Mobil Geliştirme 1", [
            "React Native / Expo temel yapısı",
            "Navigation kurulumu",
            "Onboarding ve profil oluşturma ekranı",
            "Ortak component yapısı",
        ]),
        ("3. Mobil Geliştirme 2 + Entegrasyon", [
            "Etkinlik önerileri ekranı",
            "Etkinlik detay ekranı ve kaydedilenler",
            "Backend entegrasyonu",
            "UI düzenlemeleri ve kullanıcı akışı iyileştirmeleri",
        ]),
        ("4. Backend / API", [
            "FastAPI proje yapısı",
            "GET /health, GET /students, GET /clubs, GET /events",
            "POST /recommendations/student/{student_id}",
            "Veri modelleri ve response yapıları",
        ]),
        ("5. AI / Veri + Dokümantasyon", [
            "Sentetik veri yapısı ve örnek test verileri",
            "Recommendation scoring mantığı",
            "Açıklanabilir öneri metni",
            "README ve sprint doküman desteği",
        ]),
    ]
    for title, items in role_sections:
        story.extend(role_block(title, items, styles))

    story.append(PageBreak())
    story.append(Paragraph("Çalışma Prensibi ve Öncelik Sırası", styles["SectionCM"]))
    story.append(
        bullet_list(
            [
                "Herkesin bir ana sorumluluğu olacak.",
                "Her işin tek sahibi olacak, gerekirse destekli yürütülecek.",
                "Bağımlı işler yüzünden bekleme olursa mock data veya fake response ile ilerleme yapılacak.",
                "Öncelik öğrenci tarafı MVP olacak; kulüp yöneticisi tarafı ikinci aşamada genişletilecek.",
            ],
            styles["BodyCM"],
        )
    )

    story.append(Paragraph("Öncelik Sırası", styles["SubSectionCM"]))
    story.append(
        number_list(
            [
                "Ürün netliği ve backlog",
                "Öğrenci tarafı mobil ekranlar",
                "Backend endpointleri",
                "Recommendation mantığı",
                "Entegrasyon",
                "Demo ve dokümantasyon",
            ],
            styles["BodyCM"],
        )
    )

    story.append(Paragraph("Kısa Durum Mantığı", styles["SectionCM"]))
    story.append(
        bullet_list(
            [
                "Mobil ekip, backend tamamen bitmeden mock veriyle çalışabilir.",
                "Backend ekip, AI tamamen bitmeden fake response ile ilerleyebilir.",
                "AI ekip, mobil tamamen hazır olmadan veri ve scoring testleri yapabilir.",
                "Product tarafı tüm bu süreci birbirine bağlar.",
            ],
            styles["BodyCM"],
        )
    )

    story.append(Paragraph("Haftalık Mini Çalışma Şablonu", styles["SubSectionCM"]))
    story.append(
        number_list(
            [
                "Haftanın başı: görev dağılımı ve öncelik netleştirme",
                "Hafta ortası: kısa ilerleme kontrolü",
                "Hafta sonu: çıkan işlerin birleştirilmesi ve eksiklerin görülmesi",
            ],
            styles["BodyCM"],
        )
    )

    note = Table(
        [[Paragraph("Not: Amaç herkesin aynı anda her şeyi yapması değil, doğru zamanda doğru parçayı üretmesidir. Paralel çalışma desteklenir; ancak bağımlılıklar erken fark edilip iletişim sık tutulmalıdır.", styles["BodyCM"])]],
        colWidths=[6.1 * inch],
        hAlign="CENTER",
    )
    note.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.75, BLUE),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
            ]
        )
    )
    story.extend([Spacer(1, 0.15 * inch), note])

    doc.build(story, onFirstPage=add_page, onLaterPages=add_page)
    print(PDF_PATH)


if __name__ == "__main__":
    build_pdf()
