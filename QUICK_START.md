# ProcessCube Robot Agent - Quick Start Guide

> Schnelle Referenz für die häufigsten Aufgaben

## 🚀 5-Minuten Setup

```bash
# 1. Abhängigkeiten installieren
npm install

# 2. Service starten
npm run processcube_robot_agent

# 3. Robots checken (neues Terminal)
curl http://localhost:42042/robot_agents/robots
```

**Fertig!** Der Agent läuft auf `http://localhost:42042`

---

## 📝 Cheat Sheet

### Service Management

```bash
# Service starten
npm run processcube_robot_agent
# oder
npm run run

# Service mit Debug
CONFIG_FILE=./config.dev.json npm run processcube_robot_agent

# Service mit anderer Config (Windows)
set CONFIG_FILE=config.dev-win.json && npm run processcube_robot_agent
```

### Robots verwalten

```bash
# Alle Robots auflisten
curl http://localhost:42042/robot_agents/robots

# Robot manuell packen
npm run pack

# Robot lokal testen
cd robots/src/rcc/<robot-name>
robot tasks.robot

# Mit RCC lokal testen
rcc run -c robots/src/rcc/<robot-name>
```

### Development

```bash
# Python venv erstellen
python -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# Logs anschauen
tail -f ~/.processcube/robot-agent/logs.txt

# RCC checken
rcc version
rcc robot list
```

### Studio Extension

```bash
# Bauen
cd studio_extension
npm run build

# Starten mit Dev-Erweiterung
5minds-studio --extension-development-dir=./studio_extension

# Installation in Studio (manuell oder Script)
npm run install_studio_extension
```

---

## 🆘 Häufige Probleme

| Problem | Lösung |
|---------|--------|
| `ModuleNotFoundError: No module named 'processcube_robot_agent'` | `export PYTHONPATH=$(pwd)` |
| `rcc: command not found` | RCC installieren: https://github.com/robocorp/rcc |
| `Address already in use` | Port 42042 in config ändern |
| Robot wird nicht registriert | `npm run pack` ausführen, Service neu starten |
| Studio-Erweiterung lädt nicht | `cd studio_extension && npm run build` |

---

## 🔧 Konfiguration ändern

```bash
# 1. Config-Datei öffnen
nano config.dev.json

# 2. Parameter ändern
{
  "rest_api": {
    "port": 42042,      # ← Port ändern hier
    "host": "0.0.0.0"
  }
}

# 3. Service neu starten
npm run processcube_robot_agent
```

### Wichtige Parameter

| Parameter | Beschreibung |
|-----------|-------------|
| `rest_api.port` | HTTP-Port des Services (default: 42042) |
| `rcc.topic_prefix` | Präfix für Robot-Topics (default: rcc) |
| `rcc.project_dir` | Wo Robot-Quellen liegen (default: robots/src/rcc) |
| `engine.url` | ProcessCube-Engine URL |

---

## 📦 Neuen Robot erstellen

```bash
# 1. Verzeichnis anlegen
mkdir robots/src/rcc/my-robot
cd robots/src/rcc/my-robot

# 2. Konfiguration (robot.yaml)
cat > robot.yaml << 'EOF'
tasks:
  MyTask:
    robotTaskName: Meine Task
condaConfigFile: conda.yaml
artifactsDir: output
PATH: [.]
PYTHONPATH: [.]
EOF

# 3. Tasks definieren (tasks.robot)
cat > tasks.robot << 'EOF'
*** Tasks ***
MyTask
    Log    Hallo Welt!
EOF

# 4. Dependencies (conda.yaml)
cat > conda.yaml << 'EOF'
channels:
  - conda-forge
dependencies:
  - python=3.9
  - pip
  - pip:
    - rpaframework>=15.1.4
EOF

# 5. Service neu starten
npm run processcube_robot_agent

# 6. Robot sollte jetzt registriert sein
curl http://localhost:42042/robot_agents/robots
# Output sollte "my-robot" enthalten
```

---

## ✅ Checklist für neue Robots

- [ ] robot.yaml erstellt mit TaskName
- [ ] tasks.robot mit *** Tasks *** Sektion
- [ ] conda.yaml mit Dependencies
- [ ] Lokal getestet: `robot tasks.robot`
- [ ] Service neu gestartet
- [ ] In Robot-Liste sichtbar: `curl http://localhost:42042/robot_agents/robots`
- [ ] In Studio verfügbar

---

## 🧪 Robot lokal testen

