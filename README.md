# Icebreaker

A party game for your phone with **6,179 questions** across 17 categories.

**Play:** https://icebreaker.mattbriney.com

## Ways to play

- **Host a live game:** the host gets a 4-letter code, and everyone joins on their own phone (or opens the invite link).
- **Play on one phone:** add players and pass the phone around.
- **Text a challenge:** answer a card, then send it by text. The other person answers before they can see your answer, and they can send one back. Earlier rounds of the back-and-forth stay attached to the link.

## A round

1. Every player picks a category.
2. Cards are dealt according to the host's rules:
   - **Mix everyone's picks:** the picks are shuffled and dealt around.
   - **Pick for the next player:** your pick becomes the next player's card.
   - **Pick your own:** you answer from the category you chose.
3. **Answers:**
   - **Say it out loud:** the player whose card it is answers.
   - **Challenge (type and reveal):** everyone types an answer, and all the answers are shown at once.
4. Each card can be swapped for a new one **twice**.

The 18+ categories (Dating & Romance, Couples Connect, Intimacy, Flirty) only show up when the host turns them on.

## No repeats

Each phone remembers which questions it has seen, so you won't get the same card twice. In a live game, the host's phone combines everyone's history and avoids any card that anyone in the room has already seen. When a category runs out, it starts over.

## Privacy

- Names, players, answers and settings exist only in memory and are gone when the tab closes.
- The only thing saved on the device is the question history (`ib-seen`). It holds question numbers only, never names or answers.
- **Live games** connect phones directly with WebRTC, which is encrypted end to end. A public PeerJS server only introduces the phones to each other; game data never passes through it. The host's phone runs the game, so the host needs to keep the screen on.
- **Challenge links** are encrypted on the phone with AES-GCM (256-bit). The encrypted data goes in the query string (`?ch=`). The key goes after the `#` (`#k=`), and browsers never send that part to any server. A link missing the `#k=` part can't be opened.

## Files

| File | What it is |
|---|---|
| `index.html` | The whole app |
| `questions.js` | Question bank (generated) |
| `tools/build_questions.py` | Generates `questions.js`. Edit questions here, then run `python3 tools/build_questions.py` |
| `peerjs.min.js` | PeerJS 1.5.5, included in the repo |
| `sw.js`, `manifest.webmanifest`, `icon*` | Offline support and "Add to Home Screen" |
| `CNAME` | Custom domain for GitHub Pages |

## Hosting

GitHub Pages serves the site from the `main` branch root, with the custom domain set by `CNAME`.
