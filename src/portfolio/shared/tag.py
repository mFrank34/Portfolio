import bleach

ALLOWED_TAGS = bleach.sanitizer.ALLOWED_TAGS.union(
    {"p", "pre", "h1", "h2", "h3", "h4", "img", "br", "hr", "span"}
)
ALLOWED_ATTRS = {**bleach.sanitizer.ALLOWED_ATTRIBUTES, "img": ["src", "alt", "title"]}
