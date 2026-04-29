---
name: hello
description: Initialize the repo with a HELLO.md file
---

Ensure the repo contains a `HELLO.md` file:

1. Use `readFile("HELLO.md")` to read the contents of "HELLO.md"
2. If the file is not available, use `writeFile('HELLO.md',"#Hello World")` to create a new file
3. Finally, activate the 'poem-writing' skill and use it to generate a new poem

If any step fails, print the string "BIG OOPS!"
