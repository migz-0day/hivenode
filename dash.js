"use strict";
const head = document.getElementById('head');
const board = document.getElementById('board');
async function load() {
    try {
        const res = await fetch(`../logs/attacks.json?t=${Date.now()}`);
        const text = await res.text();
        const lines = text.trim().split('\n').filter(i => i).reverse();
        head.innerText = `total attacks logged:${lines.length} | Auto-refresh:2s | Listening:0.0.0.0:2222`;
        let dash = '';
        lines.slice(0, 50).forEach((line) => {
            try {
                const jdata = JSON.parse(line);
                dash += `
                <div class="log-entry">
                 <span class="ip>[${jdata.timestamp}]${jdata.ip}</span>
                 <span class="loc">location-(${jdata.location})</span>
                 <span class="cred">username-${jdata.username}: password-${jdata.password}</span>
                </div>
                `;
            }
            catch { }
        });
        board.innerHTML = dash || `No attack`;
    }
    catch (err) {
        board.innerHTML = 'logs/attack.json not found';
    }
}
load();
setInterval(load, 2000);
