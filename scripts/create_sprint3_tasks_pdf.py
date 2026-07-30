from __future__ import annotations

import re
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "scrum" / "sprint-3" / "yapilmasi-gerekenler.md"
OUTPUT = ROOT / "output" / "pdf" / "Sprint_3_Yapilmasi_Gerekenler.pdf"

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_X = 18 * mm
MARGIN_TOP = 20 * mm
MARGIN_BOTTOM = 17 * mm

INK = colors.HexColor("#153D35")
PRIMARY = colors.HexColor("#256F63")
PRIMARY_SOFT = colors.HexColor("#DCEFE9")
CREAM = colors.HexColor("#FFF0D8")
PAPER = colors.HexColor("#F5FAF7")
MUTED = colors.HexColor("#687A75")
BORDER = colors.HexColor("#D6E3DE")
WHITE = colors.white


def register_fonts() -> None:
    pdfmetrics.registerFont(TTFont("Campus", r"C:\Windows\Fonts\arial.ttf"))
    pdfmetrics.registerFont(TTFont("Campus-Bold", r"C:\Windows\Fonts\arialbd.ttf"))


def parse_markdown() -> tuple[str, str, list[tuple[str, list[tuple[bool, str]]]], list[str], list[str]]:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    title = lines[0].removeprefix("# ")
    intro = lines[2]
    sections: list[tuple[str, list[tuple[bool, str]]]] = []
    order: list[str] = []
    done_criteria: list[str] = []
    current_title = ""
    current_items: list[tuple[bool, str]] = []
    mode = "sections"

    for line in lines[3:]:
        if line == "## Önerilen Çalışma Sırası":
            if current_title:
                sections.append((current_title, current_items))
            current_title, current_items = "", []
            mode = "order"
            continue
        if line == "## Projenin Bitmiş Sayılması İçin":
            mode = "done"
            continue
        if line.startswith("## ") and mode == "sections":
            if current_title:
                sections.append((current_title, current_items))
            current_title = line.removeprefix("## ")
            current_items = []
            continue
        task_match = re.match(r"- \[([ x])\] (.+)", line)
        if task_match and mode == "sections":
            current_items.append((task_match.group(1) == "x", task_match.group(2)))
            continue
        order_match = re.match(r"\d+\. (.+)", line)
        if order_match and mode == "order":
            order.append(order_match.group(1))
            continue
        if line.startswith("- ") and mode == "done":
            done_criteria.append(line.removeprefix("- "))

    return title, intro, sections, order, done_criteria


def styles():
    base = getSampleStyleSheet()
    return {
        "cover_eyebrow": ParagraphStyle(
            "CoverEyebrow", parent=base["Normal"], fontName="Campus-Bold", fontSize=9,
            leading=12, textColor=PRIMARY, tracking=2.2, alignment=TA_CENTER,
        ),
        "cover_title": ParagraphStyle(
            "CoverTitle", parent=base["Title"], fontName="Campus-Bold", fontSize=27,
            leading=32, textColor=INK, alignment=TA_CENTER, spaceAfter=8,
        ),
        "cover_intro": ParagraphStyle(
            "CoverIntro", parent=base["BodyText"], fontName="Campus", fontSize=11,
            leading=17, textColor=MUTED, alignment=TA_CENTER,
        ),
        "section": ParagraphStyle(
            "Section", parent=base["Heading2"], fontName="Campus-Bold", fontSize=15,
            leading=19, textColor=INK, spaceAfter=7,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName="Campus", fontSize=9.2,
            leading=13, textColor=INK,
        ),
        "body_muted": ParagraphStyle(
            "BodyMuted", parent=base["BodyText"], fontName="Campus", fontSize=8.6,
            leading=12, textColor=MUTED,
        ),
        "task": ParagraphStyle(
            "Task", parent=base["BodyText"], fontName="Campus", fontSize=9,
            leading=12.5, textColor=INK,
        ),
        "task_done": ParagraphStyle(
            "TaskDone", parent=base["BodyText"], fontName="Campus", fontSize=9,
            leading=12.5, textColor=MUTED,
        ),
        "number": ParagraphStyle(
            "Number", parent=base["Normal"], fontName="Campus-Bold", fontSize=10,
            leading=12, textColor=WHITE, alignment=TA_CENTER,
        ),
        "small_bold": ParagraphStyle(
            "SmallBold", parent=base["Normal"], fontName="Campus-Bold", fontSize=8,
            leading=10, textColor=PRIMARY,
        ),
    }


