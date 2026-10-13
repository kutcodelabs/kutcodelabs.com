#!/usr/bin/env python3
"""
Search and sharing tags for every page, the English copies, and the sitemap.

The Turkish pages are the source: index.html, motionarea/index.html and motionarea/privacy/index.html
(the privacy policy keeps both languages on one page). Edit those, then run, from the website folder:

    python tools/seo.py

It fills the block between <!-- seo:start --> and <!-- seo:end --> in each page's <head> (title,
description, canonical and language links, Open Graph and Twitter cards, structured data), writes
en/index.html and en/motionarea/index.html (the same page with English showing and its links kept in
English), and rewrites sitemap.xml. The FAQ data is read from the FAQ on the page itself, so the two
always say the same thing.
"""
import datetime, html, io, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://kutcodelabs.com"
TODAY = datetime.date.today().isoformat()
ORG_ID = SITE + "/#organization"
APP_ID = SITE + "/motionarea/#app"
LOCALE = {"tr": "tr_TR", "en": "en_US"}

GAMES = [
    ("jungle-run", "Jungle Run", "Jungle Run",
     "Yerinde koşarak kıvrılan orman yolunda yarış; eğilerek şerit değiştir, kütüklerin üstünden zıpla, dalların altından eğil.",
     "Run on the spot through a winding jungle; lean to change lanes, jump the logs and duck the branches."),
    ("gold-rain", "Altın Yağmuru", "Gold Rain",
     "Gökten altın yağıyor: sağa sola eğilerek altının altına koş ve yakala, bombalardan kaç.",
     "Gold is raining from the sky: lean left and right to run under it and catch it, and dodge the bombs."),
    ("red-light", "Kırmızı Işık, Yeşil Işık", "Red Light, Green Light",
     "Dev avcı şarkı söylerken koş, arkasını dönünce donup kal; kıpırdayan başa uçar.",
     "Run while the giant hunter sings and freeze when he turns round; anyone still moving flies back to the start."),
    ("wall-rush", "Duvar Koşusu", "Wall Rush",
     "Duvarlar geliyor: bedeninle deliğin şeklini yap, yoksa göle düşersin.",
     "Walls are coming: make the shape of the hole with your body, or splash into the lake."),
    ("snowball-towers", "Kartopu Kuleleri", "Snowball Towers",
     "Takım halinde kartopu savaşı: kar topla, elini kaldırıp nişan al ve karşı kulenin kardan adamlarını devir.",
     "A team snowball battle: scoop snow, raise your hand to aim and knock down the other tower's snowmen."),
    ("floor-piano", "Yer Piyanosu", "Floor Piano",
     "Aşağı inen parlayan tuşların üstüne zıpla ve ayaklarınla ünlü şarkıları çal.",
     "Jump onto the glowing tiles as they come down and play famous tunes with your feet."),
]

KEYWORDS_STUDIO = {
    "tr": "KutCode Labs, kutcodelabs, MotionArea, mobil oyun stüdyosu, bağımsız oyun stüdyosu, Türk oyun stüdyosu, "
          "hareketle oynanan oyun, hareket oyunu, kameralı oyun, telefon kamerasıyla oyun, vücut hareketiyle oynanan oyun, "
          "vücut takibi, hareket algılama, cihaz üzerinde yapay zekâ, aile oyunu, çocuk oyunu, parti oyunu, kumandasız oyun, "
          "Kinect alternatifi, TV'de oynanan telefon oyunu, Android oyun, mobil uygulama geliştirme",
    "en": "KutCode Labs, kutcodelabs, MotionArea, mobile game studio, independent game studio, motion games, "
          "camera games, games played with the phone camera, full-body motion game, body tracking, motion detection, "
          "on-device AI, family games, kids games, party games, controller-free games, Kinect alternative, "
          "phone game on TV, Android games, mobile app development",
}
KEYWORDS_APP = {
    "tr": "MotionArea, hareket oyunu, hareketle oynanan oyun, kameralı oyun, Android kameralı oyun, telefon kamerasıyla oyun, "
          "vücut hareketiyle oynanan oyun, kumandasız oyun, Kinect benzeri oyun, Kinect alternatifi, Just Dance benzeri, "
          "telefonla TV'de oyun, ekran yansıtma oyunu, aile oyunu, ailece oynanan oyun, çocuklar için hareket oyunu, "
          "evde hareket oyunu, egzersiz oyunu, exergame, parti oyunu, çok oyunculu yerel oyun, 4 kişilik oyun, "
          "Jungle Run, Altın Yağmuru, Kırmızı Işık Yeşil Işık, Duvar Koşusu, duvardan geçme oyunu, Kartopu Kuleleri, "
          "kartopu savaşı oyunu, Yer Piyanosu, ayakla piyano oyunu",
    "en": "MotionArea, motion game, motion games for Android, camera game, phone camera game, full-body game, "
          "body tracking game, controller-free game, Kinect-like game, Kinect alternative, Just Dance alternative, "
          "play phone games on TV, screen mirroring game, family game, family party game, kids motion game, "
          "active game at home, exergame, fitness game, local multiplayer, 4 player game, Jungle Run, Gold Rain, "
          "Red Light Green Light game, Wall Rush, hole in the wall game, Snowball Towers, snowball fight game, "
          "Floor Piano, piano tiles with your feet",
}


