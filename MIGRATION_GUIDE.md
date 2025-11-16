# Migration Guide: Aggressive Package Updates (Nov 2025)

## Übersicht

Dieses Dokument dokumentiert die Aktualisierung zu den neuesten Major Versions aller Abhängigkeiten:

| Paket | Alte Version | Neue Version | Status |
|-------|-------------|-------------|--------|
| processcube-sdk | 3-4.x | 6.0.0+ | 🔴 BREAKING |
| robotframework | 6.x | 7.x | 🟡 MINOR BREAKING |
| rpaframework | 16.x | 31.x | 🔴 MAJOR BREAKING |
| watchdog | 3.x | 6.x | 🟡 MINOR BREAKING |
| fastapi | 0.95.x | 0.121.x | ✅ KOMPATIBEL |
| uvicorn | 0.25.x | 0.38.x | ✅ KOMPATIBEL |
| typer | 0.9.x | 0.20.x | ✅ KOMPATIBEL |

---

## 1. rpaframework (16.x → 31.x) - KRITISCH

### Was hat sich geändert?

**Browser Automation:**
```robot
# Alte Version (16.x)
Open Browser    https://example.com    chrome

# Neue Version (31.x) - Nutzt jetzt Playwright statt Selenium
Open Browser    https://example.com    headlesschrome
```

**Neue Features:**
- Playwright Integration (besser als Selenium)
- Besseres Performance für Web Automation
- Neue Keywords für moderne Web-Frameworks

### Migration Steps

1. **Browser-Tests aktualisieren:**
   ```bash
   # Alte Selenium-Keywords müssen auf Playwright umgestellt werden
   grep -r "Open Browser" robots/src/rcc/
   ```

2. **Neue Keywords nutzen:**
   ```robot
   # Nutze neue Playwright-Features
   Open Browser    https://example.com    chromium
   Get Page State   # Neues Keyword
   Evaluate    # Bessere JavaScript-Unterstützung
   ```

3. **Testen:**
   ```bash
   rcc robot run --directory robots/src/rcc/<robot>/
   ```

### Kompatibilität Checklist

- [ ] Alle Web-Automation Tests durchführen
- [ ] Browser-Kompatibilität verifizieren
- [ ] Screenshots/Video-Recording testen
- [ ] Fehlerbehandlung überprüfen

---

## 2. robotframework (6.x → 7.x) - MINOR BREAKING

### Was hat sich geändert?

**Listener/Visitor APIs:**
```python
# Alte Version
class MyListener:
    ROBOT_LISTENER_API_VERSION = 2

    def start_suite(self, data, result):
        pass

# Neue Version (7.x)
class MyListener:
    ROBOT_LISTENER_API_VERSION = 3

    def start_suite(self, data, result):
        pass  # Signature gleich, aber Version-Number wichtig!
```

**Neue Features:**
- Bessere Python 3.12+ Support
- Performance Improvements (bis zu 20%)
- Verbesserte Error Messages

### Migration Steps

1. **Listener aktualisieren (falls vorhanden):**
   ```python
   # Überprüfe ob Custom Listeners verwendet werden
   grep -r "ROBOT_LISTENER_API_VERSION" robots/

   # Falls ja: Version auf 3 setzen
   ```

2. **Output/Reporting anpassen:**
   ```bash
   # Log-Format könnte sich geändert haben
   # Überprüfe ob Log-Parser noch funktionieren
   ```

3. **Performance testen:**
   ```bash
   time rcc robot run --directory robots/src/rcc/<robot>/
   ```

### Kompatibilität Checklist

- [ ] Custom Listeners prüfen und aktualisieren
- [ ] Output-Parsing überprüfen
- [ ] Performance-Tests durchführen
- [ ] Log-Datei-Format überprüfen

---

## 3. processcube-sdk (3-4.x → 6.0.0) - BREAKING

### Was hat sich geändert?

**API Struktur:**
```python
# Alte Version
from processcube_sdk.external_task import ExternalTaskClient

client = ExternalTaskClient(base_url="http://localhost:56100")

# Neue Version (6.0.0)
from processcube_sdk import ExternalTaskClient

client = ExternalTaskClient(base_url="http://localhost:56100")
```

**Event Handling:**
```python
# Alte Version
handler.subscribe_to_topic("robot_task.webui", callback)

# Neue Version
handler.subscribe("robot_task.webui", callback)  # Umbenannt
```

### Migration Steps

