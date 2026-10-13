# kutcodelabs.com

The KutCode Labs website: the studio's home page, the MotionArea product page (`/motionarea/`) and its privacy
policy (linked from the Google Play listing as `https://kutcodelabs.com/motionarea/privacy/`). Plain static files —
HTML, one stylesheet, two small scripts and images. Served by GitHub Pages; the custom domain is in `CNAME`.

## Languages
Turkish pages live at `/` and `/motionarea/`; their English copies at `/en/` and `/en/motionarea/` are made from
them. Each page carries both languages and shows one (`lang.js`); the TR/EN buttons move between the two addresses.
The privacy policy keeps both languages on one page and shows the reader's.

## Search, sharing and AI answers
After editing a page, run from this folder:

    python tools/seo.py

It fills each page's `<!-- seo:start -->` block (title, description, canonical and language links, Open Graph and
Twitter cards, schema.org data — the FAQ data is read from the page's own FAQ), rewrites the English copies under
`en/`, and rewrites `sitemap.xml`. `robots.txt` lets search engines and AI assistants read everything; `llms.txt`
is a plain summary of the studio and MotionArea for AI assistants.
