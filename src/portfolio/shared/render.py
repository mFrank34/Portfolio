import markdown
import bleach

from portfolio.shared.tag import ALLOWED_ATTRS, ALLOWED_TAGS

def render_html(content_md: str) -> str:
    raw_html = markdown.markdown(content_md)
    return bleach.clean(raw_html, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS)