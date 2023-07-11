
import json
import sys
import markdownify


def load_zip_files(filenames: list[str], id: str) -> dict[str, str]:
    import zipfile

    pages = {}

    for filename in filenames:
        archive = zipfile.ZipFile(filename, "r")

        file = None
        for f in archive.filelist:
            if f.filename.endswith("journal.db"):
                file = f
                break

        if file is None:
            print(f"Could not find journal.db in {filename}")
            exit(1)

        for line in archive.open(file):
            data = json.loads(line)
            if data['_id'] == id:
                for page in data['pages']:
                    title = page['name']
                    content = page['text']['content']
                    if title not in pages:
                        pages[title] = content
                    else:
                        pages[title] += '\n' + content
    return pages


pages = load_zip_files(sys.argv[1:], 'NfWjoESIxVhASMsp')

for (title, content) in pages.items():
    filename = title.lower().replace(' ', '_') + '.md'
    md = markdownify.markdownify(content)
    with open(filename, 'w') as f:
        f.write(md)
