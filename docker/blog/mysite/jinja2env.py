from django.templatetags.static import static
from jinja2 import Environment

WWW = "https://www.quantiota.ai"
ROUTES = {
    "index": WWW + "/",
    "contact": WWW + "/contact-us",
    "signin": WWW + "/sign-in",
    "compliance": WWW + "/compliance",
}


def url_for(endpoint, **values):
    """Flask-compatible shim so www's Jinja2 templates work unchanged."""
    if endpoint == "static":
        return static(values["filename"])
    return ROUTES.get(endpoint, "/")


def image_url(image, spec):
    """Absolute URL of an image rendition (for og:image, which needs a bare
    https:// URL, not the <img> tag that Wagtail's image() global returns).
    Prepends the default Site's root_url (https://blog.quantiota.ai)."""
    if image is None:
        return ""
    url = image.get_rendition(spec).url
    if not url.startswith(("http://", "https://")):
        from wagtail.models import Site

        site = Site.objects.filter(is_default_site=True).first()
        if site:
            url = site.root_url + url
    return url


def environment(**options):
    env = Environment(**options)
    env.globals.update(url_for=url_for, static=static, image_url=image_url)
    return env
