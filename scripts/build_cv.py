"""Build Yuejia Li's academic CV in the supplied reference CV's style."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Flowable, HRFlowable, KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

OUTPUT = Path(__file__).resolve().parents[1] / 'files/Li_Yuejia_CV.pdf'
PAGE_W, _ = A4
MARGIN = 43
WIDTH = PAGE_W - 2 * MARGIN
BLACK = colors.HexColor('#111111')
BLUE = '#174C9A'
LINK = f'color="{BLUE}"'
CHARTER = Path('/System/Library/Fonts/Supplemental/Charter.ttc')
if CHARTER.exists():
    for name, index in [('Charter', 0), ('Charter-Italic', 1),
                        ('Charter-BoldItalic', 2), ('Charter-Bold', 3)]:
        pdfmetrics.registerFont(TTFont(name, str(CHARTER), subfontIndex=index))
    pdfmetrics.registerFontFamily('Charter', normal='Charter', bold='Charter-Bold',
                                  italic='Charter-Italic', boldItalic='Charter-BoldItalic')
    REGULAR, BOLD, ITALIC = 'Charter', 'Charter-Bold', 'Charter-Italic'
else:
    REGULAR, BOLD, ITALIC = 'Times-Roman', 'Times-Bold', 'Times-Italic'

styles = {
    'name': ParagraphStyle('name', fontName=REGULAR, fontSize=22.5, leading=25, textColor=BLACK, spaceAfter=2),
    'subtitle': ParagraphStyle('subtitle', fontName=REGULAR, fontSize=10.5, leading=13.2, textColor=BLACK, spaceAfter=5),
    'contact': ParagraphStyle('contact', fontName=REGULAR, fontSize=8.7, leading=11, textColor=BLACK, spaceAfter=3),
    'section': ParagraphStyle('section', fontName=BOLD, fontSize=13.8, leading=16.5, textColor=BLACK, spaceBefore=8, spaceAfter=1),
    'body': ParagraphStyle('body', fontName=REGULAR, fontSize=10.3, leading=12.5, textColor=BLACK),
    'small': ParagraphStyle('small', fontName=REGULAR, fontSize=9.3, leading=11.7, textColor=BLACK),
    'title': ParagraphStyle('title', fontName=BOLD, fontSize=10.6, leading=12.5, textColor=BLACK),
    'date': ParagraphStyle('date', fontName=REGULAR, fontSize=10.1, leading=12.5, textColor=BLACK, alignment=TA_RIGHT),
    'venue': ParagraphStyle('venue', fontName=ITALIC, fontSize=9.5, leading=11.7, textColor=BLACK),
}
styles['intern_body'] = ParagraphStyle('intern_body', parent=styles['body'], leftIndent=17)
styles['intern_small'] = ParagraphStyle('intern_small', parent=styles['small'], leftIndent=17)


class MicrosoftMark(Flowable):
    """Small vector version of the four-square Microsoft symbol."""

    def __init__(self):
        super().__init__()
        self.width = self.height = 12

    def draw(self):
        side, gap = 5.3, 1.4
        squares = (
            (0, side + gap, '#F25022'),
            (side + gap, side + gap, '#7FBA00'),
            (0, 0, '#00A4EF'),
            (side + gap, 0, '#FFB900'),
        )
        for x, y, color in squares:
            self.canv.setFillColor(colors.HexColor(color))
            self.canv.rect(x, y, side, side, stroke=0, fill=1)

def p(value, style='body'):
    return Paragraph(value, styles[style])

def section(value):
    return [p(value, 'section'), HRFlowable(width='100%', thickness=0.6, color=BLACK, spaceAfter=7)]

def row(left, right='', left_style='title'):
    table = Table([[p(left, left_style), p(right, 'date')]], colWidths=[WIDTH - 114, 114])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    return table


def microsoft_row(left, right):
    table = Table([[MicrosoftMark(), p(left, 'title'), p(right, 'date')]],
                  colWidths=[17, WIDTH - 17 - 114, 114])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    return table

def bullet(value, gap=3):
    table = Table([[p('&#8226;'), p(value)]], colWidths=[14, WIDTH - 14])
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    return [table, Spacer(1, gap)]

def pub(title, url, authors, venue):
    linked = f'<link href="{url}" {LINK}>{title}</link>' if url else title
    return KeepTogether([
        row('&#8226;&nbsp;&nbsp;' + linked), p(authors, 'small'), p(venue, 'venue'), Spacer(1, 8),
    ])

story = [
    p('Yuejia Li', 'name'),
    p('Undergraduate Student in Computer Science and Technology @ Wuhan University', 'subtitle'),
    p(f'<link href="mailto:2024302111194@whu.edu.cn" {LINK}>2024302111194@whu.edu.cn</link>'
      '  &#183;  (+86) 152 7216 1950  &#183;  '
      f'<link href="https://scholar.google.com/citations?user=p9oPgT0AAAAJ" {LINK}>Google Scholar</link>'
      '  &#183;  ' f'<link href="https://github.com/Kemalau" {LINK}>GitHub</link>'
      '  &#183;  ' f'<link href="https://kemalau.github.io/" {LINK}>Homepage</link>', 'contact'),
]
story += section('Research &amp; Selected Experiences')
story += bullet('My research interests include <b>representation learning</b>, <b>explainable AI</b>, <b>responsible AI</b>, and <b>multimodal learning</b>.')
story += bullet('Co-developed Semantic Consistency Learning for cross-species animal re-identification (<b>ECCV 2026</b>); evaluated on 11 datasets covering 40+ species, with the best Rank-1 and mAP on 8 of 10 unseen datasets.', 1)
story += bullet('Our work on threshold-stable selective classification for FOIA privilege review was selected for an <b>NLPCC 2026 oral presentation</b>.', 1)

story += section('Education')
story.append(KeepTogether([
    row('Undergraduate, Computer Science and Technology (Hongyi Honor Class)', '2024-2028 (expected)'),
    row('Wuhan University', 'Wuhan, China', 'body'),
    p('Research supervisor: Prof. Mang Ye  &#183;  Average score: 88.5/100', 'small'), Spacer(1, 4),
]))

story += section('Internship Experience')
story.append(KeepTogether([
    microsoft_row('Microsoft Research Asia, Star of Tomorrow Research Intern', 'Summer 2026'),
    p(f'Social Computing Group  &#183;  Mentor: <link href="https://www.microsoft.com/en-us/research/people/fangzwu/" {LINK}>Fangzhao Wu</link>', 'intern_body'),
    p('Project 1: Radioactive Feedback: Tracing Models Trained by Proprietary LLM Judges <i>(under review at ICLR 2027)</i>', 'intern_small'),
    p('Project 2: On the Vulnerability of Semantic IDs in Generative Recommendation <i>(under review at ICLR 2027)</i>', 'intern_small'),
    p('Project 3: Towards Unbiased Generative Recommendation <i>(under review at ICLR 2027)</i>', 'intern_small'),
    p('Project 4: On the Mechanisms of Safety Failure in Large Language Models<br/><i>(under review at Nature Machine Intelligence)</i>', 'intern_small'),
    Spacer(1, 3),
]))

story += section('Publications &amp; Preprints')
story.append(pub('Cross-Species Animal Re-Identification with Semantic Consistency Learning',
    'https://arxiv.org/abs/2609.09705',
    'Shuoyi Chen*, <b>Yuejia Li*</b>, Mang Ye  (* equal contribution)', 'ECCV 2026'))
story.append(pub('See Before You Code: Learning Visual Priors for Spatially Aware Educational Animation Generation',
    'https://arxiv.org/abs/2605.15585',
    '<b>Yuejia Li*</b>, Ke He*, Junheng Li, Shutong Chen, Jingkang Xia, Zhiyue Su, Junchi Zhang, Mang Ye  (* equal contribution)', 'arXiv preprint, 2026'))
story.append(pub('FedDiG: Federated Continual Graph Learning with Disentangled Generative Replay', None,
    '<b>Yuejia Li*</b>, Zihan Tan*, Wenke Huang, Bin Yang, Mang Ye  (* equal contribution)',
    'Under review at ICLR 2027'))

story += section('Ongoing Research')
story.append(KeepTogether([
    row('AI-Assisted Learning Silently Degrades Metacognition', 'In progress'),
    p('Yuejia Li, Synesis AI  &#183;  Supervisor: Mang Ye', 'small'),
    p('Developing a Bayesian cognitive model, behavioral observation framework, pseudo-understanding risk index, and cognition-aware interventions; a prototype and small-scale validation are complete.', 'small'), Spacer(1, 2),
]))

story += section('Community Contributions &amp; Projects')
story += bullet(f'<link href="http://synesis.cn" {LINK}><b>Synesis AI</b></link> (co-founder and technical lead, 2025-present): AI-assisted learning products and multimodal teaching tools.')
story += bullet(f'<link href="https://github.com/billion-token-one-task/Deepgraph" {LINK}><b>DeepGraph</b></link> (creator, 2026-present): research agent for literature discovery, proposal generation, experiment planning, and code execution.')
story += bullet(f'<link href="https://github.com/billion-token-one-task/ClawOSS" {LINK}><b>ClawOSS</b></link> (co-author, 2026-present): open-source maintenance agent; project pull requests have been merged by PyPI, OpenClaw, and ByteDance DeepFlow.')
story += bullet(f'<link href="https://github.com/openclaw/openclaw" {LINK}><b>OpenClaw</b></link> (contributor, 2026-present): agent workflow automation and engineering infrastructure.', 1)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
SimpleDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=29, bottomMargin=28, title='Yuejia Li - Curriculum Vitae', author='Yuejia Li',
    subject='English academic curriculum vitae').build(story)
print(OUTPUT)
