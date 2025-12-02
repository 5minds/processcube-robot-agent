# ProcessCube Robot Agent - Claude.md

Dieses Dokument hilft Claude Code, schneller und effektiver mit diesem Projekt zu arbeiten.

## Projekt-Übersicht

ProcessCube Robot Agent ist ein Python-basierter Agent-Service, der BPMN-Workflows (ProcessCube Engine) mit RPA-Automatisierungen verbindet. Das Projekt unterstützt zwei verschiedene Robot-Typen:

- **RCC Robots**: Basieren auf Robot Framework, optimal für UI/Web-Automation (über Robocorp RCC CLI)
- **UV Robots**: Reine Python-Skripte, optimal für API-Integration und Datenverarbeitung (über UV Package Manager)

## Architektur

### High-Level Komponenten

```
ProcessCube Engine (BPMN)
    ↓ External Tasks
FastAPI REST Server (Port 42042)
    ├─ External Task Handler
    ├─ MultiRunnerFactoryCreator
    │   ├─ RCC Robot Factory → RCC Robot Agent
    │   └─ UV Robot Factory → UV Robot Agent
    └─ Project Watcher (optional)
```

### Schlüsselkonzepte

1. **Dual-Engine Ansatz**: Zwei separate Robot-Typen (RCC und UV) für unterschiedliche Anwendungsfälle
2. **Factory Pattern**: Automatische Erkennung und Instanziierung von Robots aus ZIP-Packages
3. **Topic-basiertes Routing**: Robots werden über Topics (z.B. "rcc.windows.ui" oder "uv.api-processor") angesprochen
4. **Work Items**: JSON-basierter Payload-Austausch zwischen Engine und Robots
5. **Hot Reload**: Optional automatisches Neu-Packen und Re-Registrieren bei Dateiänderungen

### Wichtige Module

| Modul | Zweck | Wichtige Dateien |
|-------|-------|------------------|
| `processcube_robot_agent/` | Hauptpaket | `__main__.py` (CLI Entry Point) |
| `robot_agent/` | Core Robot Execution | `base_agent.py`, `builder.py` |
| `robot_agent/rcc/` | RCC Robot Implementation | `robot_agent.py`, `rcc_runner.py` |
| `robot_agent/uv/` | UV Robot Implementation | `robot_agent.py`, `uv_runner.py` |
| `external_task/` | ProcessCube Integration | `robot_task_handler.py` |
| `rest_api/` | HTTP API Endpoints | `robots.py`, `health.py` |
| `tools/` | Utilities | `robot_runner.py`, `work_items.py` |

## Verzeichnisstruktur

```
processcube-robot-agent/
├── processcube_robot_agent/          # Hauptpaket
│   ├── __main__.py                   # CLI Entry Point (Typer)
│   ├── commands/                     # CLI Commands
│   │   ├── pack_robots_command.py
│   │   ├── serve_command.py
│   │   └── watch_robots_command.py
│   ├── robot_agent/                  # Robot Agents
│   │   ├── base_agent.py             # Abstract Base
│   │   ├── rcc/                      # RCC Implementation
│   │   └── uv/                       # UV Implementation
│   ├── external_task/                # ProcessCube Bridge
│   ├── rest_api/                     # FastAPI Server
│   └── tools/                        # Shared Utilities
├── robots/
│   ├── src/                          # Source Robots (entwickelt hier)
│   │   ├── rcc/                      # RCC Robot Sources
│   │   └── uv/                       # UV Robot Sources
│   └── installed/                    # Gepackte Robots (ZIP)
│       ├── rcc/                      # RCC Robot ZIPs
│       └── uv/                       # UV Robot ZIPs
├── tests/
│   ├── unit/                         # Unit Tests
│   └── integration/                  # Integration Tests
├── temp/                             # Temporäre Dateien (unwrapped robots)
├── config.dev.json                   # Development Config
├── pyproject.toml                    # Python Package Config
└── architecture-diagram.excalidraw   # Architektur-Diagramm
```

## Konfiguration

### config.dev.json Struktur

```json
{
  "debugging": {
    "enabled": false,
    "hostname": "0.0.0.0",
    "port": 5678,
    "wait_for_client": false
  },
  "engine": {
    "url": "http://localhost:8000"
  },
  "rcc": {
    "topic_prefix": "rcc",
    "wrap_dir": "robots/installed/rcc",
    "unwrap_dir": "temp/robots/rcc/unwrapped",
    "start_watch_project_dir": true,
    "project_dir": "robots/src/rcc"
  },
  "uv": {
    "topic_prefix": "uv",
    "wrap_dir": "robots/installed/uv",
    "unwrap_dir": "temp/robots/uv/unwrapped",
    "start_watch_project_dir": true,
    "project_dir": "robots/src/uv"
  },
  "rest_api": {
    "port": 42042,
    "host": "0.0.0.0"
  }
}
```

## Entwicklungs-Workflows

### 1. Neue Features entwickeln

