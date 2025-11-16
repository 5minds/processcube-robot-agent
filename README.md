# ProcessCube Robot Agent

> Eine RPA-Integrationslösung, die Robot Framework-basierte Automatisierungen mit ProcessCube Workflow-Engines verbindet.

## 🎯 Überblick

Das **ProcessCube Robot Agent** Projekt ist eine umfassende Lösung zur Integration von Robotic Process Automation (RPA) mit ProcessCube, einem BPM-System (Business Process Management). Es besteht aus drei Hauptkomponenten:

1. **processcube_robot_agent** - Ein Python-basierter Microservice, der RPA-Roboter verwaltet und ausführt
2. **robots** - Eine Sammlung von Robot Framework-basierten Automatisierungsaufgaben
3. **studio_extension** - Eine TypeScript/React-Erweiterung für die 5Minds Studio IDE

### Architektur

```
┌─────────────────────────────────┐
│    ProcessCube Engine           │ (Workflow-Engine)
│    (BPMN Prozesse)              │
└──────────┬──────────────────────┘
           │
      External Tasks
           │
┌──────────▼──────────────────────┐
│  Robot Agent Service (Python)   │ (REST API Port 42042)
│  ├── Task Handler               │
│  ├── RCC Runner                 │
│  └── File Watcher (Auto-reload) │
└──────────┬──────────────────────┘
           │
           ├─► RPA Robots (.zip packages)
           │   ├── Web UI Automation
           │   ├── Windows UI Automation
           │   └── Custom Tasks
           │
           └─► RCC (Robot Code Compiler)
               └── Robocorp's Robot Packaging Tool
```

---

## 📋 Inhaltsverzeichnis

