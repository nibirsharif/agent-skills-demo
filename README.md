# agent-skills-demo

This repo is a demo of [agent-skills](https://github.com/nibirsharif/agent-skills). It starts as a small URL shortener (create a short link, redirect to it), and new features are built step by step with its skills: spec → plan → tasks → verified code, with every step's files and commits kept in the history.

Python 3 standard library only; no dependencies to install.

## Run the server

```bash
python3 -m shortener --port 8000
```

```bash
curl -i -X POST localhost:8000/links -H 'X-User: alice' -d '{"url": "https://example.com"}'
curl -i localhost:8000/<code>
```

## Run the tests

```bash
python3 -m unittest
```
