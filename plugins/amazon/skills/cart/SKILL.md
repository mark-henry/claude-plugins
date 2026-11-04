---
name: cart
description: "Read the user's Amazon carts (Amazon Cart with its same-day windowed items, Amazon Fresh Cart, Whole Foods Market Cart, Saved for Later) and get items added by opening product pages in the user's real Chrome. Use for \"what's in my Amazon cart\", \"add X to my cart\", \"how much more for free delivery\", or juggling grocery vs regular items."
---

# Amazon carts

Two verbs, both via `amazon-cart` (on PATH from this plugin):

- `amazon-cart read` prints JSON for all three carts. It runs in a dedicated **agent Chrome** (own profile `~/.chrome-agent`, CDP on port 9333, started in the background by `agent-chrome`), so there is no "Allow remote debugging?" prompt and no focus steal. It opens one tab, reads every cart by same-origin `fetch` (the cart pages are server-rendered), and closes the tab.
- `amazon-cart open ASIN...` opens product pages in the user's **real** Chrome for the user to click Add to Cart. Afterwards, run `read` and confirm each ASIN is in `list: "active"`.

## Adding: the user clicks, you never do

Every automated add route failed or was flagged (measured 2026-11-04):

- Clicking `#add-to-cart-button` by JS `.click()`, by CDP mouse event with focus emulation, or by `form.requestSubmit()` silently added nothing. After about two product-page loads plus add attempts, Amazon put the **account** behind `/checkpoint/continue` ("I am human" checkbox), and the checkpoint carried over to a fresh browser profile.
- The legacy add link `/gp/aws/cart/add.html?ASIN.1=…&Quantity.1=…` redirects to the cart and adds nothing, **even when the user opens it by hand**. It shows no error and no confirmation page, so the only evidence is the item's absence. The "Added to Cart / Failed. Try again!" strings in the cart page source are hidden templates, not results.
- A manual click by the user works.

So: find the ASINs, run `amazon-cart open`, tell the user which tabs to click, then verify with `read`. Never click the checkpoint box, and never try to get past it. If `read` reports `checkpoint: true`, stop and ask the user to clear it.

Be polite: no rapid product-page loads in the agent Chrome. Reads pause 3 s between carts.

## The carts: names and how to tell them apart

| Name (Amazon's) | Path | Notes |
|---|---|---|
| **Amazon Cart** | `/gp/cart/view.html` | The normal cart. Header "Your Amazon Cart", total "Amazon Subtotal". Also holds **Saved for Later** (`list: "saved"`). |
| **Amazon Fresh Cart** | `/cart/localmarket?almBrandId=QW1hem9uIEZyZXNo` | A separate cart with its own checkout. Page title "Amazon Fresh Shopping Cart". |
| **Whole Foods Market Cart** | `/cart/localmarket?almBrandId=VUZHIFdob2xlIEZvb2Rz` | Also separate. Page title "Whole Foods Market Shopping Cart". |

The `almBrandId` values are base64 ("Amazon Fresh", "UFG Whole Foods").

**Windowed items inside the Amazon Cart.** Amazon's **Same-Day Perishable Grocery Delivery** (launched 2025) puts grocery items in the normal Amazon Cart with nothing to mark them, except that their delivery promise is a **time window**: "FREE delivery Tomorrow 1 PM - 4 PM on $25 of qualifying items". The window marks the delivery route, not the product type. On 2026-11-04 shelf-stable Horizon milk **and furniture floor pads** both carried windows. The reader sets `windowed: true` when the row's `data-unifieddeliverymessage` contains a time range. Windowed items share a basket minimum ($25 for Prime, or $2.99 under it). `free_delivery_nudge` gives the shortfall ("Add $1.04 for FREE Tomorrow delivery").

**"Amazon Grocery" is a store brand** (items under $5), not a cart. Don't call the Fresh cart that.

When reporting, group the Amazon Cart into windowed and regular shipping, then list the Fresh and Whole Foods carts separately. Say which checkout each item goes through.

## Output fields

Each cart has `name, page_title, status, checkpoint, signed_in, empty, subtotal, free_delivery_nudge, items[]`. Each item has `list (active|saved), asin, title, qty, price, out_of_stock, delivery, windowed`. A `price` of null means no current offer, not free.

The Fresh and Whole Foods item selectors are assumed to match the Amazon Cart (`.sc-list-item[data-asin]`) but were only seen empty. If one of those carts reports `empty: false` with zero items, the selector is wrong: re-measure.

## Traps (inherited from danielrosehill/Claude-Amazon-Plugin research, plus ours)

- Amazon's bot wall answers **HTTP 200**. Check the body and the URL (`/checkpoint/`), not the status.
- Navigating a signed-in session can land somewhere live, such as an order-cancel page. Prefer fetches, and if you land somewhere unexpected, click nothing.
- `textContent` of a fetched document includes scripts, so strip `script/style/noscript` first.
- If the agent Chrome has crashed, `agent-chrome` relaunches it. The sign-in persists in the profile. If `signed_in` is false, ask the user to sign in there (`agent-chrome --show`).