def url(path):
    return SITE + path


def organization(lang, full=True):
    node = {
        "@type": "Organization", "@id": ORG_ID, "name": "KutCode Labs", "alternateName": "kutcodelabs",
        "url": SITE + "/",
        "logo": {"@type": "ImageObject", "url": SITE + "/img/logo.png", "width": 394, "height": 120},
    }
    if full:
        node.update({
            "image": SITE + "/img/og-kutcode.jpg",
            "email": "info@kutcodelabs.com",
            "description": {
                "tr": "KutCode Labs, telefon kamerası ve cihaz üzerinde çalışan yapay zekâyla, hareketle oynanan mobil oyunlar ve uygulamalar geliştiren bağımsız bir yazılım stüdyosudur.",
                "en": "KutCode Labs is an independent software studio making mobile games and apps people play by moving, using the phone's camera and on-device AI.",
            }[lang],
            "founder": {"@type": "Person", "name": "Hilal Ulusoy"},
            "contactPoint": {"@type": "ContactPoint", "contactType": "customer support", "email": "info@kutcodelabs.com",
                             "availableLanguage": ["Turkish", "English"]},
            "knowsAbout": ["mobile game development", "motion games", "computer vision", "body tracking",
                           "on-device machine learning", "family games", "Unity", "Android"],
        })
    return node


def app(lang, page_url, full=True):
    node = {
        "@type": ["VideoGame", "MobileApplication"], "@id": APP_ID, "name": "MotionArea",
        "url": page_url, "operatingSystem": "Android", "applicationCategory": "GameApplication",
        "publisher": {"@id": ORG_ID},
    }
    if not full:
        return node
    node.update({
        "alternateName": "MotionArea: Motion Games",
        "description": {
            "tr": "MotionArea, telefonun kamerasıyla bütün vücudu takip eden, ailece oynanan hareket oyunlarıdır. Kumanda ya da sensör gerekmez; 1–4 oyuncu koşar, zıplar, eğilir ve ekrandaki hayvanları her hareketi anında taklit eder. Görüntü TV'ye yansıtılabilir; kamera görüntüsü yalnızca telefonda işlenir.",
            "en": "MotionArea is a set of motion games for the whole family that follow players' whole bodies through the phone's camera. No controllers or sensors: one to four players run, jump and lean, and their animals on screen copy every move. It can be shown on a TV, and the camera picture is processed only on the phone.",
        }[lang],
        "image": SITE + "/img/og-image.jpg",
        "screenshot": [SITE + "/img/hero-%s.webp" % g[0] for g in GAMES],
        "applicationSubCategory": {"tr": "Hareket ve parti oyunu", "en": "Motion and party game"}[lang],
        "genre": {"tr": ["Parti", "Aile", "Hareket", "Spor", "Müzik"], "en": ["Party", "Family", "Motion", "Sports", "Music"]}[lang],
        "gamePlatform": ["Android"],
        "playMode": ["SinglePlayer", "MultiPlayer"],
        "numberOfPlayers": {"@type": "QuantitativeValue", "minValue": 1, "maxValue": 4},
        "inLanguage": "en",
        "audience": {"@type": "PeopleAudience", "audienceType": {"tr": "Aileler ve çocuklar", "en": "Families and children"}[lang]},
        "isAccessibleForFree": True,
        "keywords": KEYWORDS_APP[lang],
        "featureList": {
            "tr": ["Telefon kamerasıyla, cihaz üzerinde vücut takibi", "Aynı anda 1–4 oyuncu", "TV'ye ekran yansıtma ya da USB-C–HDMI",
                   "Altı hareket oyunu", "Hareketleri taklit eden dört hayvan karakter", "Elini kaldırıp fare gibi kullanma",
                   "Kamera görüntüsü kaydedilmez ve gönderilmez"],
            "en": ["On-device body tracking with the phone camera", "One to four players at once", "Screen mirroring or USB-C to HDMI for the TV",
                   "Six motion games", "Four animal characters that copy your moves", "Raise a hand to point like a mouse",
                   "The camera picture is never recorded or sent"],
        }[lang],
        "hasPart": [{"@type": "VideoGame", "name": g[1] if lang == "tr" else g[2], "description": g[3] if lang == "tr" else g[4],
                     "image": SITE + "/img/hero-%s.webp" % g[0], "gamePlatform": "Android"} for g in GAMES],
        "author": {"@id": ORG_ID},
        "creator": {"@id": ORG_ID},
    })
    return node


