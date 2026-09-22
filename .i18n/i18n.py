# -*- coding: utf-8 -*-
"""Translation tooling for index.html. Not shipped.

A guide's markup is written in one language — `data-lang` on the `<article>` — and every
translatable element carries the *other* language in a `data-en` or `data-ja` attribute. So
Okinawa is Japanese markup + `data-en`, and New Zealand is English markup + `data-ja`.

    python3 .i18n/i18n.py slots  <guide>            # what would be translated, and from where
    python3 .i18n/i18n.py check  <guide>            # every slot translated? any stale leftovers?
    python3 .i18n/i18n.py extract <guide>           # -> .i18n/strings-<guide>.json
    python3 .i18n/i18n.py inject  <guide>           # .i18n/ja-<guide>.json -> index.html

`strings-<guide>.json` is a list of {slot, src, id}; `ja-<guide>.json` a list of {id, ja} by the
same id. The id is sha1(slot|src)[:10], so changing one word of the source orphans its
translation instead of silently keeping a stale one.

The generated map SVG is skipped: `.map/nz.py` and `.map/build.py` own their pin labels, in both
languages. `inject` only ever adds or replaces one attribute on an opening tag, so it cannot
disturb the wrapper spans in `h2.section`, `a.outlink`, `.glabel` or the edit button, all of which
are load-bearing.
"""
import hashlib
import json
import re
import sys

HTML = 'index.html'
VOID = {'br', 'hr', 'img', 'input', 'meta', 'link', 'use', 'circle', 'rect', 'path', 'source'}

# Elements holding translatable text, as (tag, required classes, required parent). A match is a
# whole unit: `span.txt` keeps its nested `<small>`, because one attribute must reproduce both.
# The packing list is the exception — `seedFromDOM()` reads an item's text and its note as two
# fields, so there `span.ctxt` stops at the `<small>` and the `<small>` is a slot of its own.
SLOTS = [
    ('h1', (), None), ('p', ('sub',), None), ('span', ('eyebrow',), None),
    ('div', ('t',), None), ('div', ('sub2',), None), ('div', ('m',), None), ('div', ('wd',), None),
    ('span', ('txt',), None), ('li', (), 'ul.bul'), ('p', ('desc',), None),
    ('div', ('subhead',), None), ('div', ('k',), None), ('div', ('v',), None),
    ('span', ('chip',), None), ('div', ('footer',), None), ('p', ('intro',), None),
    ('span', ('ctxt',), None), ('small', (), 'span.ctxt'),
    ('span', ('gname',), None), ('span', ('lb',), None),
    ('p', ('empty-note',), None), ('title', (), 'svg.map'),
    # The bare wrapper spans: a label inside a button, a section heading or an outbound link.
    ('span', (), 'button'), ('span', (), 'h2.section'), ('span', (), 'a.outlink'),
    ('span', (), 'div.glabel'), ('span', (), 'summary.head'),
    ('button', (), 'div.filters'), ('button', (), 'div.toolbar'),
]
SPLIT_NOTE = {'ctxt'}     # slots whose src stops before a nested <small>, which is its own slot


def parse(html, start, end):
    """Walk the tags in html[start:end], yielding every element as
    (tag, classes, content_start, content_end, open_tag_start, open_tag_end, ancestors)."""
    stack = []
    for m in re.finditer(r'<(/?)([a-zA-Z][\w-]*)((?:"[^"]*"|[^>"])*?)(/?)>', html[start:end]):
        closing, tag, attrs, selfclose = m.group(1), m.group(2).lower(), m.group(3), m.group(4)
        if closing:
            for i in range(len(stack) - 1, -1, -1):
                if stack[i][0] == tag:
                    t, cls, cs, os_, oe = stack.pop(i)
                    del stack[i:]
                    yield t, cls, cs, start + m.start(), os_, oe, tuple(
                        (s[0], s[1]) for s in stack)
                    break
            continue
        if selfclose or tag in VOID:
            continue
        cl = re.search(r'\bclass="([^"]*)"', attrs)
        stack.append((tag, tuple((cl.group(1) if cl else '').split()),
                      start + m.end(), start + m.start(), start + m.end()))


def guide_range(html, guide):
    a = html.index('<article class="guide t-%s"' % guide)
    return a, html.index('</article>', a)


def matches(tag, cls, ancestors):
    for stag, scls, parent in SLOTS:
        if tag != stag:
            continue
        # A slot listing no class means the bare element: `<li>` in a bullet list, the wrapper
        # `<span>` in a button. Without this, a stop row's `.time` would look like a wrapper span.
        if scls:
            if not set(scls) <= set(cls):
                continue
        elif cls:
            continue
        if parent:
            if not ancestors:
                continue
            ptag, pcls = parent.split('.') if '.' in parent else (parent, None)
            atag, acls = ancestors[-1]
            if atag != ptag or (pcls and pcls not in acls):
                continue
        return '-'.join(scls) or stag
    return None


