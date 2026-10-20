# Archived product photos (live until 2026-10-20)

These are the product photos the site showed until 2026-10-20. On that date
the owner replaced them with the client's new set,
`assets/ahlam/products images - new (2)`, used as supplied. They are kept
here in case they are needed again.

Nothing reads this folder. The build reads only `content/images/`, and
GitHub Pages deploys only `_site/`, so these files are never published.

## What is here

The tree mirrors `content/images/` as it was at commit `fa62e98`, the last
commit that used these files. The files are unchanged: they were moved with
`git mv`, not re-encoded. There are 94 files for the 48 products.
`ambience/flint-room.jpg` was not archived: it is a decorative photo, not a
product photo, and is still in use.

What the set has that the new one does not:

- **White-background cut-outs** (`main.jpg` and the colour files) for most
  products. The listings showed them whole on white.
- **Logo-free bed photos.** The bunk bed (`bunk-beds/iron-bunk-bed/main.jpg`),
  the single bed (`metal-beds/single-iron-bed/main.jpg`) and the heavy-mesh
  folding bed (`metal-beds/heavy-mesh-folding-bed/folded.jpg`, `unfolded.jpg`)
  have no CROWN logo. The new set shows it.
- **RT-M101 colour cut-outs** (`metal-beds/rt-m101/black|grey|cream|blue.jpg`)
  on white. The new set has room scenes.
- **The 50×70 hotel pillow** on white with its carry bag
  (`pillows/hotel-50x70/main.jpg`), which was the Pillows collection cover.
- **The nano 4×3 rug**, its room scene set on a white square
  (`rugs/nano-patterned-4x3/main.jpg`).

Most `second.jpg` files are the client's real-background shots. The new set
contains the same shots again, sometimes re-saved.

## Where the files came from

All the files are in `assets/ahlam/` (the client's folders, outside this
repository):

- `products images`: the first delivery. RT-M101, tables and the Chinese
  camp bag are from here.
- `products images - new`: the revised delivery imported on 2026-10-08
  (commit 470bb82). It has a main image and `secondary images/<same name>`
  per product.
- the client's "New folder/صور الاصناف - خلفية بيضاء 4000px - النسخة
  النهائية/مخدات": the two hotel pillows (commits 7c56f00, 93d08ea)
- `دورين 2.png`: the logo-free bunk bed (commit 5847122)

The site's copies were saved as JPEG, longest side 2000 px.

## Files per product

| Product slug | Files |
|---|---|
| rt-m101-folding-bed | `metal-beds/rt-m101/` black, grey, cream, blue (cut-outs, one per colour) |
| single-iron-bed | `metal-beds/single-iron-bed/main.jpg` (logo-free) |
| heavy-mesh-folding-bed | `metal-beds/heavy-mesh-folding-bed/` folded, unfolded (logo-free) |
| iron-bunk-bed | `bunk-beds/iron-bunk-bed/main.jpg` (logo-free) |
| comforter-* (12) | `comforters/<name>/` main (cut-out), second (room or spec photo) |
| blanket-bifi | `blankets/bifi/` main (blanket on a sofa), second (poster) |
| pillow-classic, pillow-hotel, pillow-memory-foam-* | `pillows/<name>/main.jpg` |
| pillow-hotel-50x70 | `pillows/hotel-50x70/` main (pillow and bag on white), second (specs) |
| rug-* (12) | `rugs/<name>/` main (cut-out), second (floor or room photo) |
| prayer-rug-* (3) | `prayer-rugs/<name>/` main (cut-out), second (floor photo) |
| chair-* (7) | `chairs/<name>/` main (cut-out), second (floor photo) |
| round- / square-plastic-table | `plastic-tables/<shape>-table/` beige, white |
| camp-bag-chinese | `camp-bags/chinese/` main, open, dimensions, detail |
| camp-bag-tanzanian | `camp-bags/tanzanian/` main, open |

## How to restore

1. Copy the files you need back to the same path under `content/images/`.
2. Restore the matching `images:` entries in `content/catalog.yml` from the
   version that used them:

   ```bash
   git show fa62e98:content/catalog.yml
   ```

   That version also sets `home.hero_image: rugs/nano-patterned-4x3/second.jpg`
   (the home hero) and the collection `cover:` paths.
3. Run `python build.py`. It must end with "checks passed".
