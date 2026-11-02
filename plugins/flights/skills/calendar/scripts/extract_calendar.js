// Evaluate in the Google Flights tab AFTER the date calendar is open and prices have loaded.
// Usage from browser-use:  js(open('.../extract_calendar.js').read().replace('__FROM__','2026-12-07').replace('__TO__','2027-01-03'))
// Returns {meta, rows:[{date,price,aria}], loaded, total}. price is null (never 0) when Google shows no fare.
(() => {
  const FROM = '__FROM__', TO = '__TO__';
  const inp = l => [...document.querySelectorAll('input')].find(i => (i.getAttribute('aria-label')||'').startsWith(l));
  const chip = t => [...document.querySelectorAll('button')].map(b => (b.getAttribute('aria-label')||b.innerText).trim().replace(/\n/g,' ')).find(x => x.startsWith(t)) || null;
  const rows = [];
  document.querySelectorAll('[role=gridcell][data-iso]').forEach(c => {
    const d = c.dataset.iso; if (d < FROM || d > TO) return;
    const lab = [...c.querySelectorAll('[aria-label]')].map(x => x.getAttribute('aria-label')).join(' ## ');
    const m = lab.match(/([\d,]+) US dollars/) || (c.innerText.split('\n')[1]||'').match(/\$([\d,]+)/);
    rows.push({date: d, price: m ? +m[1].replace(/,/g,'') : null});
  });
  const pax = document.querySelector('[aria-label*="passenger" i]');
  return {
    meta: {
      origin: (inp('Where from')||{}).getAttribute?.('aria-label') || null,
      destination: (inp('Where to')||{}).getAttribute?.('aria-label') || null,
      selected_departure: (inp('Departure')||{}).value || null,
      stops_chip: chip('Nonstop') || chip('1 stop') || chip('2 stops') || chip('Stops'),
      times_chip: chip('Times'),
      passengers_label: pax ? pax.getAttribute('aria-label') : null,
      url: location.href, observed_at: new Date().toISOString()
    },
    total: rows.length, loaded: rows.filter(r => r.price !== null).length, rows
  };
})()
