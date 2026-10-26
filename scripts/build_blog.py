#!/usr/bin/env python3
"""Build static Markdown pages with pre-rendered equations and article navigation."""
from __future__ import annotations

import html
import json
import re
import shutil
import subprocess
from datetime import date
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"
SITE = "https://kemalau.github.io"


def inline_math(state, silent):
    """Recognize dollar-delimited inline TeX before Markdown text parsing."""
    start = state.pos
    if state.src[start] != "$" or state.src.startswith("$$", start):
        return False
    match = re.match(r"\$([^\n$]+?)(?<!\\)\$", state.src[start:state.posMax])
    if not match or match[1] != match[1].strip():
        return False
    if not silent:
        token = state.push("math_inline", "math", 0)
        token.content = match[1]
    state.pos += len(match[0])
    return True


def typeset_math(tokens):
    formulas, math_tokens = [], []
    for token in tokens:
        for candidate in [token, *(token.children or [])]:
            display = candidate.type == "fence" and candidate.info.strip() == "math"
            if display or candidate.type == "math_inline":
                formulas.append({"latex": candidate.content, "display": display})
                math_tokens.append(candidate)
    if not formulas:
        return False
    result = subprocess.run(
        ["node", str(ROOT / "scripts/render_math.cjs")],
        input=json.dumps(formulas), capture_output=True, text=True, check=True, cwd=ROOT,
    )
    rendered = json.loads(result.stdout)
    for token, formula, markup in zip(math_tokens, formulas, rendered, strict=True):
        display = formula["display"]
        tag, style = ("div", "math-display") if display else ("span", "math-inline")
        attributes = ' tabindex="0" role="region" aria-label="Equation"' if display else ""
        token.type = "html_block" if display else "html_inline"
        token.content = f'<{tag} class="{style}"{attributes}>{markup}</{tag}>' + ("\n" if display else "")
    return True


def copy_math_assets():
    source = ROOT / "node_modules/katex"
    target = BLOG / "assets/katex"
    target.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source / "dist/katex.min.css", target / "katex.min.css")
    shutil.copy2(source / "LICENSE", target / "LICENSE")
    shutil.copytree(source / "dist/fonts", target / "fonts", dirs_exist_ok=True)


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def date_label(value: str) -> str:
    return date.fromisoformat(value).strftime("%d %B %Y").lstrip("0")


def render_markdown(source: Path):
    text = source.read_text()
    # The title/date are rendered by the page header, with source prose intact.
    text = re.sub(r"\A# [^\n]+\n+\*[^\n]+\*\n+", "", text, count=1)
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
    md.inline.ruler.before("escape", "math_inline", inline_math)
    tokens = md.parse(text)
    headings = []
    used = set()
    for i, token in enumerate(tokens):
        if token.type == "heading_open":
            title = tokens[i + 1].content
            anchor = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "section"
            candidate, suffix = anchor, 2
            while candidate in used:
                candidate = f"{anchor}-{suffix}"
                suffix += 1
            used.add(candidate)
            token.attrSet("id", candidate)
            if token.tag == "h2":
                headings.append((candidate, title))
        for child in token.children or []:
            if child.type == "image":
                child.attrSet("loading", "lazy")
                child.attrSet("decoding", "async")
    has_math = typeset_math(tokens)
    body = md.renderer.render(tokens, md.options, {})
    body = re.sub(
        r'<p>(<img\s[^>]+>)</p>\s*<p><em>(Figure[^<]*(?:<(?!/em>)[^>]*>[^<]*)*)</em></p>',
        lambda m: '<figure><a href="' + re.search(r'src="([^"]+)"', m[1])[1]
        + '" aria-label="Open full-size figure">' + m[1]
        + '</a><figcaption>' + m[2] + '</figcaption></figure>',
        body,
    )
    body = body.replace("<table>", '<div class="table-scroll"><table>').replace("</table>", "</table></div>")
    return body, headings, has_math


