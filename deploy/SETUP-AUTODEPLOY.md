# Auto-deploy (push = live) + GitHub backup

Goal: run `git push` once → the site updates on `artemisstrength.in` automatically,
**and** a backup copy lands on GitHub.

You need three details from your host (cPanel → look under "SSH Access" / the welcome email):
- **USER**  – your cPanel username (e.g. `artemis`)
- **HOST**  – your server hostname or IP (e.g. `server123.web-hosting.com`)
- **PORT**  – SSH port (often `22`; some hosts use a custom one like `21098`)

---

## 1. Enable SSH (one time)
In cPanel open **SSH Access** → **Manage SSH Keys** → generate or import a key and
**authorize** it. (Or use password login if your host allows it.) Confirm you can log in:

```bash
ssh -p PORT USER@HOST
```

## 2. Create the deploy repo + hook on the server
While logged in over SSH, build the bare repo:

```bash
cd ~
git init --bare artemis.git
```

Then create the hook and paste in the contents of **`deploy/post-receive`** from this repo:

```bash
nano ~/artemis.git/hooks/post-receive
# paste the file contents, then save: Ctrl+O, Enter, Ctrl+X
chmod +x ~/artemis.git/hooks/post-receive
```

> If your site is an **addon/subdomain**, edit the `WEB=` line in the hook to that
> domain's document root before saving.

Type `exit` to leave SSH.

## 3. Point your local repo at cPanel + GitHub

```bash
# --- cPanel deploy remote ---
git remote add cpanel ssh://USER@HOST:PORT/home/USER/artemis.git

# --- GitHub backup remote ---
# First create an EMPTY repo at https://github.com/new  (e.g. name: artemis-strength)
git remote add github https://github.com/YOURNAME/artemis-strength.git

# --- one command that pushes to BOTH ---
git remote add all ssh://USER@HOST:PORT/home/USER/artemis.git
git remote set-url --add --push all ssh://USER@HOST:PORT/home/USER/artemis.git
git remote set-url --add --push all https://github.com/YOURNAME/artemis-strength.git
```

## 4. First push (publishes the whole site)

```bash
git push all main
```

cPanel's hook fires and copies everything into `public_html`. Visit
**https://artemisstrength.in/** — it's live. GitHub now has the backup too.

---

## Everyday updates from now on

```bash
# 1. edit files
# 2. if you changed exercise DATA:
python build_seo.py
# 3. ship it (remember to bump ?v= in index.html if you edited css/js)
git add -A
git commit -m "what changed"
git push all main          # → deploys to cPanel AND backs up to GitHub
```

That's it — `git push all main` is your publish button.

## Troubleshooting
- **Permission denied (publickey):** your SSH key isn't authorized — redo step 1.
- **Push works but site unchanged:** check the hook is executable
  (`chmod +x ~/artemis.git/hooks/post-receive`) and the `WEB=` path is right.
- **Want to see deploy output:** the hook prints a line on each push; watch your
  terminal after `git push`.
