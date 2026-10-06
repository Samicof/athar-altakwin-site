# Athar Altakwin website

Official bilingual website for `athrtk.com`. Arabic is the default route (`/`); English is at `/en/`. It describes ATHR, VIA, and ARC as products in development and testing. This repository contains only public site assets. Private source documents are kept outside Git.

## Preview and checks

Run `python -m http.server 18080 --directory site`, then open `http://127.0.0.1:18080/` and `/en/`. Run `python scripts/check_site.py` to check the home, privacy, and 404 pages in both languages, local links, metadata, and published assets. Nginx returns the actual 404 status; the Python preview server only renders the saved 404 documents directly.

The site is static: there is no contact form, account, analytics script or application database. Contact links open the visitor's email app. The published assets use the supplied final Athar logo. The website's `athar-pattern-chevron-clean.svg` is a derivative of the identity guide's Chevron: it removes a diamond subpath present in the pattern asset but absent from the guide's Chevron example, and uses a transparent ground for the open page layout. The source asset and final logo are unchanged. The Strata SVG is copied unchanged. Cairo is self-hosted in Arabic and Latin subsets under SIL Open Font License 1.1; see `site/assets/Cairo-OFL.txt`.

## Image and deployment

On a push to `main`, GitHub Actions checks the site, builds the Nginx image from a digest-pinned official base, smokes the Arabic and English routes, and publishes `ghcr.io/samicof/athar-altakwin-site:sha-<commit>`. The deployment stack lives separately in `jorncafe-cmd/my-stacks`. Pin that stack to the reviewed image digest after CI succeeds. The server pulls the image; it does not build it or rely on Watchtower.

The stack routes both `athrtk.com` and `www.athrtk.com` through Traefik's `web` entrypoint. Nginx redirects `www` to the apex. Cloudflare Tunnel public hostnames should send both hosts to `http://localhost:8088`, after replacing any conflicting root DNS record. Cloudflare terminates public HTTPS, so Traefik has no TLS or redirect labels. Verify the final HTTPS responses externally after the owner approves the `my-stacks/main` push.

The privacy notice needs an owner decision based on the actual Cloudflare and server logging settings before publication. Do not assume a retention period or analytics configuration.