```bash
# 1. Branch erstellen
git checkout -b feature/neue-feature

# 2. Tests schreiben (TDD)
# - Unit Tests in tests/unit/
# - Integration Tests in tests/integration/

# 3. Code implementieren

# 4. Tests ausführen
pytest

# 5. Code Coverage prüfen
pytest --cov=processcube_robot_agent --cov-report=html
```

### 2. Neuen RCC Robot erstellen

```bash
# 1. Robot in robots/src/rcc/ erstellen
mkdir -p robots/src/rcc/mein-robot
cd robots/src/rcc/mein-robot

# 2. robot.yaml und tasks.robot erstellen
# robot.yaml:
#   tasks:
#     Default:
#       shell: python -m robot --outputdir ./output tasks.robot

# 3. Robot packen
python -m processcube_robot_agent pack

# 4. Startet automatisch mit Topic "rcc.mein-robot"
```

### 3. Neuen UV Robot erstellen

```bash
# 1. Robot in robots/src/uv/ erstellen
mkdir -p robots/src/uv/mein-robot
cd robots/src/uv/mein-robot

# 2. pyproject.toml erstellen
# [project]
# name = "mein-robot"
# [project.scripts]
# robot_runner = "main:main"

# 3. main.py erstellen

# 4. Robot packen
python -m processcube_robot_agent pack

# 5. Startet automatisch mit Topic "uv.mein-robot"
```

### 4. Service lokal starten

```bash
# Development Mode mit Hot Reload
CONFIG_FILE=config.dev.json python -m processcube_robot_agent serve

# Nur Robots packen
python -m processcube_robot_agent pack
```

## Häufige Aufgaben

### Tests ausführen

```bash
# Alle Tests
pytest

# Nur Unit Tests
pytest tests/unit/

# Nur Integration Tests
pytest tests/integration/

# Mit Coverage
pytest --cov=processcube_robot_agent --cov-report=term-missing

# Coverage HTML Report
pytest --cov=processcube_robot_agent --cov-report=html
open htmlcov/index.html
```

### Debugging

```bash
# Mit Debugger starten (wartet auf VSCode)
# In config.dev.json: debugging.enabled = true, wait_for_client = true
CONFIG_FILE=config.dev.json python -m processcube_robot_agent serve

# Logs ansehen
# Logs werden auf stdout ausgegeben
```

### Dependencies verwalten

```bash
# Dependencies installieren
pip install -e .

# Development Dependencies
pip install -e ".[dev]"

# Neue Dependency hinzufügen
# → Bearbeite pyproject.toml [project.dependencies]
pip install -e .
```

## Testing-Strategie

### Unit Tests (tests/unit/)

- **Fokus**: Einzelne Komponenten isoliert testen
- **Mocking**: Externe Dependencies werden gemockt
- **Schnell**: < 1 Sekunde pro Test
- **Beispiele**:
  - `test_rcc_robot_agent.py`: RCC Agent Logik
  - `test_uv_robot_agent.py`: UV Agent Logik
  - `test_work_items.py`: Work Items Handling

### Integration Tests (tests/integration/)

- **Fokus**: Komponenten-Interaktion und End-to-End Flows
- **Mock Engine**: `mock_engine.py` simuliert ProcessCube Engine
- **Langsamer**: ~ 1-5 Sekunden pro Test
- **Beispiele**:
  - `test_robot_execution_integration.py`: Robot Execution Flow
  - `test_external_task_integration.py`: External Task Handling
  - `test_rest_api_integration.py`: REST API Endpoints

### Test Coverage Ziel

- **Minimum**: 60% (requirement für CI/CD)
- **Aktuell**: ~85%
- **Fokus**: Kritische Pfade und Error Handling

## Code-Konventionen

### Python Style

- **PEP 8** konform
- **Black** für Code Formatting (falls konfiguriert)
- **Type Hints** wo sinnvoll

### Namenskonventionen

- **Klassen**: `PascalCase` (z.B. `RobotAgent`, `MultiRunnerFactoryCreator`)
- **Funktionen/Methoden**: `snake_case` (z.B. `execute_robot`, `create_work_items`)
- **Konstanten**: `UPPER_SNAKE_CASE` (z.B. `DEFAULT_PORT`)
- **Private**: Prefix `_` (z.B. `_internal_method`)

### Async/Await

- **ProcessCube SDK** benötigt `asyncio`
- **FastAPI** ist async-native
- **nest-asyncio** wird verwendet für Kompatibilität

### Error Handling

```python
# Verwende RobotError für Robot-spezifische Fehler
from processcube_robot_agent.robot_agent.error import RobotError, RobotErrorCode

try:
    # Robot Logik
    pass
except Exception as e:
    raise RobotError(
        code=RobotErrorCode.EXECUTION_FAILED,
        message="Robot execution failed",
        details={"error": str(e)}
    )
```

## Wichtige Dependencies

### Produktion

- **processcube-sdk** (6.0.2a1): ProcessCube Integration
- **FastAPI** (0.121+): REST API
- **uvicorn** (0.23+): ASGI Server
- **typer** (0.9+): CLI Framework
- **watchdog** (6.0+): File System Monitoring
- **Robot Framework** (7.x): RPA Framework (für RCC)

