from src.turndown import TurndownService

html_input = "<h1>Hallo Welt</h1><p>Dies ist ein Test</p>"
td = TurndownService({"headingStyle": "atx", "codeBlockStyle": "fenced"})
md_output = td.turndown(html_input)
print(md_output)
