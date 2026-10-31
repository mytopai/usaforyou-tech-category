# USA / FOR YOU — техника

Demo repository produced with the `github-static-commerce-release` workflow.

## Intent

Фокусная категория для проверки спроса на технику и аксессуары.

The catalog is illustrative: facts marked for verification remain `hold`/`preorder`; no prices, stock, warranty, authenticity or delivery promises are invented. The CTA leads to a manual request, not card collection.

## GitHub Pages

Enable manually: **Settings → Pages → Deploy from a branch → main → /(root)**.

## Validation

```bash
python3 /home/ubuntu/skills/github-static-commerce-release/scripts/audit_static_site.py .
node --check app.js
python3 -m json.tool data/products.json >/dev/null
```
