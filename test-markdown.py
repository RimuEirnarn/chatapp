from chatapp import markdown

with open('test-markdown.md') as f:
    data = f.read()

md_data = markdown.parse(data)
ATTR_LISTED = [
    "{ #id .something .something }",
    "{#id .abc}",
    "{ .class }",
    "{.class}",
    "```{ #id .something .something }",
    "```{#id .abc}",
    "```{ .class }",
    "```{.class}",
    "{id=2}", # BEGIN ALLOWED DATA -- DO NOT STRIP THEM
    "{ 'data': true }",
    "{data: false}",
    r"\{id=2}"
]
for i in ATTR_LISTED:
    print(f"""{i!r:<40} -> {markdown.ATTR_LIST.sub("", i)!r}""")

#print('='*20)
#print(md_data)
#print('='*20)
#print(data)
