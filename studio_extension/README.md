# Example

Um die Extension zu bauen, müssen folgende Befehle ausgeführt werden:

```
npm ci
npm run build
# alternative: npm run build -- --watch
```

Anschließend 5Minds studio mit `--extension-development-dir` starten:

```
# Beispiel für die Beta auf macOS:
/Applications/5Minds\ Studio\ \(Beta\).app/Contents/MacOS/5Minds\ Studio\ \(Beta\) --extension-development-dir "${PWD}"
```