def faq_from(page_html, lang):
    items = re.findall(r'<details><summary><span lang="tr">(.*?)</span><span lang="en">(.*?)</span></summary>'
                       r'<p><span lang="tr">(.*?)</span><span lang="en">(.*?)</span></p></details>', page_html)
    pick = (lambda q: (q[0], q[2])) if lang == "tr" else (lambda q: (q[1], q[3]))
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": html.unescape(q), "acceptedAnswer": {"@type": "Answer", "text": html.unescape(a)}}
        for q, a in map(pick, items)]}


def crumbs(lang, trail):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": name, "item": link} for i, (name, link) in enumerate(trail)]}


PAGES = [
    {
        "src": "index.html", "path": {"tr": "/", "en": "/en/"},
        "title": {"tr": "KutCode Labs — Hareketle oynanan mobil oyunlar ve uygulamalar",
                  "en": "KutCode Labs — Mobile games and apps you play by moving"},
        "desc": {"tr": "Telefon kamerasıyla vücut hareketini algılayan mobil oyunlar geliştiren bağımsız stüdyo. İlk oyunumuz MotionArea: kumandasız, ailece 1–4 kişilik hareket oyunları.",
                 "en": "Independent studio making mobile games that read your body through the phone's camera. Our first, MotionArea: controller-free motion games for 1–4 players."},
        "keywords": KEYWORDS_STUDIO,
        "image": ("/img/og-kutcode.jpg?v=2", 1200, 630),
        "image_alt": {"tr": "KutCode Labs logosu ve MotionArea'nın hayvan karakterleri", "en": "The KutCode Labs logo and MotionArea's animal characters"},
        "graph": lambda lang, p, page: [
            organization(lang),
            {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "KutCode Labs",
             "inLanguage": ["tr", "en"], "publisher": {"@id": ORG_ID}},
            {"@type": "WebPage", "@id": url(p) + "#webpage", "url": url(p), "name": PAGES[0]["title"][lang],
             "description": PAGES[0]["desc"][lang], "inLanguage": lang, "isPartOf": {"@id": SITE + "/#website"},
             "about": {"@id": ORG_ID}, "primaryImageOfPage": {"@type": "ImageObject", "url": SITE + "/img/og-kutcode.jpg"},
             "dateModified": TODAY},
            app(lang, url({"tr": "/motionarea/", "en": "/en/motionarea/"}[lang]), full=False),
        ],
    },
    {
        "src": "motionarea/index.html", "path": {"tr": "/motionarea/", "en": "/en/motionarea/"},
        "title": {"tr": "MotionArea — Telefon kamerasıyla oynanan hareket oyunları",
                  "en": "MotionArea — Motion games you play with your phone's camera"},
        "desc": {"tr": "Kumanda yok, kablo yok: telefonun kamerası bütün vücudunu takip eder. Koş, zıpla, eğil; altı hareket oyunu, ailece 1–4 oyuncu, TV'ye yansıt. Android'de yakında.",
                 "en": "No controllers, no cables: the phone's camera follows your whole body. Run, jump, lean — six motion games for 1–4 players, on your TV. Coming soon to Android."},
        "keywords": KEYWORDS_APP,
        "image": ("/img/og-image.jpg", 1024, 500),
        "image_alt": {"tr": "MotionArea: telefonun konsol, bedenin kumanda", "en": "MotionArea: your phone is the console, your body is the controller"},
        "preload": "/img/hero-jungle-run.webp",
        "graph": lambda lang, p, page: [
            organization(lang, full=False),
            {"@type": "WebPage", "@id": url(p) + "#webpage", "url": url(p), "name": PAGES[1]["title"][lang],
             "description": PAGES[1]["desc"][lang], "inLanguage": lang, "isPartOf": {"@id": SITE + "/#website"},
             "about": {"@id": APP_ID}, "mainEntity": {"@id": APP_ID}, "dateModified": TODAY,
             "breadcrumb": {"@id": url(p) + "#breadcrumb"}},
            dict(crumbs(lang, [("KutCode Labs", url({"tr": "/", "en": "/en/"}[lang])), ("MotionArea", url(p))]), **{"@id": url(p) + "#breadcrumb"}),
            app(lang, url(p)),
            dict(faq_from(page, lang), **{"@id": url(p) + "#faq"}),
        ],
    },
    {
        "src": "motionarea/privacy/index.html", "path": {"tr": "/motionarea/privacy/"}, "single": True,
        "title": {"tr": "MotionArea Gizlilik Politikası — KutCode Labs", "en": "MotionArea Privacy Policy — KutCode Labs"},
        "desc": {"tr": "MotionArea gizlilik politikası: kamera görüntüsü yalnızca telefonda işlenir, kaydedilmez ve gönderilmez. Reklamlar Google AdMob ile kişiselleştirilmeden gösterilir."},
        "keywords": {"tr": "MotionArea gizlilik politikası, MotionArea privacy policy, KutCode Labs gizlilik, kamera verisi, Google AdMob, çocuk gizliliği"},
        "image": ("/img/og-image.jpg", 1024, 500),
        "image_alt": {"tr": "MotionArea"},
        "graph": lambda lang, p, page: [
            organization(lang, full=False),
            {"@type": "WebPage", "@id": url(p) + "#webpage", "url": url(p), "name": PAGES[2]["title"]["tr"],
             "description": PAGES[2]["desc"]["tr"], "inLanguage": ["tr", "en"], "isPartOf": {"@id": SITE + "/#website"},
             "about": {"@id": APP_ID}, "publisher": {"@id": ORG_ID}, "dateModified": TODAY},
            crumbs(lang, [("KutCode Labs", SITE + "/"), ("MotionArea", SITE + "/motionarea/"), ("Gizlilik Politikası", url(p))]),
        ],
    },
]


