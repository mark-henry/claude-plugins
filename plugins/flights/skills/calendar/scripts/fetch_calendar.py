"""browser-use recipe: open a fare calendar in a NEW tab and return rows. Run inside mcp browser_exec
(helpers new_tab/switch_tab/js/cdp are pre-imported there). Not a standalone script.

    SK = '<this scripts dir>/'
    exec(open(SK + 'fetch_calendar.py').read())
    res = fetch_calendar(url, '2026-12-07', '2027-01-03')
"""
import time, json
def fetch_calendar(url, frm, to, max_next=3, close=True):
    tid = new_tab(url); switch_tab(tid); time.sleep(6)
    js("[...document.querySelectorAll('input')].find(x=>x.getAttribute('aria-label')=='Departure').click()")
    time.sleep(3)
    src = open(SK+'extract_calendar.js').read().replace('__FROM__',frm).replace('__TO__',to)
    cdp("Emulation.setFocusEmulationEnabled", enabled=True)   # background tabs never load prices otherwise
    try:
        for i in range(max_next+1):
            switch_tab(tid)
            for _ in range(5):
                time.sleep(2); r = js(src)
                if r['total'] and r['loaded'] >= 1: break
            if r['total'] and r['loaded'] == r['total']: break
            if i < max_next: js("document.querySelector('[role=dialog] [jsname=KpyLEe]').click()")  # Next month(s)
    finally:
        cdp("Emulation.setFocusEmulationEnabled", enabled=False)
    if close: cdp("Target.closeTarget", targetId=tid)
    return r
