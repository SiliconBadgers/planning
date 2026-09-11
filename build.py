"""Build a standalone HTML reader and complete Markdown export from local sources.

Uses only the Python standard library. Supports the Markdown forms used here:
headings, paragraphs, inline links/code/bold, flat lists, tables and fenced code.
No publishing, Git commands or network requests are performed.
"""
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib
import html
import json
import re
import sys
from urllib.parse import urlsplit
sys.dont_write_bytecode = True
import model_budget

ROOT = Path(__file__).resolve().parent
REPOS = ROOT / 'sources/team-charters'
SNAPSHOT = json.loads((ROOT / 'repository-snapshot.json').read_text())
MANIFEST = json.loads((ROOT / 'sources/team-manifest.json').read_text())['components']


def github_link(name, path=''):
    record = SNAPSHOT['repositories'][name]
    return record['url'] + ('/blob/' + record['commit'] + '/' + path if path else '')


def import_doc(name, filename, shift):
    source = (REPOS / name / filename).read_text()
    source = re.sub(r'^# [^\n]+\n', '', source, count=1).strip()
    source = re.sub(r'(?m)^(#{2,5}) ', lambda m: '#' * min(len(m[1]) + shift, 6) + ' ', source)
    def relink(match):
        label, target = match.groups()
        if '://' in target or target.startswith('#'):
            return match.group(0)
        return '[' + label + '](' + github_link(name, target) + ')'
    return re.sub(r'\[([^\]]+)\]\(([^)]+)\)', relink, source)


def assemble():
    template = (ROOT / 'plan-source.md').read_text()
    technical = (ROOT / 'technical-plan.md').read_text()
    for key, value in model_budget.build().items():
        technical = technical.replace('{{' + key + '}}', value)
    template = template.replace('{{TECHNICAL_PLAN}}', technical)
    rows = ['| Repository | Charter focus | Supplied code |', '|---|---|---|']
    charters = []
    snapshots = ['| Repository | Recorded revision | Visibility | Commits at check |', '|---|---|---|---|']
    source_hashes = {filename: hashlib.sha256((ROOT / filename).read_bytes()).hexdigest()
                     for filename in ['plan-source.md', 'technical-plan.md', 'model_budget.py', 'sources/team-manifest.json']}
    for name, record in MANIFEST.items():
        status = 'MAC example contributor' if record['status'] == 'working-starter' else 'Documentation and scaffold'
        rows.append(f'| [{name}](#team-{name}) | {record["owner_role"]} | {status} |')
        charter = import_doc(name, 'CHARTER.md', 2)
        objectives = import_doc(name, 'OBJECTIVES.md', 3)
        charters.append(f'''### Team: {name}

[Open repository]({github_link(name)}) | [Source charter]({github_link(name, 'CHARTER.md')}) | [Source objectives]({github_link(name, 'OBJECTIVES.md')})

{charter}

#### High-level objectives

{objectives}
''')
        repository = SNAPSHOT['repositories'][name]
        revision = repository['commit']
        visibility = 'Private' if repository['private'] else 'Public'
        snapshots.append(f'| {name} | [{revision[:10]}]({github_link(name)}/commit/{revision}) | {visibility} | {repository["commits"]} |')
        for filename in ['CHARTER.md', 'OBJECTIVES.md']:
            source_hashes[name + '/' + filename] = hashlib.sha256((REPOS / name / filename).read_bytes()).hexdigest()
    verified = datetime.fromisoformat(SNAPSHOT['verified_at']).astimezone(ZoneInfo('America/Chicago'))
    snapshots.insert(0, 'Repository snapshot checked ' + verified.strftime('%B %d, %Y at %I:%M %p %Z') + '.\n')
    doc = template.replace('{{REPOSITORY_TABLE}}', '\n'.join(rows)).replace('{{TEAM_CHARTERS}}', '\n'.join(charters)).replace('{{SNAPSHOT_TABLE}}', '\n'.join(snapshots))
    assert '{{' not in doc, 'Unexpanded source placeholder'
    assert '\u2014' not in doc, 'Em dashes are not used in this document'
    (ROOT / 'PLAN.md').write_text(doc)
    (ROOT / 'source-hashes.json').write_text(json.dumps(source_hashes, indent=2) + '\n')
    return doc, verified