def shell(title: str, description: str, path: str, content: str, *, article=False, has_math=False):
    image_meta = ('<meta property="og:image" content="' + SITE
                  + '/blog/assets/sparse-mlp-neurons/figure_rq2.png">') if article else ""
    document = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)} · Li Yuejia</title>
  <meta name="description" content="{escape(description)}">
  <link rel="canonical" href="{SITE}{path}">
  <meta property="og:type" content="{'article' if article else 'website'}">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(description)}">
  <meta property="og:url" content="{SITE}{path}">
  {image_meta}
  <link rel="preload" href="/blog/assets/fonts/et-book-roman.woff" as="font" type="font/woff" crossorigin>
  <link rel="stylesheet" href="/blog/blog.css">
  {'<link rel="stylesheet" href="/blog/assets/katex/katex.min.css">' if has_math else ''}
  {'<script src="/blog/navigation.js" defer></script>' if article else ''}
</head>
<body>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <a class="site-name" href="/">Li Yuejia</a>
    <nav class="site-nav" aria-label="Main navigation">
      <a href="/">Home</a>
      <a href="/blog/"{' aria-current="page"' if path == '/blog/' else ''}>Blog</a>
      <a href="https://github.com/Kemalau">GitHub</a>
    </nav>
  </header>
  <main id="main"{' class="article-page"' if article else ''}>{content}</main>
  <footer class="site-footer"><p>Li Yuejia · Research notes &amp; ideas</p></footer>
</body>
</html>
'''
    return "\n".join(line.rstrip() for line in document.splitlines()) + "\n"


def build_article(post: dict, *, appendix=False):
    source_name = post["appendix" if appendix else "source"]
    source = BLOG / "posts" / source_name
    body, headings, has_math = render_markdown(source)
    title = "Technical Appendix: Discovery, Intervention, and Evidence" if appendix else post["title"]
    path = f'/blog/{post["slug"]}/' + ("appendix/" if appendix else "")
    toc = "".join(f'<li><a href="#{anchor}">{escape(label)}</a></li>' for anchor, label in headings)
    related = (f'<a href="/blog/{post["slug"]}/">Read the article</a>' if appendix else
               f'<a href="/blog/{post["slug"]}/appendix/">Technical appendix</a>') if post.get("appendix") else ""
    content = f'''
    <aside class="toc-sidebar" aria-label="Article navigation">
      <a class="toc-title" href="#article-top">{escape(title)}</a>
      <nav aria-label="Table of contents"><ol>{toc}</ol></nav>
    </aside>
    <article class="post" id="article-top">
      <header class="post-header">
        <p class="eyebrow">{'Technical appendix' if appendix else escape(post['category'])}</p>
        <h1>{escape(title)}</h1>
        <p class="post-meta">Li Yuejia <span class="separator">·</span> <time datetime="{post['date']}">{date_label(post['date'])}</time></p>
        <div class="post-tools"><a href="/blog/posts/{source_name}">Markdown</a>{related}</div>
      </header>
      <details class="toc"><summary>On this page</summary><ol>{toc}</ol></details>
      <div class="article-body">{body}</div>
    </article>
    '''
    target = ROOT / path.strip("/") / "index.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(shell(title, post["description"], path, content, article=True, has_math=has_math))


def main():
    copy_math_assets()
    posts = sorted(json.loads((BLOG / "posts.json").read_text()), key=lambda p: p["date"], reverse=True)
    cards = []
    for post in posts:
        build_article(post)
        if post.get("appendix"):
            build_article(post, appendix=True)
        cards.append(f'''<article class="post-card">
          <p class="post-meta"><time datetime="{post['date']}">{date_label(post['date'])}</time> · {escape(post['category'])}</p>
          <h2><a href="/blog/{post['slug']}/">{escape(post['title'])}</a></h2>
          <p>{escape(post['description'])}</p>
          <a class="read-link" href="/blog/{post['slug']}/">Read the article <span aria-hidden="true">→</span></a>
        </article>''')
    content = '<header><p class="eyebrow">Notes from research</p><h1>Blog</h1><p>On understanding AI systems, their behavior, and alignment.</p></header><section class="post-list" aria-label="Articles">' + "".join(cards) + '</section>'
    (BLOG / "index.html").write_text(shell("Blog", "Research notes by Li Yuejia on AI systems, model behavior, and alignment.", "/blog/", content))
    print(f"Built blog index and {len(posts)} article(s).")


if __name__ == "__main__":
    main()
