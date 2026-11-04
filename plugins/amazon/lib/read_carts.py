# Runs inside browser-harness (helpers pre-imported), fed on stdin by `amazon-cart read`.
# Opens ONE tab in the agent Chrome, reads the three carts with same-origin fetches
# (server-rendered, so no clicking), prints JSON, and always closes its tab.
import json, time

CARTS = {
    "amazon":     ("Amazon Cart",              "/gp/cart/view.html"),
    "fresh":      ("Amazon Fresh Cart",        "/cart/localmarket?almBrandId=QW1hem9uIEZyZXNo"),
    "wholefoods": ("Whole Foods Market Cart",  "/cart/localmarket?almBrandId=VUZHIFdob2xlIEZvb2Rz"),
}

# One fetch per call: Runtime.evaluate times out after ~5 s, so the page stores the result
# in window.__cart and Python polls for it.
FETCH = r"""window.__cart=null;(async()=>{try{
const r=await fetch(%s,{credentials:'include'}); const h=await r.text();
const d=new DOMParser().parseFromString(h,'text/html');
const strip=s=>{const x=new DOMParser().parseFromString(s||'','text/html');const w=x.createTreeWalker(x.body,4),t=[];while(w.nextNode())t.push(w.currentNode.nodeValue);return t.join(' ').replace(/[\s\u202f]+/g,' ').trim()};
d.querySelectorAll('script,style,noscript').forEach(e=>e.remove());
const body=d.body?d.body.textContent.replace(/[\s ]+/g,' '):'';
const items=[...d.querySelectorAll('.sc-list-item[data-asin]')].map(e=>{const s=e.dataset;
  const delivery=strip(s.unifieddeliverymessage);
  return {list:s.itemtype==='saved'?'saved':'active', asin:s.asin, title:s.producttitle||null,
    qty:+s.quantity||0, price:s.price&&+s.price?+s.price:null, out_of_stock:s.outofstock==='1',
    delivery:delivery||null,
    windowed:/\d\s*(AM|PM)\s*-\s*\d{1,2}\s*(AM|PM)/i.test(delivery)}});
window.__cart={status:r.status, final_url:r.url.split('?')[0], page_title:d.title,
  checkpoint:/\/checkpoint\//.test(r.url)||/I am human|not a robot|captcha/i.test(body.slice(0,20000)),
  signed_in:!/Hello, sign in/.test(body), empty:/Cart is empty/i.test(body),
  subtotal:(body.match(/Subtotal \(\d+ items?\): ?\$[\d.,]+/)||[null])[0],
  free_delivery_nudge:(body.match(/Add \$[\d.,]+ for FREE [^.$]{0,40}delivery/)||[null])[0],
  items};
}catch(err){window.__cart={error:String(err)}}})();0"""

out = {"read_at": time.strftime("%Y-%m-%d %H:%M"), "carts": {}}
tid = new_tab("https://www.amazon.com/gp/cart/view.html")
try:
    time.sleep(5)
    for key, (name, path) in CARTS.items():
        switch_tab(tid)                      # re-pin: the daemon's tab pointer is shared
        js(FETCH % json.dumps(path))
        r = None
        for _ in range(20):
            time.sleep(1); r = js("window.__cart")
            if r: break
        r = r or {"error": "timed out"}
        r["name"] = name
        out["carts"][key] = r
        if r.get("checkpoint"):
            out["stopped"] = "Amazon checkpoint ('I am human'): ask the user to clear it; do not click it"
            break
        time.sleep(3)                        # be polite between carts
finally:
    cdp("Target.closeTarget", targetId=tid)
print(json.dumps(out, indent=1))