def inline(value):
    pattern = r'(`[^`]+`|\[[^\]]+\]\([^)]*\)|\*\*[^*]+\*\*)'
    output = []
    for token in re.split(pattern, value):
        if not token:
            continue
        if token.startswith('`') and token.endswith('`'):
            output.append('<code>' + html.escape(token[1:-1]) + '</code>')
        elif token.startswith('**') and token.endswith('**'):
            output.append('<strong>' + html.escape(token[2:-2]) + '</strong>')
        elif token.startswith('[') and re.fullmatch(r'\[[^\]]+\]\([^)]*\)', token):
            match = re.fullmatch(r'\[([^\]]+)\]\(([^)]*)\)', token)
            label, target = match.groups()
            if urlsplit(target).scheme not in {'', 'https', 'http'}:
                raise ValueError('Unsupported link scheme')
            output.append('<a href="' + html.escape(target, quote=True) + '">' + html.escape(label) + '</a>')
        else:
            output.append(html.escape(token))
    return ''.join(output)


def render(doc):
    lines = doc.splitlines()
    out, toc, paragraph = [], [], []
    used_ids = set()
    current_section = False
    current_team = False
    list_tag = None
    index = 0

    def unique_id(title):
        slug = re.sub(r'[^a-z0-9 -]', '', title.lower()).strip().replace(' ', '-')
        slug = re.sub('-+', '-', slug)
        candidate = slug
        n = 2
        while candidate in used_ids:
            candidate = slug + '-' + str(n)
            n += 1
        used_ids.add(candidate)
        return candidate

    def flush():
        nonlocal list_tag
        if paragraph:
            out.append('<p>' + inline(' '.join(paragraph)) + '</p>')
            paragraph.clear()
        if list_tag:
            out.append('</' + list_tag + '>')
            list_tag = None

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            flush()
            index += 1
            continue
        if line.startswith('```'):
            flush()
            code = []
            index += 1
            while index < len(lines) and not lines[index].startswith('```'):
                code.append(lines[index])
                index += 1
            assert index < len(lines), 'Unclosed code fence'
            out.append('<pre><code>' + html.escape('\n'.join(code)) + '</code></pre>')
            index += 1
            continue
        heading = re.match(r'^(#{1,6}) (.+)$', line)
        if heading:
            flush()
            level, title = len(heading[1]), heading[2]
            if level == 1:
                index += 1
                continue
            if level == 2:
                if current_team:
                    out.append('</div></details>')
                    current_team = False
                if current_section:
                    out.append('</section>')
                anchor = unique_id(title)
                match = re.match(r'(\d+)\. (.*)', title)
                number, label = match.groups() if match else ('', title)
                toc.append((number, label, anchor))
                out.append('<section class="chapter" id="' + anchor + '"><header class="chapter-header"><span class="chapter-number">' + number + '</span><h2>' + html.escape(label) + '</h2></header>')
                current_section = True
                if 'Team charter library' in title:
                    out.append('<div class="library-tools js-only"><label for="charter-search">Find a team or topic</label><div class="search-row"><input id="charter-search" type="search" placeholder="Try memory, numerical behavior, or FPGA" autocomplete="off"><button type="button" id="clear-search">Clear</button></div><p id="search-count" class="search-count" role="status" aria-live="polite">11 team charters</p><div class="library-buttons"><button type="button" id="expand-charters">Expand all</button><button type="button" id="collapse-charters">Collapse all</button></div></div>')
            elif level == 3 and title.removeprefix('Team: ') in MANIFEST:
                if current_team:
                    out.append('</div></details>')
                name = title.removeprefix('Team: ')
                anchor = 'team-' + name
                assert anchor not in used_ids
                used_ids.add(anchor)
                out.append('<details class="team-charter" id="' + anchor + '"><summary><span class="team-name">' + html.escape(name) + '</span><span class="team-focus">' + html.escape(MANIFEST[name]['owner_role']) + '</span><span class="expand-mark" aria-hidden="true">+</span></summary><div class="charter-body">')
                current_team = True
            else:
                anchor = unique_id(title)
                out.append(f'<h{level} id="{anchor}">' + inline(title) + f'</h{level}>')
            index += 1
            continue
        if line.startswith('|') and index + 1 < len(lines) and re.fullmatch(r'[| :\-]+', lines[index + 1].strip()):
            flush()
            rows = [line.strip().strip('|').split('|')]
            index += 2
            while index < len(lines) and lines[index].startswith('|'):
                rows.append(lines[index].strip().strip('|').split('|'))
                index += 1
            out.append('<div class="table-scroll" tabindex="0" role="region" aria-label="Scrollable reference table"><table><thead><tr>')
            out.extend('<th scope="col">' + inline(cell.strip()) + '</th>' for cell in rows[0])
            out.append('</tr></thead><tbody>')
            for row in rows[1:]:
                assert len(row) == len(rows[0]), 'Uneven table row'
                out.append('<tr>' + ''.join('<td>' + inline(cell.strip()) + '</td>' for cell in row) + '</tr>')
            out.append('</tbody></table></div>')
            continue
        item = re.match(r'^(?:([-*]) |\d+\. )(.+)$', line)
        if item:
            if paragraph:
                out.append('<p>' + inline(' '.join(paragraph)) + '</p>')
                paragraph.clear()
            tag = 'ul' if item[1] else 'ol'
            if list_tag != tag:
                if list_tag:
                    out.append('</' + list_tag + '>')
                out.append('<' + tag + '>')
                list_tag = tag
            out.append('<li>' + inline(item[2]) + '</li>')
            index += 1
            continue
        if list_tag:
            out.append('</' + list_tag + '>')
            list_tag = None
        paragraph.append(line.strip())
        index += 1
    flush()
    if current_team:
        out.append('</div></details>')
    if current_section:
        out.append('</section>')
    return '\n'.join(out), toc