def block(page, lang, html_src):
    p = page["path"][lang]
    title, desc = page["title"][lang], page["desc"][lang]
    image, w, h = page["image"]
    alt = page["image_alt"][lang]
    a = lambda s: s.replace("&", "&amp;").replace("\"", "&quot;").replace("<", "&lt;")
    out = [
        "<title>%s</title>" % a(title),
        '<meta name="description" content="%s">' % a(desc),
        '<meta name="keywords" content="%s">' % a(page["keywords"][lang]),
        '<meta name="author" content="KutCode Labs">',
        '<meta name="publisher" content="KutCode Labs">',
        '<meta name="robots" content="index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1">',
        '<link rel="canonical" href="%s">' % url(p),
    ]
    if not page.get("single"):
        out += ['<link rel="alternate" hreflang="%s" href="%s">' % (l, url(page["path"][l])) for l in ("tr", "en")]
        out.append('<link rel="alternate" hreflang="x-default" href="%s">' % url(page["path"]["tr"]))
    out += [
        '<meta property="og:type" content="website">',
        '<meta property="og:site_name" content="KutCode Labs">',
        '<meta property="og:title" content="%s">' % a(title),
        '<meta property="og:description" content="%s">' % a(desc),
        '<meta property="og:url" content="%s">' % url(p),
        '<meta property="og:image" content="%s">' % (SITE + image),
        '<meta property="og:image:width" content="%d">' % w,
        '<meta property="og:image:height" content="%d">' % h,
        '<meta property="og:image:alt" content="%s">' % a(alt),
        '<meta property="og:locale" content="%s">' % LOCALE[lang],
        '<meta property="og:locale:alternate" content="%s">' % LOCALE["en" if lang == "tr" else "tr"],
        '<meta name="twitter:card" content="summary_large_image">',
        '<meta name="twitter:title" content="%s">' % a(title),
        '<meta name="twitter:description" content="%s">' % a(desc),
        '<meta name="twitter:image" content="%s">' % (SITE + image),
        '<meta name="twitter:image:alt" content="%s">' % a(alt),
        '<meta name="theme-color" content="#f5f4ef">',
        '<meta name="application-name" content="KutCode Labs">',
        '<meta name="apple-mobile-web-app-title" content="KutCode Labs">',
        '<link rel="manifest" href="/site.webmanifest">',
    ]
    if page.get("preload"):
        out.append('<link rel="preload" as="image" href="%s" fetchpriority="high">' % page["preload"])
    graph = {"@context": "https://schema.org", "@graph": page["graph"](lang, p, html_src)}
    out.append('<script type="application/ld+json">\n%s\n</script>' % json.dumps(graph, ensure_ascii=False, indent=1))
    return "<!-- seo:start -->\n" + "\n".join(out) + "\n<!-- seo:end -->"


