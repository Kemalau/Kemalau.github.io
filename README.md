# Li Yuejia Academic Homepage

This is a lightweight static academic homepage for GitHub Pages.

## Local Preview

Open `index.html` directly in a browser, or run:

```bash
python -m http.server 8000
```

Then visit `http://localhost:8000`.

## Blog

The blog lives at `/blog/`. Article sources are in `blog/posts/`; titles,
publication dates, and summaries are listed in `blog/posts.json`.

After editing or adding a Markdown post, rebuild the committed HTML pages:

```bash
python -m pip install -r scripts/requirements-blog.txt
npm ci --ignore-scripts
python scripts/build_blog.py
```

Preview with the local server above. The blog uses locally hosted ET Book fonts
with their license in `blog/assets/fonts/LICENSE`. Full-size figures open when
clicked. Push the source and generated HTML to `main` to publish via GitHub Pages.

Use fenced `math` blocks for display equations and `$...$` for inline equations.
The build renders KaTeX HTML and accessible MathML, and copies its licensed fonts
and CSS locally; visitors do not need a third-party script for the equations.
Article headings automatically form the desktop sidebar and mobile table of
contents. The sidebar follows the current section as readers scroll.

The build adds content versions to homepage and blog CSS/JavaScript URLs, so a
browser with an older cached stylesheet fetches the matching styles after an
update. Run the same build after editing `stylesheet.css` or blog assets.

## CV

The homepage links to `files/Li_Yuejia_CV.pdf`. To regenerate it after editing
`scripts/build_cv.py`, install ReportLab and run:

```bash
python scripts/build_cv.py
```

The CV uses Charter on macOS and falls back to Times where Charter is unavailable.

## Publish With GitHub Pages

For a GitHub user site, the repository name should be:

```text
Kemalau.github.io
```

Then publish from the `main` branch with GitHub Pages.

## Content To Replace

- Replace `images/profile.jpg` with a real headshot.
- Add public papers to the Publications section only after they are public.