def main():
    doc, verified = assemble()
    content, toc = render(doc)
    nav = ''.join(f'<a href="#{anchor}"><span class="nav-number">{number}</span><span>{html.escape(label)}</span></a>' for number, label, anchor in toc)
    css = (ROOT / 'reader.css').read_text()
    js = (ROOT / 'reader.js').read_text()
    output = '''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light">
<meta name="description" content="SiliconBadgers Qwen3.5-2B accelerator plan: INT4 and FP4 tradeoffs, prefill, decode, hybrid attention, memory budgets and eleven team charters.">
<title>SiliconBadgers | Project master plan</title>
<style>''' + css + '''</style>
<noscript><style>.js-only{display:none!important}</style></noscript>
</head>
<body>
<a class="skip-link" href="#document">Skip to the plan</a>
<aside class="rail" aria-label="Document navigation">
<a class="brand" href="#top"><span class="brand-mark" aria-hidden="true">SB</span><span>SiliconBadgers<small>Project master plan</small></span></a>
<div class="edition"><span class="status-dot"></span> Technical draft 0.2</div>
<p class="rail-label">In this document</p>
<nav>''' + nav + '''</nav>
<div class="rail-footer">Shared engineering plan<br>Member-directed work</div>
</aside>
<div class="page">
<header class="topbar"><span>ENGINEERING / SHARED DIRECTION</span><div><a class="quiet-button" href="PLAN.md" download="SiliconBadgers-Plan.md">Markdown</a><button class="quiet-button js-only" id="print-plan" type="button">Print / PDF</button></div></header>
<main id="document">
<div class="cover" id="top"><p class="eyebrow">SILICONBADGERS / PLAN 02</p><h1>Qwen 3.5<br><span>to silicon.</span></h1><p class="cover-deck">A 2B model. Four-bit weights.<br>An engineering plan for eleven teams.</p><div class="cover-meta"><span>Qwen3.5-2B baseline</span><span>INT4 / FP4 studies</span><span>Shared technical draft</span></div><div class="next-decision"><span class="next-label">TARGET SET / TRADEOFFS OPEN</span><p>Prefill, decode and persistent state need different compute, memory and precision choices.</p><a href="#04-qwen-baseline-and-exact-scope">Read the technical baseline <span aria-hidden="true">↗</span></a></div></div>
<article>''' + content + '''</article>
<footer class="document-footer"><span>SiliconBadgers / Technical draft 0.2</span><span>Repository snapshot: ''' + verified.strftime('%d %b %Y') + '''</span></footer>
</main>
</div>
<script>''' + js + '''</script>
</body>
</html>
'''
    assert '\u2014' not in output
    (ROOT / 'index.html').write_text(output)
    print(f'Built PLAN.md and index.html: {len(MANIFEST)} full charters, {len(toc)} chapters, {len(doc.split()):,} words.')


if __name__ == '__main__':
    main()
