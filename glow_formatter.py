class GlowFormatter:
    """
    A class to format text as Markdown for Glow terminal-based Markdown readers.
    """

    @staticmethod
    def header(text, level=1):
        """
        Formats a header.
        :param text: The header text.
        :param level: The header level (1-6).
        :return: Formatted header string.
        """
        return f"{'#' * level} {text}"

    @staticmethod
    def list_item(text, ordered=False, index=None):
        """
        Formats a list item.
        :param text: The list item text.
        :param ordered: Whether the list is ordered.
        :param index: The index for ordered lists.
        :return: Formatted list item string.
        """
        if ordered:
            return f"{index}. {text}" if index is not None else f"1. {text}"
        return f"- {text}"

    @staticmethod
    def code_block(code, language=""):
        """
        Formats a code block.
        :param code: The code to format.
        :param language: The programming language (optional).
        :return: Formatted code block string.
        """
        return f"```{language}\n{code}\n```"

    @staticmethod
    def bold(text):
        """
        Formats text as bold.
        :param text: The text to format.
        :return: Formatted bold string.
        """
        return f"**{text}**"

    @staticmethod
    def italic(text):
        """
        Formats text as italic.
        :param text: The text to format.
        :return: Formatted italic string.
        """
        return f"*{text}*"

    @staticmethod
    def blockquote(text):
        """
        Formats a blockquote.
        :param text: The text to format.
        :return: Formatted blockquote string.
        """
        return f"> {text}"

    @staticmethod
    def horizontal_rule():
        """
        Returns a horizontal rule.
        :return: Horizontal rule string.
        """
        return "---"

# Example usage
if __name__ == "__main__":
    formatter = GlowFormatter()

    # Example Markdown content
    print(formatter.header("Glow Markdown Formatter", level=1))
    print(formatter.header("Features", level=2))
    print(formatter.list_item("Supports headers", ordered=False))
    print(formatter.list_item("Supports lists", ordered=False))
    print(formatter.list_item("Supports code blocks", ordered=False))
    print(formatter.code_block("print('Hello, World!')", language="python"))
    print(formatter.bold("Bold Text"))
    print(formatter.italic("Italic Text"))
    print(formatter.blockquote("This is a blockquote."))
    print(formatter.horizontal_rule())