"""Build Yuejia Li's academic CV in the supplied reference CV's style."""
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import BaseDocTemplate, Flowable, Frame, HRFlowable, Image, KeepTogether, PageTemplate, Paragraph, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'files/Li_Yuejia_CV.pdf'
UW_CREST = ROOT / 'images/uw-madison-crest.png'
WHU_SEAL = ROOT / 'images/wuhan-university-seal.png'
BERKELEY_SEAL = ROOT / 'images/uc-berkeley-seal.png'
PAGE_W, _ = A4
MARGIN = 43
WIDTH = PAGE_W - 2 * MARGIN
INSTITUTION_INDENT = 24
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
    'section': ParagraphStyle('section', fontName=BOLD, fontSize=13.8, leading=16.5, textColor=BLACK, spaceBefore=5, spaceAfter=1),
    'body': ParagraphStyle('body', fontName=REGULAR, fontSize=10.3, leading=12.5, textColor=BLACK),
    'small': ParagraphStyle('small', fontName=REGULAR, fontSize=9.3, leading=11.7, textColor=BLACK),
    'title': ParagraphStyle('title', fontName=BOLD, fontSize=10.6, leading=12.5, textColor=BLACK),
    'date': ParagraphStyle('date', fontName=REGULAR, fontSize=10.6, leading=12.5, textColor=BLACK, alignment=TA_RIGHT),
    'venue': ParagraphStyle('venue', fontName=ITALIC, fontSize=9.5, leading=11.7, textColor=BLACK),
}
styles['intern_body'] = ParagraphStyle('intern_body', parent=styles['body'], leftIndent=INSTITUTION_INDENT)
styles['intern_small'] = ParagraphStyle('intern_small', parent=styles['small'], leftIndent=INSTITUTION_INDENT)
styles['location'] = ParagraphStyle('location', parent=styles['body'], alignment=TA_RIGHT)
styles['publication_authors'] = ParagraphStyle('publication_authors', parent=styles['small'], leftIndent=14)
styles['publication_venue'] = ParagraphStyle('publication_venue', parent=styles['venue'], leftIndent=14)


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
    table = Table([[p(left, left_style), p(right, 'date')]], colWidths=[WIDTH - 114, 114], hAlign='LEFT')
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    return table


def institution_row(mark, left, right='', left_style='title'):
    right_style = 'date' if left_style == 'title' else 'location'
    table = Table([[mark if mark is not None else '', p(left, left_style), p(right, right_style)]],
                  colWidths=[INSTITUTION_INDENT, WIDTH - INSTITUTION_INDENT - 114, 114], hAlign='LEFT')
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (0, 0), 'CENTER'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    return table

def seal(path):
    return Image(str(path), width=16, height=16, kind='proportional', mask='auto')

def bullet(value, gap=3, text_style='body'):
    table = Table([[p('&#8226;', text_style), p(value, text_style)]], colWidths=[14, WIDTH - 14], hAlign='LEFT')
    table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0), ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 0), ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    return [table, Spacer(1, gap)]

def pub(title, url, authors, venue):
    linked = f'<link href="{url}" {LINK}>{title}</link>' if url else title
    return KeepTogether([
        *bullet(linked, 0, 'title'), p(authors, 'publication_authors'),
        *([p(venue, 'publication_venue')] if venue else []), Spacer(1, 5),
    ])

story = [
    p('Yuejia Li', 'name'),
    p('Undergraduate Student in Computer Science and Technology @ Wuhan University', 'subtitle'),
    p(f'<link href="mailto:liyuejia@whu.edu.cn" {LINK}>liyuejia@whu.edu.cn</link>'
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
    institution_row(seal(WHU_SEAL), 'Undergraduate, Computer Science and Technology (Hongyi Honor Class)', '2024-2028 (expected)'),
    institution_row(None, 'Wuhan University', 'Wuhan, China', 'body'),
    p('Research supervisor: Prof. Mang Ye  &#183;  Average score: 88.5/100', 'intern_small'), Spacer(1, 4),
]))
story.append(KeepTogether([
    institution_row(seal(BERKELEY_SEAL), 'Exchange Student', 'Jan. 2027 - May 2027'),
    institution_row(None, 'University of California, Berkeley', 'Berkeley, CA, USA', 'body'),
    Spacer(1, 4),
]))