1. [Installation & Setup](#installation--setup)
2. [Schnelleinstieg](#schnelleinstieg)
3. [Konfiguration](#konfiguration)
4. [Projektstruktur](#projektstruktur)
5. [Robot-Entwicklung](#robot-entwicklung)
6. [Studio-Erweiterung](#studio-erweiterung)
7. [API-Dokumentation](#api-dokumentation)
8. [Entwicklung & Debugging](#entwicklung--debugging)
9. [Problembehebung](#problembehebung)
10. [Contributing](#contributing)

---

## 🚀 Installation & Setup

### Voraussetzungen

- **Python** 3.8 oder höher
- **Node.js** 14.x oder höher (für Studio-Erweiterung)
- **npm** 6.x oder höher
- **RCC** (Robocorp Command Center) - Download: https://github.com/robocorp/rcc
- **Git**

### Installation

#### 1. Repository klonen

```bash
git clone https://github.com/5minds/processcube-robot-agent.git
cd processcube-robot-agent
```

#### 2. Python-Abhängigkeiten installieren

```bash
# Option A: Mit npm Scripts (empfohlen)
npm install

# Option B: Direkt mit pip
pip install -r requirements.txt
```

#### 3. RCC installieren und validieren

```bash
# RCC herunterladen und in PATH platzieren
# https://github.com/robocorp/rcc/releases

# Überprüfung:
rcc version
```

#### 4. Node-Abhängigkeiten installieren

```bash
npm install
```

#### 5. Studio-Erweiterung bauen (optional)

```bash
cd studio_extension
npm ci
npm run build
cd ..
```

### Erste Ausführung

```bash
# Startet den Robot Agent Service
npm run processcube_robot_agent

# Output sollte ähnlich aussehen:
# INFO:     Application startup complete [uvicorn]
# INFO:     Uvicorn running on http://0.0.0.0:42042 (Press CTRL+C to quit)
```

---

## ⚡ Schnelleinstieg

### 1. Service starten

```bash
# Terminal 1: Robot Agent Service
npm run processcube_robot_agent
# Service läuft auf http://localhost:42042
```

### 2. Verfügbare Robots prüfen

```bash
# Terminal 2: Alle Robots auflisten
curl http://localhost:42042/robot_agents/robots

# Output:
# {
#   "topics": [
#     {"name": "webui", "topic": "rcc/webui"}
#   ]
# }
```

### 3. Mit ProcessCube verbinden

```bash
# ProcessCube-Engine muss auf einem bekannten Service registrieren können
# Der Agent ist dann verfügbar unter dem konfigurierten URL
# (Standard: http://localhost:42042)
```

### 4. Einen eigenen Robot erstellen

```bash
# 1. Neuen Robot-Ordner anlegen
mkdir robots/src/rcc/my-robot
cd robots/src/rcc/my-robot

# 2. Robot-Vorlage erstellen
cat > robot.yaml << 'EOF'
tasks:
  MyTask:
    robotTaskName: Meine Custom Task
condaConfigFile: conda.yaml
artifactsDir: output
PATH: [.]
PYTHONPATH: [.]
EOF

# 3. Tasks definieren
cat > tasks.robot << 'EOF'
*** Settings ***
Library    RPA.Browser.Selenium

*** Tasks ***
MyTask
    Log    Hallo Welt!
EOF

# 4. Conda-Umgebung definieren
cat > conda.yaml << 'EOF'
channels:
  - conda-forge
dependencies:
  - python=3.9
  - pip
  - pip:
    - rpaframework>=15.1.4
EOF

# Der Robot wird automatisch beim nächsten Service-Start gepackt und registriert
```

---

## ⚙️ Konfiguration

### Konfigurationsdatei

Die Service-Konfiguration erfolgt über JSON-Dateien im Root-Verzeichnis:

- **config.dev.json** - Linux/macOS Entwicklung
- **config.dev-win.json** - Windows Entwicklung
- Umgebungsvariable: `CONFIG_FILE` definiert, welche Datei geladen wird

### Konfigurationsstruktur

```json
{
  "debugging": {
    "enabled": true,
    "hostname": "localhost",
    "port": 5678,
    "wait_for_client": false
  },
  "engine": {
    "url": "http://localhost:56100"
  },
  "rcc": {
    "topic_prefix": "rcc",
    "wrap_dir": "robots/installed/rcc",
    "unwrap_dir": "temp/robots/rcc/unwrapped",
    "start_watch_project_dir": true,
    "project_dir": "robots/src/rcc"
  },
  "rest_api": {
    "port": 42042,
    "host": "0.0.0.0"
  }
}
```

### Konfigurationsparameter Erklärung

| Parameter | Beschreibung | Standard |
|-----------|-------------|----------|
| `debugging.enabled` | Debug-Mode aktivieren (Port 5678) | `false` |
| `engine.url` | ProcessCube-Engine URL | - |
| `rcc.topic_prefix` | Präfix für Robot Topics | `robot_task` |
| `rcc.wrap_dir` | Ausgabeverzeichnis für gepackte Robots | `robots/installed/rcc` |
| `rcc.unwrap_dir` | Temp-Verzeichnis beim Unpacking | `temp/robots/rcc/unwrapped` |
| `rcc.start_watch_project_dir` | Auto-Reload bei Dateiänderungen | `true` |
| `rcc.project_dir` | Robot-Quellverzeichnis | `robots/src/rcc` |
| `rest_api.port` | Service-Port | `42042` |
| `rest_api.host` | Listen-Adresse | `0.0.0.0` |

### Umgebungsvariablen

```bash
# Konfigurationsdatei auswählen
export CONFIG_FILE=/path/to/config.json

# Python-Path für Importe
export PYTHONPATH=/path/to/processcube-robot-agent

# RCC Debug-Output
export RCC_DEBUG=true
```

### Mehrere Konfigurationen

Für verschiedene Umgebungen (Dev, Staging, Prod):

```bash
# Development
CONFIG_FILE=./config.dev.json npm run processcube_robot_agent

# Production
CONFIG_FILE=./config.prod.json npm run processcube_robot_agent
```

---

## 📁 Projektstruktur

```
processcube-robot-agent/
│
├── processcube_robot_agent/          # Backend-Microservice (Python)
│   ├── __main__.py                   # CLI-Einstiegspunkt
│   ├── rest_api_command.py           # REST API Server
│   ├── pack_robots_command.py        # Packaging-Kommando
│   ├── watch_robots_command.py       # File-Watcher-Kommando
│   │
│   ├── robot_agent/                  # Agent-Logik
│   │   ├── base_agent.py             # Abstrakte Basisklasse
│   │   ├── builder.py                # Factory-Builder
│   │   ├── error.py                  # Custom Exception
│   │   │
│   │   └── rcc/                      # RCC-Implementierung
│   │       ├── robot_agent.py        # Hauptausführungs-Engine
│   │       ├── rcc_runner.py         # RCC-Validator
│   │       ├── robot_task_handler_factory.py  # Factory Pattern
│   │       ├── project_packer.py     # Robot-Packaging
│   │       └── project_watcher.py    # Hot-Reload Watcher
│   │
│   ├── external_task/                # ProcessCube Integration
│   │   └── robot_task_handler.py     # External Task Handler
│   │
│   └── rest_api/                     # HTTP-Endpoints
│       └── robots.py                 # Robot-List-Endpoint
│
├── robots/                           # RPA Robot-Definitionen
│   ├── src/rcc/                      # Quell-Robots
│   │   ├── webui/                    # Web UI Automatisierung
│   │   ├── windows/
│   │   │   └── ui/                   # Windows UI Automatisierung
│   │   ├── windows-example-calculator/
│   │   └── web-example-rpa-challenge/
│   │
│   ├── installed/                    # Gepackte, einsatzbereite Robots
│   │   └── rcc/                      # RCC-gepackte .zip Dateien
│   │
│   └── backup/                       # Backup von Robots
│       └── readexcel/                # Excel-Lese-Beispiel
│
├── studio_extension/                 # TypeScript/React IDE-Erweiterung
│   ├── index.ts                      # Erweiterungs-Einstiegspunkt
│   ├── robotServiceType/             # Robot Service-Type UI
│   │   ├── initializeServiceTypeRobot.ts
│   │   ├── PropertiesRobotTaskPane.tsx
│   │   ├── PropertiesRobotTaskPaneContent.tsx
│   │   ├── fetchRobots.ts
│   │   └── PropertiesRobotServiceTask.md
│   │
│   ├── agentSettings/                # Agent-Konfiguration UI
│   │   ├── initializeAgentSettingsEditor.ts
│   │   ├── getRobotAgents.ts
│   │   ├── RobotAgentsConfigDocument.ts
│   │   └── RobotAgentsConfigEditor.tsx
│   │
│   ├── package.json
│   ├── tsconfig.json
│   ├── webpack.config.js
│   └── README.md
│
├── processes/                        # Beispiel BPMN-Prozesse
│   ├── RobotTask.bpmn
│   └── .processcube/
│
├── package.json                      # Root NPM-Konfiguration
├── requirements.txt                  # Python-Abhängigkeiten
├── config.dev.json                   # Linux/macOS Dev-Konfiguration
├── config.dev-win.json               # Windows Dev-Konfiguration
├── start_on_windows.sh               # Windows Startup-Script
│
└── README.md                         # Diese Datei
```

---

## 🤖 Robot-Entwicklung

### Robot Framework Grundlagen

Robot Framework ist ein Python-basiertes, textgetriebenes Automatisierungstool mit roboterlesbarer Syntax:

```robot
*** Settings ***
Library    Collections
Library    RPA.Browser.Selenium

*** Variables ***
${USERNAME}    admin
${PASSWORD}    pw123

*** Tasks ***
Login And Verify
    Open Browser    https://example.com/login    chrome
    Input Text    id:username    ${USERNAME}
    Input Text    id:password    ${PASSWORD}
    Click Button   xpath://button[@type='submit']
    Page Should Contain    Welcome

*** Keywords ***
Login As User
    [Arguments]    ${user}    ${pass}
    Input Text    id:username    ${user}
    Input Text    id:password    ${pass}
    Click Button   xpath://button[@type='submit']
```

### Robot-Projekt-Struktur

Ein Minimal-Robot mit den erforderlichen Dateien:

```
my-robot/
├── robot.yaml              # Robot-Metadaten
├── tasks.robot             # Task-Definitionen
├── conda.yaml              # Abhängigkeiten
├── locators.json           # Optional: UI-Element-Locators
└── output/                 # Output-Verzeichnis (vom System erstellt)
    ├── output.xml          # Test-Ergebnisse
    ├── log.html            # HTML-Log
    └── report.html         # Testbericht
```

### robot.yaml - Konfiguration

```yaml
# Task-Definitionen
tasks:
  TaskName:
    robotTaskName: Anzeigename für ProcessCube
  SecondTask:
    robotTaskName: Zweite Task

# Conda-Umgebungskonfiguration
condaConfigFile: conda.yaml

# Ausgabeverzeichnis
artifactsDir: output

# Pfadvariablen
PATH: [.]
PYTHONPATH: [.]
```

### tasks.robot - Task-Definition

```robot
*** Settings ***
Library    RPA.Browser.Selenium
Library    RPA.HTTP
Library    Collections
Resource   common.robot

*** Tasks ***
WebUI Example
    Open Available Browser    https://www.example.com
    Click Element When Visible    css=.cookie-accept
    Take Screenshot    full
    Close Browser

Process Data
    ${data}=    Get Request    https://api.example.com/data
    ${json}=    Evaluate    ${data.text}
    Log    ${json}[0][name]
```

### conda.yaml - Abhängigkeiten

```yaml
channels:
  - conda-forge
  - defaults

dependencies:
  - python=3.9
  - pip
  - chromium

  - pip:
    - rpaframework>=15.1.4
    - robotframework>=5.0.1
    - robotframework-tidy
    - selenium>=4.0.0
```

### Work Items (Ein-/Ausgabe)

Robot Framework arbeitet mit **Work Items** für strukturierte Datenverwaltung:

#### Input in tasks.robot

```robot
*** Settings ***
Library    RPA.Robocorp.Process

*** Tasks ***
Process Purchase Order
    ${order_data}=    Get Work Item Variable    order_id
    ${customer}=      Get Work Item Variable    customer_name

    Log    Processing order ${order_id} for ${customer}
    # ... weitere Verarbeitung ...

    Set Work Item Variable    status    completed
    Set Work Item Variable    result_data    ${result}
```

#### JSON Input von ProcessCube

```json
{
  "order_id": "ORD-12345",
  "customer_name": "Acme Corp",
  "items": [
    {"sku": "ITEM-001", "qty": 5}
  ]
}
```

### Robots lokal testen

```bash
# Single Task ausführen
cd robots/src/rcc/my-robot
robot --task TaskName tasks.robot

# Alle Tasks
robot tasks.robot

# Mit RCC (wie im Production-System)
rcc robot run --task TaskName

# Outputs checken
open output/log.html
```

### Best Practices für Robot-Entwicklung

1. **Klare Task-Namen** - Sprechende Namen in robot.yaml
2. **Fehlerbehandlung** - Run Keyword If und Error Handling
3. **Logging** - Ausreichend Log-Ausgaben für Debugging
4. **Modularisierung** - Keywords für wiederverwendbaren Code
5. **Locators separat** - locators.json für Wartbarkeit
6. **Timeouts** - Explizite Timeouts für Stabilität
7. **Screenshots** - Bei Fehlern für Debugging

---

## 📦 Studio-Erweiterung

Die Studio-Erweiterung ermöglicht die grafische Konfiguration von Robot-Agents und Tasks in der 5Minds Studio IDE.

### Features

- **Robot Service Type Registration** - "Robot" als Task-Typ in BPMN
- **Agent Management** - Verwaltung von Robot-Agent-Instanzen
- **Topic Selection** - Auswahl des auszuführenden Robots
- **Visual Feedback** - Robot-Icon auf BPMN-Diagrammen
- **Properties Panel** - Konfiguration im Studio

### Installation in Studio

```bash
cd studio_extension

# Abhängigkeiten installieren
npm ci

# Build erstellen
npm run build

# Installation per npm-Script (muss in studio_extension/package.json konfiguriert sein)
npm run install_studio_extension
```

### Manuelle Installation

1. Studio öffnen: `5minds-studio`
2. Menü: Settings → Extensions
3. "processcube.robot.extension" auswählen
4. Path zum `studio_extension/out/index.js` angeben
5. Studio neu starten

### Verwendung in Studio

#### 1. Agent konfigurieren

1. Studio: Menü → Settings → "Configure Robot Agents"
2. Agent hinzufügen:
   ```json
   {
     "name": "Local Robot Agent",
     "url": "http://localhost:42042",
     "uuid": "robot-agent-001"
   }
   ```
3. Speichern in `~/.processcube/robot-agent/agents.json`

#### 2. Robot Task in BPMN erstellen

1. BPMN-Editor öffnen
2. Service-Task hinzufügen
3. Properties → Type: "Robot" wählen
4. Properties → Agent: Konfigurierter Agent wählen
5. Properties → Topic: Verfügbaren Robot aus Liste wählen
   - `rcc/webui`
   - `rcc/windows/ui`
   - etc.

#### 3. Work Items konfigurieren

```javascript
// Task Properties im BPMN
{
  "taskConfig": {
    "agent": "robot-agent-001",
    "topic": "rcc/webui",
    "timeout": 300,
    "retry": 3
  }
}
```

### Studio-Erweiterung Entwicklung

#### Komponenten

- **PropertiesRobotTaskPane.tsx** - Haupt-UI für Robot-Tasks
- **PropertiesRobotTaskPaneContent.tsx** - Task-Eigenschaften
- **RobotAgentsConfigEditor.tsx** - Agent-Verwaltung UI

#### Debugging

```bash
# Studio mit Erweiterungs-Dev-Mode starten
5minds-studio --extension-development-dir=./studio_extension

# VSCode Debugger: F5 zum Debuggen des TypeScript
```

#### Build & Release

```bash
# Development Build
npm run build

# Outputs als studio_extension/out/index.js

# Für Beta
npm run copy_release_to_beta
```

---

## 🔌 API-Dokumentation

### REST API Endpoints

#### Robot-Liste abrufen

```
GET /robot_agents/robots
```

**Response:**
```json
{
  "topics": [
    {
      "name": "webui",
      "topic": "rcc/webui"
    },
    {
      "name": "windows/ui",
      "topic": "rcc/windows/ui"
    }
  ]
}
```

**cURL Beispiel:**
```bash
curl -X GET http://localhost:42042/robot_agents/robots
```

### ProcessCube External Task Integration

Der Agent registriert sich bei ProcessCube als External Task Subscriber:

```python
# Beispiel Task-Ausführung
task_handler.execute(
    payload={
        "order_id": "ORD-123",
        "customer": "Acme"
    },
    task={
        "id": "task-123",
        "topic": "rcc/webui"
    }
)
```

### Fehler-Responses

```json
{
  "error": {
    "code": "unwrap_failed",
    "message": "Failed to unwrap robot package",
    "details": {
      "return_code": 1,
      "robot_path": "robots/installed/rcc/webui.zip"
    }
  }
}
```

---

## 🔧 Entwicklung & Debugging

### Projekt-Setup für Entwicklung

```bash
# 1. Repository klonen
git clone <repo-url>
cd processcube-robot-agent

# 2. Python venv erstellen
python -m venv venv
source venv/bin/activate  # Linux/macOS
# oder
venv\Scripts\activate  # Windows

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. RCC prüfen
rcc version
```

### Service mit Debug-Modus starten

```bash
# Debug-Modus in config.dev.json aktivieren:
{
  "debugging": {
    "enabled": true,
    "hostname": "localhost",
    "port": 5678,
    "wait_for_client": true
  }
}

# Service starten
npm run processcube_robot_agent

# Debugger verbinden (PyCharm/VSCode)
# Verbinden auf localhost:5678
```

### Logging & Debugging

#### Console Logging aktivieren

```python
# In processcube_robot_agent/__main__.py
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

#### Log-Ausgaben nachverfolgen

```bash
# Service mit verbose Output
LOG_LEVEL=DEBUG npm run processcube_robot_agent

# RCC Debug-Output
RCC_DEBUG=true npm run processcube_robot_agent

# Service Logs live folgen
tail -f ~/.processcube/robot-agent/logs.txt
```

### Watch Mode für Entwicklung

Mit automatischem Reload bei Dateiänderungen:

```bash
# config.dev.json:
{
  "rcc": {
    "start_watch_project_dir": true,
    "project_dir": "robots/src/rcc"
  }
}

# Service starten - ändert einen Robot und beobachte Auto-Reload
npm run processcube_robot_agent
```

Dateiänderungen werden erkannt:
- Neue robot.yaml → Robot wird gepackt und registriert
- Geänderte robot.yaml → Neupacken und Neuregistrierung
- Neue tasks.robot → Repack automatisch

### Manuelles Testen

```bash
# 1. Robot lokal testen
cd robots/src/rcc/webui
robot --task WebUIExample tasks.robot

# 2. Robot mit RCC packen
rcc robot wrap -z robots/src/rcc/webui

# 3. Robot auspacken und inspizieren
rcc robot unwrap -z robots/installed/rcc/webui.zip -d temp/webui

# 4. Mit RCC ausführen
rcc run -c robots/src/rcc/webui
```

### Unit Testing hinzufügen

```bash
# Abhängigkeiten
pip install pytest pytest-asyncio pytest-cov

# Tests schreiben (noch nicht vorhanden!)
mkdir tests
cat > tests/test_robot_agent.py << 'EOF'
import pytest
from unittest.mock import Mock, patch
from processcube_robot_agent.robot_agent.rcc.robot_agent import RobotAgent

def test_execute_missing_robot():
    agent = RobotAgent()
    with pytest.raises(Exception):
        agent.execute({}, {"task_id": "test"})
EOF

# Tests ausführen
pytest tests/ -v --cov
```

### Typprüfung (mypy)

```bash
# Installation
pip install mypy types-all

# Typprüfung
mypy processcube_robot_agent/

# Mit Konfiguration
cat > mypy.ini << 'EOF'
[mypy]
python_version = 3.9
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
EOF

mypy processcube_robot_agent/
```

---

## ⚠️ Problembehebung

### Service startet nicht

**Problem:** `ModuleNotFoundError: No module named 'processcube_robot_agent'`

```bash
# Lösung 1: PYTHONPATH setzen
export PYTHONPATH=$(pwd)
npm run processcube_robot_agent

# Lösung 2: Abhängigkeiten neu installieren
pip install -r requirements.txt --force-reinstall

# Lösung 3: Virtual Environment verwenden
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
npm run processcube_robot_agent
```

### RCC nicht gefunden

**Problem:** `rcc: command not found`

```bash
# RCC herunterladen
cd /tmp
wget https://github.com/robocorp/rcc/releases/download/v12.x.x/rcc-linux-64bit
chmod +x rcc
sudo mv rcc /usr/local/bin/

# Oder in PATH hinzufügen
export PATH=$PATH:/path/to/rcc/directory

# Überprüfung
rcc version
```

### Robot wird nicht registriert

**Problem:** Robot nach Hinzufügen nicht in der Liste sichtbar

```bash
# 1. Watch-Modus aktiviert?
# config.dev.json: "start_watch_project_dir": true

# 2. Robots manuell packen
npm run pack

# 3. Service neu starten
npm run processcube_robot_agent

# 4. Robots auflisten
curl http://localhost:42042/robot_agents/robots
```

### Fehler im Robot beim Ausführen

**Problem:** Robot schlägt fehl, Output nicht sichtbar

```bash
# 1. Logs anschauen
tail -100 ~/.processcube/robot-agent/logs.txt

# 2. Robot lokal testen
cd robots/src/rcc/mein-robot
robot tasks.robot

# 3. Output überprüfen
open output/log.html

# 4. RCC Output lesen
rcc run -c robots/src/rcc/mein-robot

# 5. Debug-JSON check
cat robots/installed/rcc/mein-robot/output.xml
```

### ProcessCube verbindet sich nicht

**Problem:** Service läuft, aber ProcessCube findet ihn nicht

```bash
# 1. Service-URL prüfen
curl http://localhost:42042/robot_agents/robots
# Sollte erfolgreich sein

# 2. Config überprüfen
cat config.dev.json
# rest_api.host und rest_api.port korrekt?

# 3. Firewall/Netzwerk
# Port 42042 offen von ProcessCube?
netstat -tuln | grep 42042

# 4. ProcessCube Config überprüfen
# ProcessCube sollte konfiguriert sein mit:
# http://<agent-host>:42042
```

### Studio-Erweiterung lädt nicht

**Problem:** "Robot" Task-Type nicht verfügbar in Studio

```bash
# 1. Erweiterung gebaut?
cd studio_extension
npm run build

# 2. out/index.js existiert?
ls -la out/index.js

# 3. Studio Debug-Mode
5minds-studio --extension-development-dir=./studio_extension

# 4. Browser Console prüfen (F12)
# Fehler in Extensions anschauen
```

### Port 42042 bereits in Verwendung

**Problem:** `Address already in use`

```bash
# Prozess finden und beenden
lsof -i :42042
kill -9 <PID>

# Oder anderen Port verwenden
cat config.dev.json | sed 's/42042/42043/' > config.dev.json.new
mv config.dev.json.new config.dev.json
npm run processcube_robot_agent
```

---

## 📊 Analyse & Bekannte Probleme

### Code-Qualität Zusammenfassung

**Aktuelle Status:**
- 28 Probleme identifiziert
- ⚠️ 5 HIGH Severity Issues
- ⚠️ 15 MEDIUM Severity Issues
- ⚠️ 8 LOW Severity Issues

**Kritische Probleme:**
1. **Shell-Injection Anfälligkeit** - `subprocess.run()` mit `shell=True`
2. **Keine Tests** - 0% Test-Coverage
3. **Veraltete Dependencies** - RCC 2.1.0 statt 4.0.0, uvicorn 0.17.5 statt 0.25+
4. **Fehlende Dokumentation** - Nur 3% Docstring-Coverage
5. **Typsicherheit** - Viele fehlende Type Hints

**Verbesserungen in Planung:**
- [ ] Shell-Injection-Lücken schließen
- [ ] Unit Tests hinzufügen (Ziel: 70%+ Coverage)
- [ ] Dependencies aktualisieren
- [ ] Type Hints hinzufügen (Python)
- [ ] Docstrings für alle Public APIs
- [ ] Production-Build für Studio-Erweiterung

Detaillierte Analyse siehe: [ANALYSIS.md](./ANALYSIS.md) (wird separat erstellt)

---

## 📚 Weitere Dokumentation

### Zusammengehörige Komponenten

#### processcube_robot_agent
- Backend-Service mit RPA-Executor
- **Hauptdatei:** `processcube_robot_agent/__main__.py`
- **Dokumentation:** siehe [Processing Robot Agent Details](#robot-entwicklung)

#### robots
- Robot Framework Projekte
- **Struktur:** `robots/src/rcc/`
- **Packaging:** Automatisch via RCC oder `npm run pack`

#### studio_extension
- TypeScript/React IDE-Integration
- **Build:** `npm run build` im `studio_extension/` Verzeichnis
- **Installation:** in 5Minds Studio

---

## 🤝 Contributing

### Bereiche mit Verbesserungsbedarf

1. **Tests schreiben** - `tests/` Verzeichnis aufbauen
2. **Dependencies updaten** - Modern halten
3. **Fehlerbehandlung** - Robustness erhöhen
4. **Dokumentation** - Docstrings ergänzen
5. **Logging** - Debugbarkeit verbessern

### Commit-Konventionen

```bash
# Feature
git commit -m "feat: add robot auto-discovery"

# Bug Fix
git commit -m "fix: shell injection vulnerability in subprocess calls"

# Dokumentation
git commit -m "docs: add testing guide"

# Refactor
git commit -m "refactor: simplify factory builder"

# Tests
git commit -m "test: add unit tests for robot_agent.py"
```

### Pull Request Prozess

1. Fork repository
2. Feature branch erstellen: `git checkout -b feature/amazing-feature`
3. Änderungen committen: `git commit -m "feat: ..."`
4. Branch pushen: `git push origin feature/amazing-feature`
5. Pull Request öffnen
6. Tests müssen passen
7. Code-Review durchführen

---

## 📝 Lizenz

MIT License - siehe LICENSE Datei

---

## 🆘 Support & Kontakt

### Fehlermeldung beheben

1. **Logs überprüfen** - siehe [Problembehebung](#-problembehebung)
2. **Einfaches Beispiel** - webui Robot testen
3. **Isolieren** - Problem reproduzieren
4. **GitHub Issue** - https://github.com/5minds/processcube-robot-agent/issues

### Weitere Ressourcen

- **Robot Framework:** https://robotframework.org/
- **RPA Framework:** https://rpaframework.org/
- **ProcessCube:** https://processcube.io/
- **5Minds Studio:** https://docs.5minds.de/
- **Robocorp (RCC):** https://robocorp.com/

---

## 🎓 Beispiele & Tutorials

### Beispiel 1: Web-Login automatisieren

```robot
*** Settings ***
Library    RPA.Browser.Selenium
Library    Collections

*** Variables ***
${BROWSER}    Chrome
${URL}        https://app.example.com

*** Tasks ***
Automated Login
    Open Available Browser    ${URL}    ${BROWSER}
    Input Text    id:username    myuser@example.com
    Input Text    id:password    SecurePassword123
    Click Button    id:login-btn
    Wait Until Page Contains    Dashboard
    Close Browser
```

### Beispiel 2: Datenverarbeitung

```robot
*** Settings ***
Library    RPA.Excel.Files
Library    RPA.HTTP
Library    Collections

*** Tasks ***
Process Excel Data
    Open Workbook    data.xlsx
    ${data}=    Read Worksheet    sheet=Orders    as_table=True
    Close Workbook

    FOR    ${row}    IN    @{data}
        Log    Processing order ${row}[order_id]
        ${status}=    Process Order    ${row}[order_id]    ${row}[customer]
        Log    Order status: ${status}
    END

*** Keywords ***
Process Order
    [Arguments]    ${order_id}    ${customer}
    Log    Custom processing logic here
    RETURN    completed
```

### Beispiel 3: API-Integration

```robot
*** Settings ***
Library    RPA.HTTP
Library    RPA.JSON

*** Tasks ***
Fetch And Process API Data
    ${response}=    Get Request    https://api.example.com/customers
    ${json}=        Evaluate    ${response.text}

    Set Work Item Variable    customer_count    ${json.__len__()}

    FOR    ${customer}    IN    @{json}
        Log    Customer: ${customer}[name]
        Set Work Item Variable    last_customer    ${customer}[name]
    END
```

---

**Dokumentversion:** 1.0
**Letztes Update:** November 2025
**Status:** Production Ready (mit anstehenden Verbesserungen)