def fill(src, page, lang):
    s = re.sub(r"<!-- seo:start -->.*?<!-- seo:end -->", lambda m: block(page, lang, src), src, flags=re.S)
    if page.get("single"):
        return s
    tag = '<html lang="%s" data-lang="%s" data-fixed-lang="%s">' % (lang, lang, lang)
    return re.sub(r"<html[^>]*>", tag, s, count=1)


def to_english_links(s):
    # Links to the pages that have an English copy point at the copy; the privacy policy and files stay put.
    return re.sub(r'href="/(#[\w-]+|motionarea/(?:#[\w-]+)?|)"', lambda m: 'href="/en/%s"' % m.group(1), s)


def main():
    for page in PAGES:
        path = os.path.join(ROOT, page["src"])
        src = io.open(path, encoding="utf-8").read()
        assert "<!-- seo:start -->" in src, page["src"] + " has no seo block"
        io.open(path, "w", encoding="utf-8", newline="\n").write(fill(src, page, "tr"))
        if not page.get("single"):
            en_path = os.path.join(ROOT, "en", page["src"])
            os.makedirs(os.path.dirname(en_path), exist_ok=True)
            en = to_english_links(fill(src, page, "en"))
            note = "<!-- Made by tools/seo.py from %s: edit that page, not this one. -->\n" % page["src"]
            io.open(en_path, "w", encoding="utf-8", newline="\n").write(en.replace("<!doctype html>\n", "<!doctype html>\n" + note, 1))
        print("ok", page["src"])

    # Sitemap: every address, its other language, and its pictures.
    images = {"/": ["/img/og-kutcode.jpg"], "/motionarea/": ["/img/og-image.jpg"] + ["/img/hero-%s.webp" % g[0] for g in GAMES]}
    rows = ['<?xml version="1.0" encoding="UTF-8"?>',
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml" '
            'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">']
    for page in PAGES:
        for lang, p in page["path"].items():
            rows.append("  <url>")
            rows.append("    <loc>%s</loc>" % url(p))
            rows.append("    <lastmod>%s</lastmod>" % TODAY)
            if not page.get("single"):
                for l in ("tr", "en"):
                    rows.append('    <xhtml:link rel="alternate" hreflang="%s" href="%s"/>' % (l, url(page["path"][l])))
                rows.append('    <xhtml:link rel="alternate" hreflang="x-default" href="%s"/>' % url(page["path"]["tr"]))
            for img in images.get(page["path"]["tr"], []):
                rows.append("    <image:image><image:loc>%s</image:loc></image:image>" % (SITE + img))
            rows.append("  </url>")
    rows.append("</urlset>")
    io.open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8", newline="\n").write("\n".join(rows) + "\n")
    print("ok sitemap.xml")


if __name__ == "__main__":
    main()
