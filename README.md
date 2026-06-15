# AI Agent Lab — Wagtail Blog add-on

An optional **Wagtail blog** for the [AI Agent Lab](https://github.com/quantiota/AI-Agent-Lab),
served at `blog.<your-domain>`. It is **not shipped with the lab core** — drop these
files into a running lab and bring it up with a compose overlay. Nothing in the core
(`docker-compose.yaml`, nginx `default.conf.template`) is overwritten.

Features: Wagtail CMS themed with the lab's Vanilla templates (Jinja2), math via
**wagtail-katex**, YouTube oEmbed, local media served by Django, and SEO built in
(per-page titles/meta, canonical, Open Graph, `sitemap.xml`, `robots.txt`).

## Lab Journal — build, experiment, document, share

**AI Agent Lab + Lab Journal = build, experiment, document, and share.**

Use it to:

- Record experiment results
- Track project progress
- Document agent workflows
- Publish screenshots from Grafana
- Share code snippets
- Maintain research notes
- Create public or private journal entries

A typical workflow:

1. Run an experiment in AI Agent Lab.
2. Analyze the results in Grafana.
3. Take screenshots or export data.
4. Create a Lab Journal entry.
5. Publish it privately, to a team, or publicly.

## What's in here

```
docker/
  blog/                          → the Wagtail project              (copy to docker/blog/)
  docker-compose.blog.yml        → compose overlay (blog service)   (copy to docker/)
  nginx/conf.d/blog.conf.template→ blog vhost (own :80 + :443)      (copy to docker/nginx/conf.d/)
.env.blog.example                → env vars to append to docker/.env
```

## Prerequisites

- A running AI Agent Lab (`docker/` with `docker-compose.yaml`, nginx, and `.env` holding `DOMAIN`).
- A **DNS A record** `blog.<your-domain>` → the lab's server IP.
- TLS for `blog.<your-domain>` (see step 4).

## Install

1. **Copy the files into the lab's `docker/` tree:**
   ```bash
   cp -r ai-agent-lab-blog/docker/* /path/to/AI-Agent-Lab/docker/
   ```

2. **Add the env var.** Append `.env.blog.example` to `docker/.env` and set a real secret:
   ```bash
   cat ai-agent-lab-blog/.env.blog.example >> /path/to/AI-Agent-Lab/docker/.env
   # then edit docker/.env → set WAGTAIL_SECRET_KEY
   ```
   `DOMAIN` is already in the lab's `.env`; the blog auto-derives `ALLOWED_HOSTS`/CSRF and
   the nginx vhost from it (`blog.<DOMAIN>`). No code edit needed.

3. **TLS** — obtain a cert for `blog.<your-domain>` (the lab already runs certbot). Example http-01:
   ```bash
   cd /path/to/AI-Agent-Lab/docker
   docker compose run --rm certbot certonly --webroot -w /usr/share/nginx/html -d blog.$DOMAIN
   ```

4. **Build & start with the overlay** (always pass BOTH `-f` files):
   ```bash
   cd /path/to/AI-Agent-Lab/docker
   docker compose -f docker-compose.yaml -f docker-compose.blog.yml up -d --build
   ```

5. **Initialise the blog:**
   ```bash
   BLOG="docker compose -f docker-compose.yaml -f docker-compose.blog.yml exec blog"
   $BLOG python manage.py migrate
   $BLOG python manage.py createsuperuser   # no default admin exists — this sets your own username + password
   ```

6. **Set the Wagtail Site record to https** (so canonical/OG/sitemap URLs are `https://…`):
   admin → **Settings → Sites** → set hostname `blog.<DOMAIN>`, **port 443**. (Or via shell:
   `$BLOG python manage.py shell -c "from wagtail.models import Site; s=Site.objects.get(is_default_site=True); s.hostname='blog.'+__import__('os').environ['DOMAIN']; s.port=443; s.save()"`)

Visit `https://blog.<your-domain>` and log in at `/admin/`.

## Day-to-day

Always include both compose files for any command touching the blog:
```bash
docker compose -f docker-compose.yaml -f docker-compose.blog.yml <cmd>
```
**Authoring math:** use the KaTeX button in the rich-text toolbar (don't paste raw HTML —
the editor strips it). Don't open math posts in the editor expecting to hand-edit the markup.

## Uninstall

```bash
cd /path/to/AI-Agent-Lab/docker
docker compose -f docker-compose.yaml -f docker-compose.blog.yml down
rm -f docker-compose.blog.yml nginx/conf.d/blog.conf.template nginx/conf.d/blog.conf
rm -rf blog
# (optional) remove the blog-data / blog-media volumes and the WAGTAIL_SECRET_KEY line from .env
```

## Notes / caveats

- **Overlay model** — the core `docker-compose.yaml` and nginx `default.conf.template` are
  never modified, so the add-on survives lab updates. The only "shared" touch is dropping
  `blog.conf.template` into `nginx/conf.d/` (auto-loaded by `include conf.d/*.conf`).
- The blog vhost is **self-contained** (its own `:80` redirect + ACME and `:443` proxy), so it
  doesn't depend on anything in `default.conf`.
- Static files are baked at image build (WhiteNoise); uploaded media persists in the
  `blog-media` volume and is served by Django.
