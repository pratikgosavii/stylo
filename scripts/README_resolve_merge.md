# Resolve __pycache__ merge conflicts on production

When `git pull --no-rebase origin master` fails with **modify/delete** conflicts on `__pycache__/*.pyc` files, run these on the **production server** (from the project root, e.g. `~/stylo`).

## Option 1: One-time commands (copy-paste on prod)

```bash
cd ~/stylo   # or your project path

# Accept remote’s deletion for all conflicted files
git diff --name-only --diff-filter=U | while read -r f; do [ -n "$f" ] && git rm -f "$f"; done

# Finish the merge
git commit -m "Merge origin/master; resolve __pycache__ conflicts (keep deleted)"

# Push if you need to
# git push origin master
```

## Option 2: Use the script (after deploying it)

```bash
cd ~/stylo
chmod +x scripts/resolve_pycache_merge.sh
./scripts/resolve_pycache_merge.sh
```

## What this does

- **Remote** removed `__pycache__` from the repo (stop tracking `.pyc`).
- **Your branch** still had those files as “modified”.
- Resolving with `git rm -f` keeps the **deletion**: `.pyc` files are no longer in the repo and `.gitignore` will keep them ignored.
