import os, sys, json, re, datetime
from pathlib import Path
from subprocess import check_output

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

CARD_TMPL = """\
<article class="card rounded-3xl bg-white border border-slate-200 shadow p-6">
  <div class="flex items-start justify-between gap-4">
    <div>
      <h3 class="text-2xl font-extrabold">{title}</h3>
      <p class="text-sm text-slate-500 mt-1">مصدر: موريتانيا الآن — تكرار العنوان: {count}×</p>
    </div>
    <div class="flex items-center gap-2">
      <a class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm bg-slate-100 text-slate-700 hover:bg-slate-200" href="{url}" target="_blank" rel="noopener">الرابط الأصلي</a>
    </div>
  </div>
  <p class="mt-4 leading-8">
    تعليق مهذّب: العنوان يتردّد كأنه لازمة أسبوعية… لعلّ الحلّ ليس في تكرار الأخبار، بل في تكرار الحلول 🙃
  </p>
</article>"""

def run(cmd):
    return check_output(cmd, shell=True, text=True)

def render_cards():
    data = run(f"{sys.executable} scripts/scrape_rimnow.py")
    items = json.loads(data)["items"]
    cards = [CARD_TMPL.format(title=i["title"], url=i["url"], count=i["count"]) for i in items]
    now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    header = f'<div class="text-sm text-slate-500 mb-3">آخر تحديث تلقائي: {now}</div>'
    return header + "\n" + "\n".join(cards)

def replace_between(text, start_mark, end_mark, new_html):
    pattern = re.compile(r"(?s)(" + re.escape(start_mark) + r")(.*?)(" + re.escape(end_mark) + r")")
    if not pattern.search(text):
        raise SystemExit("لم أجد العلامتين START/END داخل index.html")
    return pattern.sub(r"\1\n" + new_html + r"\n\3", text)

if __name__ == "__main__":
    html = INDEX.read_text(encoding="utf-8")
    out = replace_between(html, "<!-- START AUTO -->", "<!-- END AUTO -->", render_cards())
    if out != html:
        INDEX.write_text(out, encoding="utf-8")
        print("index.html updated")
    else:
        print("no changes")
