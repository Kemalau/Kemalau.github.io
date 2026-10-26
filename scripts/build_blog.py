#!/usr/bin/env python3
"""Build static blog pages from Markdown. No runtime JavaScript is required."""
from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
BLOG = ROOT / "blog"
SITE = "https://kemalau.github.io"


def escape(value: str) -> str:
    return html.escape(value, quote=True)


def date_label(value: str) -> str:
    return date.fromisoformat(value).strftime("%d %B %Y").lstrip("0")


def render_markdown(source: Path):
    text = source.read_text()
    # The title/date are rendered by the page header, with source prose intact.
    text = re.sub(r"\A# [^\n]+\n+\*[^\n]+\*\n+", "", text, count=1)
    md = MarkdownIt("commonmark", {"html": False}).enable("table")
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
    body = md.renderer.render(tokens, md.options, {})
    body = re.sub(
        r'<p>(<img\s[^>]+>)</p>\s*<p><em>(Figure[^<]*(?:<(?!/em>)[^>]*>[^<]*)*)</em></p>',
        lambda m: '<figure><a href="' + re.search(r'src="([^"]+)"', m[1])[1]
        + '" aria-label="Open full-size figure">' + m[1]
        + '</a><figcaption>' + m[2] + '</figcaption></figure>',
        body,
    )
    body = body.replace("<table>", '<div class="table-scroll"><table>').replace("</table>", "</table></div>")
    return body, headings


def shell(title: str, description: str, path: str, content: str, *, article=False):
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
  <main id="main">{content}</main>
  <footer class="site-footer"><p>Li Yuejia · Research notes &amp; ideas</p></footer>
</body>
</html>
'''
    return "\n".join(line.rstrip() for line in document.splitlines()) + "\n"


def build_article(post: dict, *, appendix=False):
    source_name = post["appendix" if appendix else "source"]
    source = BLOG / "posts" / source_name
    body, headings = render_markdown(source)
    title = "Technical Appendix: Discovery, Intervention, and Evidence" if appendix else post["title"]
    path = f'/blog/{post["slug"]}/' + ("appendix/" if appendix else "")
    toc = "".join(f'<li><a href="#{anchor}">{escape(label)}</a></li>' for anchor, label in headings)
    related = (f'<a href="/blog/{post["slug"]}/">Read the article</a>' if appendix else
               f'<a href="/blog/{post["slug"]}/appendix/">Technical appendix</a>') if post.get("appendix") else ""
    content = f'''
    <article>
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
    target.write_text(shell(title, post["description"], path, content, article=True))


def main():
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