```bash
cd robots/src/rcc/<robot-name>

# Einfacher Test
robot --task TaskName tasks.robot

# Mit Debugging
robot --debugfile debug.txt --task TaskName tasks.robot

# Output anschauen
open output/log.html
```

---

## 🐛 Debugging

### Service-Logs

```bash
# Letzte 50 Zeilen
tail -50 ~/.processcube/robot-agent/logs.txt

# Kontinuierlich folgen
tail -f ~/.processcube/robot-agent/logs.txt

# Alle mit "ERROR"
grep ERROR ~/.processcube/robot-agent/logs.txt
```

### RCC Debug

```bash
# RCC mit Debug-Output
RCC_DEBUG=true npm run processcube_robot_agent

# RCC Version checken
rcc version

# Robots auflisten
rcc robot list
```

### Python Debug

```bash
# Debug-Mode in config.dev.json aktivieren:
{
  "debugging": {
    "enabled": true,
    "port": 5678,
    "wait_for_client": true
  }
}

# Service starten und auf Debugger warten
npm run processcube_robot_agent

# PyCharm/VSCode: Debug konfigurieren für localhost:5678
```

---

## 📊 Metriken & Monitoring

### Service Status

```bash
# Service läuft?
curl -s http://localhost:42042/robot_agents/robots | jq .

# Port belegt?
lsof -i :42042

# Prozess Infos
ps aux | grep processcube_robot_agent
```

### Performance

```bash
# Temp-Verzeichnis Größe
du -sh temp/

# Output-Dateien
find robots/installed -name "*.zip" | wc -l

# Logs Größe
du -sh ~/.processcube/robot-agent/
```

---

## 🔐 Sicherheit

### Vor Produktion prüfen

- [ ] Shell-Injection-Fix angewendet (subprocess arguments)
- [ ] Alle Dependencies aktualisiert
- [ ] Tests geschrieben und grün
- [ ] Secrets nicht in Code (nur in .env oder Config)
- [ ] HTTPS für Production konfiguriert
- [ ] Firewall: Nur notwendige Ports offen

### Secrets verwalten

```bash
# NICHT: Passwörter in Code
password = "secret123"

# JA: Aus Environment oder Config File
from os import getenv
password = getenv("DB_PASSWORD")

# Oder Config mit .env
# .env Datei
DB_PASSWORD=secret123

# In Python
from dotenv import load_dotenv
load_dotenv()
password = getenv("DB_PASSWORD")
```

---

## 📚 Häufig benötigte Befehle

```bash
# Python Package Info
python -m pip show processcube-sdk

# Version Check
rcc version
robot --version
python --version
node --version

# Installation Verify
python -c "import processcube_robot_agent; print('OK')"
rcc robot wrap --help
robot --help

# Cleanup
rm -rf temp/robots/
rm -rf robots/installed/rcc/
npm clean-install  # Neu installieren

# Update alle Dependencies
pip install --upgrade -r requirements.txt
npm update
```

---

## 🎓 Nächste Schritte

1. **Grundlagen:** Lesen Sie [README.md](./README.md)
2. **Detaillierter:** Siehe [ARCHITECTURE.md](./ARCHITECTURE.md) (wird erstellt)
3. **Probleme:** Siehe [ANALYSIS.md](./ANALYSIS.md)
4. **Entwicklung:** Robot Framework Docs: https://robotframework.org/

---

## 💡 Tipps & Tricks

### Auto-Reload aktivieren

```json
{
  "rcc": {
    "start_watch_project_dir": true
  }
}
```
Ändert einen Robot und der wird automatisch gepackt und registriert.

### Mehrere Agents laufen lassen

```bash
# Terminal 1 (Port 42042)
npm run processcube_robot_agent

# Terminal 2 (Port 42043)
cat config.dev.json | sed 's/42042/42043/' > config.dev2.json
CONFIG_FILE=./config.dev2.json npm run processcube_robot_agent
```

### IDE Integration

**VSCode:**
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black"
}
```

**PyCharm:**
- Settings → Project → Python Interpreter → Add Interpreter
- Wählen Sie den venv aus

---

## 📞 Support

- **Robot Framework:** https://robotframework.org/
- **RPA Framework:** https://rpaframework.org/
- **ProcessCube Docs:** https://processcube.io/
- **Issues:** https://github.com/5minds/processcube-robot-agent/issues

---

**Version:** 1.0
**Zuletzt aktualisiert:** November 2025