def slots(html, guide):
    """Every translatable element in the guide, outermost first, skipping the generated map SVG
    and anything nested inside another slot (one attribute already carries the lot)."""
    lo, hi = guide_range(html, guide)
    svg = re.search(r'<svg class="map".*?</svg>', html[lo:hi], re.S)
    skip = (lo + svg.start(), lo + svg.end()) if svg else None
    found = []
    for tag, cls, cs, ce, os_, oe, anc in parse(html, lo, hi):
        if skip and skip[0] <= os_ < skip[1] and tag != 'title':
            continue
        slot = matches(tag, cls, anc)
        if slot:
            if slot in SPLIT_NOTE:
                note = html.find('<small', cs, ce)
                if note != -1:
                    ce = note
            found.append({'slot': slot, 'cs': cs, 'ce': ce, 'os': os_, 'oe': oe})
    found.sort(key=lambda s: (s['os'], -s['ce']))
    out, end = [], -1
    for s in found:
        s['src'] = html[s['cs']:s['ce']]
        s['txt'] = re.sub(r'<[^>]*>', '', s['src']).strip()
        if s['os'] < end:            # nested inside the slot we just took
            # A chip's swatch or a button's icon is markup, not text: when the outer slot adds no
            # text of its own, the inner span is the real slot, which is how the file is authored.
            if out and out[-1]['ce'] >= s['ce'] and out[-1]['txt'] == s['txt']:
                out[-1] = s
                end = s['ce']
            continue
        if s['txt']:                 # icon-only spans hold no text to translate
            out.append(s)
            end = s['ce']
    return out


def other(html, guide):
    """The attribute a guide's translations live in. There is no per-book language setting any
    more — an element's markup language is simply the one attribute it does *not* carry — so the
    direction is read back from whichever attribute the guide already uses. A guide with no
    translations yet is assumed to be English awaiting Japanese."""
    lo, hi = guide_range(html, guide)
    body = html[lo:hi]
    return 'en' if body.count('data-en="') > body.count('data-ja="') else 'ja'


def sid(slot, src):
    return hashlib.sha1(('%s|%s' % (slot, src)).encode()).hexdigest()[:10]


def main():
    cmd, guide = sys.argv[1], sys.argv[2]
    html = open(HTML).read()
    att = other(html, guide)
    found = slots(html, guide)

    if cmd == 'slots':
        for s in found:
            print('%-9s %s' % (s['slot'], s['src'][:96].replace('\n', ' ')))
        print('%d slots, translating into data-%s' % (len(found), att))

    elif cmd == 'check':
        have = [s for s in found if ('data-%s="' % att) in html[s['os']:s['oe']]]
        print('%d/%d slots carry data-%s' % (len(have), len(found), att))
        for s in found:
            if s not in have:
                print('  MISSING %-9s %s' % (s['slot'], s['src'][:80]))
        stray = len(re.findall(r'data-%s="' % att, html[guide_range(html, guide)[0]:
                                                        guide_range(html, guide)[1]])) - len(have)
        if stray:
            print('  %d data-%s attributes sit on elements that are not slots' % (stray, att))

    elif cmd == 'extract':
        rows = [{'slot': s['slot'], 'src': s['src'], 'id': sid(s['slot'], s['src'])}
                for s in found]
        path = '.i18n/strings-%s.json' % guide
        json.dump(rows, open(path, 'w'), ensure_ascii=False, indent=1)
        print('%d slots -> %s' % (len(rows), path))

    elif cmd == 'inject':
        tr = {r['id']: r[att] for r in json.load(open('.i18n/ja-%s.json' % guide))}
        done = missing = 0
        for s in reversed(found):                    # back to front, so offsets stay valid
            val = tr.get(sid(s['slot'], s['src']))
            if val is None:
                missing += 1
                continue
            # A translation carries nested markup — span.u above all — so its quotes have to be
            # escaped or they close the attribute. The dataset getter resolves them again, which
            # is why innerHTML comes back byte-identical.
            val = val.replace('"', '&quot;')
            tag = html[s['os']:s['oe']]
            stripped = re.sub(r' data-%s="[^"]*"' % att, '', tag)
            new = stripped[:-1].rstrip('/') + ' data-%s="%s"' % (att, val) + \
                stripped[-1 if not stripped.endswith('/>') else -2:]
            html = html[:s['os']] + new + html[s['oe']:]
            done += 1
        open(HTML, 'w').write(html)
        print('injected %d, no translation for %d' % (done, missing))

    else:
        sys.exit(__doc__)


if __name__ == '__main__':
    main()
