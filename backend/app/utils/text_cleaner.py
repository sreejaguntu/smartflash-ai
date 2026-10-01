import re
import unicodedata


class TextCleaner:

    @staticmethod
    def clean(text: str) -> str:
        if not text:
            return ""

        # Normalize unicode (e.g. smart quotes, ligatures) to a canonical form
        text = unicodedata.normalize("NFKC", text)

        # Remove control/non-printable characters, keep newlines and tabs
        text = "".join(
            ch for ch in text
            if ch in ("\n", "\t") or not unicodedata.category(ch).startswith("C")
        )

        # Join words split by a hyphen at a line break: "exam-\nple" -> "example"
        text = re.sub(r"-\n\s*", "", text)

        # Replace remaining single newlines inside a paragraph with a space
        text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

        # Collapse runs of spaces/tabs into a single space
        text = re.sub(r"[ \t]+", " ", text)

        # Collapse 3+ consecutive newlines into a single blank line
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Trim trailing/leading whitespace on each line
        text = "\n".join(line.strip() for line in text.split("\n"))

        return text.strip()