1. **Imports überprüfen:**
   ```bash
   grep -r "from processcube_sdk" processcube_robot_agent/
   ```

2. **SDK-Integration testen:**
   ```bash
   python -m processcube_robot_agent serve
   ```

3. **externe Tasks überprüfen:**
   ```bash
   # Verifiziere dass externe Tasks korrekt registriert werden
   curl http://localhost:42042/robot_agents/robots
   ```

### Kompatibilität Checklist

- [ ] Imports aktualisieren
- [ ] External Task Handler testen
- [ ] Topic-Registrierung überprüfen
- [ ] Error-Handling überprüfen

---

## 4. watchdog (3.x → 6.x) - MINOR BREAKING

### Was hat sich geändert?

**Event Handler:**
```python
# Alte Version (3.x)
from watchdog.events import FileSystemEventHandler

class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(event.src_path)

# Neue Version (6.x) - API ähnlich, aber bessere Performance
class MyHandler(FileSystemEventHandler):
    def on_modified(self, event):
        print(event.src_path)  # Gleiches Interface
```

**Neue Features:**
- Besseres Cross-Platform Support (Windows, macOS, Linux)
- Performance Improvements
- Stabilere File-System Monitoring

### Migration Steps

1. **File Watcher testen:**
   ```bash
   # Erstelle Test-Datei und überprüfe ob sie erkannt wird
   touch robots/src/rcc/test/robot.yaml
   echo "Check logs..."
   ```

2. **Performance überprüfen:**
   ```bash
   # Überprüfe ob Watcher schneller reagiert
   time rcc robot wrap --directory robots/src/rcc/test
   ```

### Kompatibilität Checklist

- [ ] File Watcher funktioniert
- [ ] Alte Tests weiterhin bestehen
- [ ] Performance überprüfen
- [ ] Cross-Platform-Tests (falls nötig)

---

## 5. Andere Pakete (KOMPATIBEL)

### fastapi (0.95.x → 0.121.x)
- Vollständig abwärtskompatibel
- Nur Performance & Security Improvements
- Keine Code-Änderungen nötig

### uvicorn (0.25.x → 0.38.x)
- Vollständig abwärtskompatibel
- Loop-Parameter bereits entfernt (Phase 1)
- Keine Code-Änderungen nötig

### typer (0.9.x → 0.20.x)
- Vollständig abwärtskompatibel
- Neue Features für CLI, aber alte API funktioniert
- Keine Code-Änderungen nötig

---

## Testing Strategy

### 1. Unit Tests ausführen
```bash
pytest tests/ -v --cov=processcube_robot_agent --cov-fail-under=70
```

### 2. Robots testen
```bash
# Alle Robots ausführen
rcc robot run --directory robots/src/rcc/
```

### 3. Integration testen
```bash
# Starte Service
python -m processcube_robot_agent serve

# In separatem Terminal
curl http://localhost:42042/robot_agents/robots
```

### 4. Regressions überprüfen
```bash
# Alte Tests sollten alle bestehen
pytest tests/ -v
```

---

## Rollback Plan

Falls kritische Issues auftreten:

```bash
# Backup der neuen Version
git stash

# Zu alter Version zurückspulen
git checkout <commit_vor_update>

# Alte requirements.txt wiederherstellen
pip install -r requirements.txt
```

---

## Known Issues & Workarounds

### Issue 1: rpaframework Playwright Init
**Problem:** Erste Playwright-Initialisierung kann langsam sein (30-60s)
**Workaround:** Browser-Init in Setup oder vorher durchführen

### Issue 2: Robot Framework Custom Listeners
**Problem:** Alte Listener-APIs funktionieren nicht
**Workaround:** ROBOT_LISTENER_API_VERSION auf 3 aktualisieren

---

## Success Criteria

✅ Alle Unit Tests bestehen (70%+ coverage)
✅ Alle Robots ausführbar ohne Fehler
✅ ProcessCube Integration funktioniert
✅ Keine Breaking Changes im bisherigen Code
✅ Performance nicht schlechter als vorher

---

## Next Steps

1. **Installation:** `pip install -r requirements.txt`
2. **Testing:** Führe Unit Tests aus
3. **Robot Testing:** Alle Robots durchlaufen lassen
4. **Integration:** Mit ProcessCube testen
5. **Deployment:** In Staging deployen
6. **Monitoring:** Logs überprüfen

---

**Erstellt:** November 2025
**Gültig bis:** Dezember 2025
**Verwalter:** Development Team