### Externe Tools (nicht in requirements.txt)

- **RCC**: Robocorp CLI Tool (muss separat installiert werden)
- **UV**: Python Package Manager (muss separat installiert werden)

### Development

- **pytest**: Testing Framework
- **pytest-asyncio**: Async Test Support
- **pytest-cov**: Coverage Reporting

## Git Workflow

### Branches

- **main**: Produktions-Branch (stable)
- **develop**: Development-Branch (default)
- **feature/**: Feature Branches
- **fix/**: Bugfix Branches

### Commits

```bash
# Conventional Commits Format
git commit -m "feat: Add UV robot factory implementation"
git commit -m "fix: Resolve work items parsing error"
git commit -m "test: Add integration tests for robot execution"
git commit -m "docs: Update architecture diagram"
git commit -m "refactor: Simplify robot agent builder"
```

### Pull Requests

- **Base**: `develop` (nicht `main`!)
- **Title**: Beschreibender Titel
- **Description**: Was wurde geändert und warum
- **Tests**: Alle Tests müssen grün sein

## Nützliche Befehle

```bash
# Service starten (Dev Mode)
CONFIG_FILE=config.dev.json python -m processcube_robot_agent serve

# Robots packen
python -m processcube_robot_agent pack

# Tests ausführen
pytest

# Tests mit Coverage
pytest --cov=processcube_robot_agent --cov-report=html

# Git Status
git status

# Git Log (pretty)
git log --oneline --graph --all --decorate

# Branch wechseln
git checkout develop
git checkout -b feature/meine-feature

# Dependencies installieren
pip install -e .
pip install -e ".[dev]"
```

## Troubleshooting

### RCC nicht gefunden

```bash
# RCC muss separat installiert werden
# https://github.com/robocorp/rcc
# macOS/Linux:
curl -o rcc https://downloads.robocorp.com/rcc/releases/latest/macos64/rcc
chmod +x rcc
sudo mv rcc /usr/local/bin/

# Windows:
# Download von https://downloads.robocorp.com/rcc/releases/latest/windows64/rcc.exe
```

### UV nicht gefunden

```bash
# UV muss separat installiert werden
# https://github.com/astral-sh/uv
# macOS/Linux:
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows:
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Port 42042 bereits belegt

```bash
# Ändere Port in config.dev.json
# "rest_api": { "port": 42043 }
```

### ProcessCube Engine nicht erreichbar

```bash
# Prüfe Engine URL in config.dev.json
# "engine": { "url": "http://localhost:8000" }

# Prüfe Engine Status
curl http://localhost:8000/health
```

## API Endpoints

### REST API (Port 42042)

```bash
# Liste aller Robots
GET http://localhost:42042/robot_agents/robots

# Health Check
GET http://localhost:42042/health

# Metrics
GET http://localhost:42042/metrics
```

## Wichtige Hinweise für Claude

### Bei Bug-Fixes

1. **Zuerst Tests lesen**: Verstehe die erwartete Funktionalität
2. **Test schreiben**: Reproduziere den Bug in einem Test
3. **Fix implementieren**: Ändere den Code minimal
4. **Tests ausführen**: Stelle sicher, dass alle Tests grün sind

### Bei neuen Features

1. **Architektur verstehen**: Siehe [architecture-diagram.excalidraw](architecture-diagram.excalidraw)
2. **Factory Pattern beachten**: Neue Robot-Typen über Factories implementieren
3. **Tests zuerst**: TDD Ansatz bevorzugen
4. **Dokumentation aktualisieren**: README.md, CHANGELOG.md, diese Datei

### Bei Refactorings

1. **Tests beibehalten**: Ändern nur wenn nötig
2. **Kleine Schritte**: Ein Refactoring pro Commit
3. **Backwards Compatibility**: Wenn möglich beibehalten
4. **Code Smells**: Keine unused Variables, unnötige Abstractions vermeiden

### Coding Style

- **Keep it simple**: Over-Engineering vermeiden
- **DRY**: Don't Repeat Yourself - aber nicht zu früh abstrahieren
- **YAGNI**: You Aren't Gonna Need It - keine Features für "vielleicht später"
- **Error Handling**: Nur an Systemgrenzen validieren (User Input, External APIs)
- **Type Hints**: Verwenden wo sinnvoll, aber nicht zwingend überall

## Links und Ressourcen

- **ProcessCube**: https://www.processcube.io/
- **Robot Framework**: https://robotframework.org/
- **Robocorp RCC**: https://github.com/robocorp/rcc
- **UV**: https://github.com/astral-sh/uv
- **FastAPI**: https://fastapi.tiangolo.com/

## Version Information

- **Python**: 3.11+
- **processcube-sdk**: 6.0.2a1
- **Robot Framework**: 7.x
- **FastAPI**: 0.121+

---

**Letztes Update**: 2025-12-02
**Projekt Version**: 0.1.2