story += section('Internship Experience')
story.append(KeepTogether([
    institution_row(seal(UW_CREST),
                    'University of Wisconsin-Madison, Research Assistant', 'Sep. 2026 - Nov. 2026'),
    p(f'Mentor: <link href="https://luoxiao12.github.io/" {LINK}>Xiao Luo</link>', 'intern_body'),
    p('Project: Multimodal Intent Recognition', 'intern_small'),
    Spacer(1, 2),
]))
story.append(KeepTogether([
    institution_row(MicrosoftMark(), 'Microsoft Research Asia, Star of Tomorrow Research Intern', 'Summer 2026'),
    p(f'Social Computing Group  &#183;  Mentor: <link href="https://www.microsoft.com/en-us/research/people/fangzwu/" {LINK}>Fangzhao Wu</link>', 'intern_body'),
    p('Project 1: Radioactive Feedback: Tracing Models Trained by Label-Only LLM Supervision', 'intern_small'),
    p('Project 2: On the Vulnerability of Semantic IDs in Generative Recommendation', 'intern_small'),
    p('Project 3: Towards Unbiased Generative Recommendation', 'intern_small'),
    p('Project 4: On the Mechanisms of Safety Failure in Large Language Models', 'intern_small'),
    Spacer(1, 3),
]))

story += section('Publications &amp; Preprints')
story.append(pub('Sparse Neural Control Of Unethical Behavior In Language Models', None,
    '<b>Yuejia Li</b>, Hao Wu, Ke He, Xiyuan Yang, Mang Ye, Fangzhao Wu', 'Manuscript, 2026'))
story.append(pub('Radioactive Feedback: Tracing Models Trained by Label-Only LLM Supervision',
    'https://arxiv.org/abs/2610.15685',
    '<b>Yuejia Li</b>, JunHeng Li, Hao Wu, Ke He, Mang Ye', 'arXiv preprint, 2026'))
story.append(pub('Cross-Species Animal Re-Identification with Semantic Consistency Learning',
    'https://arxiv.org/abs/2609.09705',
    'Shuoyi Chen*, <b>Yuejia Li*</b>, Mang Ye  (* equal contribution)', 'ECCV 2026'))
story.append(pub('See Before You Code: Learning Visual Priors for Spatially Aware Educational Animation Generation',
    'https://arxiv.org/abs/2605.15585',
    '<b>Yuejia Li*</b>, Ke He*, Junheng Li, Shutong Chen, Jingkang Xia, Zhiyue Su, Junchi Zhang, Mang Ye  (* equal contribution)', 'arXiv preprint, 2026'))
story.append(pub('FedDiG: Federated Continual Graph Learning with Disentangled Generative Replay', None,
    '<b>Yuejia Li*</b>, Zihan Tan*, Wenke Huang, Bin Yang, Mang Ye  (* equal contribution)',
    None))

story += section('Community Contributions &amp; Projects')
story += bullet(f'<link href="http://synesis.cn" {LINK}><b>Synesis AI</b></link> (co-founder and technical lead, 2025-present): AI-assisted learning products and multimodal teaching tools.')
story += bullet(f'<link href="https://deepgraph.joulebeat.com" {LINK}><b>DeepGraph</b></link> [<link href="https://github.com/billion-token-one-task/Deepgraph" {LINK}>GitHub</link>] (creator, 2026-present; <b>3.1k+ GitHub stars</b>): research agent for literature discovery, hypothesis generation, and experiment execution.')
story += bullet(f'<link href="https://github.com/billion-token-one-task/ClawOSS" {LINK}><b>ClawOSS</b></link> (co-author, 2026-present): open-source maintenance agent; project pull requests have been merged by PyPI, OpenClaw, and ByteDance DeepFlow.')
story += bullet(f'<link href="https://github.com/openclaw/openclaw" {LINK}><b>OpenClaw</b></link> (contributor, 2026-present): agent workflow automation and engineering infrastructure.', 1)

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
document = BaseDocTemplate(str(OUTPUT), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=29, bottomMargin=28, title='Yuejia Li - Curriculum Vitae', author='Yuejia Li',
    subject='English academic curriculum vitae')
document.addPageTemplates(PageTemplate(id='CV', frames=Frame(
    document.leftMargin, document.bottomMargin, document.width, document.height,
    leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)))
document.build(story)
print(OUTPUT)