def page_chrome(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(PAPER)
    canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    canvas.setFillColor(PRIMARY_SOFT)
    canvas.circle(PAGE_WIDTH - 12 * mm, PAGE_HEIGHT - 4 * mm, 24 * mm, fill=1, stroke=0)
    canvas.setFillColor(CREAM)
    canvas.circle(5 * mm, 8 * mm, 20 * mm, fill=1, stroke=0)
    canvas.setStrokeColor(BORDER)
    canvas.line(MARGIN_X, 12 * mm, PAGE_WIDTH - MARGIN_X, 12 * mm)
    canvas.setFont("Campus", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN_X, 7.5 * mm, "CampusMatch AI - Sprint 3")
    canvas.drawRightString(PAGE_WIDTH - MARGIN_X, 7.5 * mm, f"Sayfa {doc.page}")
    canvas.restoreState()


def task_card(section_title: str, tasks: list[tuple[bool, str]], style_map) -> KeepTogether:
    rows = []
    for completed, task in tasks:
        status = "TAMAM" if completed else ""
        status_color = PRIMARY if completed else BORDER
        rows.append(
            [
                Paragraph(status, style_map["small_bold"]),
                Paragraph(task.replace("→", "-&gt;"), style_map["task_done"] if completed else style_map["task"]),
            ]
        )
    table = Table(rows, colWidths=[18 * mm, 142 * mm], hAlign="LEFT")
    commands = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5.5),
        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
        ("BOX", (0, 0), (-1, -1), 0.7, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.35, BORDER),
    ]
    for index, (completed, _) in enumerate(tasks):
        commands.append(("BACKGROUND", (0, index), (0, index), PRIMARY_SOFT if completed else colors.HexColor("#F8FBF9")))
    table.setStyle(TableStyle(commands))
    return KeepTogether([Paragraph(section_title, style_map["section"]), table, Spacer(1, 6 * mm)])


def build_pdf() -> None:
    register_fonts()
    title, intro, sections, order, done_criteria = parse_markdown()
    style_map = styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    frame = Frame(
        MARGIN_X, MARGIN_BOTTOM, PAGE_WIDTH - 2 * MARGIN_X,
        PAGE_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM, id="content", showBoundary=0,
    )
    doc = BaseDocTemplate(
        str(OUTPUT), pagesize=A4, leftMargin=MARGIN_X, rightMargin=MARGIN_X,
        topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
        title=title, author="CampusMatch AI",
    )
    doc.addPageTemplates([PageTemplate(id="CampusMatch", frames=[frame], onPage=page_chrome)])

    completed = sum(1 for _, tasks in sections for is_done, _ in tasks if is_done)
    total = sum(len(tasks) for _, tasks in sections)
    story = [
        Spacer(1, 18 * mm),
        Paragraph("CAMPUSMATCH AI", style_map["cover_eyebrow"]),
        Spacer(1, 4 * mm),
        Paragraph(title, style_map["cover_title"]),
        Paragraph(intro, style_map["cover_intro"]),
        Spacer(1, 10 * mm),
    ]

    stats = Table(
        [
            [Paragraph(f"<b>{total}</b><br/><font size='8'>Toplam görev</font>", style_map["cover_intro"]),
             Paragraph(f"<b>{completed}</b><br/><font size='8'>Tamamlanan</font>", style_map["cover_intro"]),
             Paragraph(f"<b>{len(sections)}</b><br/><font size='8'>Ana çalışma alanı</font>", style_map["cover_intro"])],
        ],
        colWidths=[53 * mm] * 3,
        rowHeights=[23 * mm],
    )
    stats.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
        ("BOX", (0, 0), (-1, -1), 0.8, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.extend([stats, Spacer(1, 14 * mm)])

    for section_title, tasks in sections:
        story.append(task_card(section_title, tasks, style_map))

    story.extend([PageBreak(), Paragraph("Önerilen Çalışma Sırası", style_map["section"]), Spacer(1, 2 * mm)])
    for index, item in enumerate(order, start=1):
        number = Table([[Paragraph(str(index), style_map["number"])]], colWidths=[8 * mm], rowHeights=[8 * mm])
        number.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PRIMARY), ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        row = Table([[number, Paragraph(item, style_map["body"])]], colWidths=[12 * mm, 148 * mm])
        row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
        story.append(row)
    story.extend([Spacer(1, 7 * mm), Paragraph("Projenin Bitmiş Sayılması İçin", style_map["section"])])

    criteria_rows = [[Paragraph("-", style_map["small_bold"]), Paragraph(item, style_map["body"])] for item in done_criteria]
    criteria = Table(criteria_rows, colWidths=[7 * mm, 153 * mm])
    criteria.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PRIMARY_SOFT),
        ("BOX", (0, 0), (-1, -1), 0.8, PRIMARY),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story.append(criteria)
    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    build_pdf()
