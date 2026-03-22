import re

def escape_for_latex(text: str) -> str:
    if not isinstance(text, str):
        return text

    # 1. Normalize "Smart" characters and common JD symbols
    replacements = {
        '“': '"', '”': '"', "‘": "'", "’": "'",
        "—": "--", "–": "-", "•": r"$\bullet$",
        "…": "...", "©": r"\copyright", "®": r"\textregistered"
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)

    # 2. Standard LaTeX character escaping
    mapping = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }

    pattern = re.compile('|'.join(re.escape(key) for key in mapping.keys()))
    return pattern.sub(lambda match: mapping[match.group()], text)