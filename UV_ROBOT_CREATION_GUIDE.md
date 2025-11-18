# UV-basierte Robot erstellen - Schritt-für-Schritt Anleitung

Diese Anleitung zeigt dir, wie du einen neuen UV-basierten Robot für das ProcessCube Robot Agent System erstellst.

## Überblick

UV ist ein moderner Python Package Manager (20-40x schneller als pip), der für ProcessCube Robots verwendet wird. Ein UV-Robot besteht aus:

- **main.py** - Das Robot-Skript mit der Hauptlogik
- **pyproject.toml** - Konfiguration mit Abhängigkeiten
- **uv.lock** - Lock-Datei für reproduzierbare Installationen
- **README.md** (optional) - Dokumentation

## Schritt 1: Robot-Verzeichnis erstellen

Erstelle ein neues Verzeichnis für deinen Robot im `robots/src/uv/` Ordner:

```bash
mkdir -p robots/src/uv/mein-neuer-robot
cd robots/src/uv/mein-neuer-robot
```

## Schritt 2: pyproject.toml erstellen

Erstelle eine `pyproject.toml` Datei mit der Grundkonfiguration:

```toml
[project]
name = "mein-neuer-robot"
version = "0.1.0"
description = "Beschreibung meines Robots"
requires-python = ">=3.11"
dependencies = [
    "robocorp-workitems>=1.0.0",
]
```

### Wichtig: Keine [build-system] Section!

Script-basierte Robots brauchen **KEINE** `[build-system]` Section. Diese ist nur für Python Pakete notwendig, die gebaut werden sollen. Mit `[build-system]` versucht UV, deinen Robot als Wheel zu bauen, was fehlschlägt.

❌ **FALSCH:**
```toml
[build-system]
requires = ["flit_core"]
build-backend = "flit_core.buildapi"
```

✅ **RICHTIG:**
```toml
[project]
name = "mein-neuer-robot"
version = "0.1.0"
# ... dependencies ...
# KEINE [build-system] Section!
```

## Schritt 3: main.py erstellen

Erstelle die Hauptdatei `main.py` mit deiner Robot-Logik:

```python
"""Beschreibung deines Robots."""

import json
import logging
from typing import Any, Dict

from robocorp.workitems import inputs, outputs

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def process_data(input_data: Dict[str, Any]) -> Dict[str, Any]:
    """Verarbeite die Eingabedaten.

    Args:
        input_data: Eingabe-Payload vom Work Item

    Returns:
        Dictionary mit Verarbeitungsergebnis
    """
    logger.info(f"Verarbeite Input: {input_data}")

    # Hier kommt deine Geschäftslogik hin
    result = {
        "original_input": input_data,
        "processed": True,
        "status": "completed"
    }

    logger.info(f"Output: {result}")
    return result


def main():
    """Haupteinstiegspunkt für den Robot.

    Liest Input Work Items, verarbeitet sie und schreibt Output Work Items.
    """
    logger.info("Robot gestartet")

    try:
        logger.info("Lese Input Work Items...")

        # In robocorp.workitems >= 1.0: durch inputs iterieren
        for input_item in inputs:
            payload = input_item.payload
            logger.info(f"Erhalten: {payload}")

            # Verarbeite die Daten
            result = process_data(payload)

            # Schreibe Output Work Item
            logger.info("Schreibe Output Work Item...")
            output_item = outputs.create(result)
            output_item.save()

        logger.info("Robot erfolgreich abgeschlossen")

    except Exception as e:
        logger.error(f"Fehler während Ausführung: {e}", exc_info=True)
        # Optional: Fehlerexit erstellen
        error_output = {
            "error": str(e),
            "status": "failed"
        }
        try:
            output_item = outputs.create(error_output)
            output_item.save()
        except Exception as output_error:
            logger.error(f"Fehler beim Schreiben: {output_error}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
```

## Schritt 4: uv.lock generieren

Generiere die Lock-Datei für reproduzierbare Installationen:

```bash
cd robots/src/uv/mein-neuer-robot
uv lock --upgrade
```

Dies erstellt eine `uv.lock` Datei mit den genauen Versionen aller Abhängigkeiten.

## Schritt 5: Robot testen (lokal)

Du kannst deinen Robot lokal testen:

```bash
# Virtuelle Umgebung erstellen
uv venv .venv

# Abhängigkeiten installieren
uv pip install -p .venv/bin/python robocorp-workitems>=1.0.0

# Robot ausführen
uv run -p .venv/bin/python main.py
```

## Schritt 6: Robot verpacken

Nachdem dein Robot fertig getestet ist, kann er vom System automatisch verpackt werden:

```bash
cd processcube-robot-agent
python -m processcube_robot_agent pack_robots_command
```

Dies erstellt automatisch eine ZIP-Datei in `robots/installed/uv/mein-neuer-robot.zip`.

Alternativ kannst du auch manuell packen:

```bash
cd robots/src/uv/mein-neuer-robot
zip -r ../../installed/uv/mein-neuer-robot.zip \
    main.py pyproject.toml uv.lock README.md \
    --exclude ".venv/*" ".git/*" "__pycache__/*" "*.pyc"
```

## Schritt 7: Robot im ProcessCube registrieren

Das System erkennt deinen Robot automatisch basierend auf seiner ZIP-Datei. Der Robot wird verfügbar unter dem Topic:

```
uv.mein-neuer-robot
```

Du kannst die verfügbaren Robots über die REST API abrufen:

```bash
curl http://localhost:8000/api/robot_agents/robots
```

Antwort:
```json
{
  "topics": [
    {
      "name": "example-python-robot",
      "topic": "uv.example-python-robot"
    },
    {
      "name": "mein-neuer-robot",
      "topic": "uv.mein-neuer-robot"
    }
  ]
}
```

## Abhängigkeiten hinzufügen

Um weitere Python-Abhängigkeiten hinzuzufügen, bearbeite `pyproject.toml`:

```toml
[project]
name = "mein-neuer-robot"
version = "0.1.0"
description = "..."
requires-python = ">=3.11"
dependencies = [
    "robocorp-workitems>=1.0.0",
    "requests>=2.28.0",
    "beautifulsoup4>=4.11.0",
    "pandas>=1.5.0",
]
```

Dann regeneriere die Lock-Datei:

```bash
uv lock --upgrade
```

## Work Items API Referenz

### Inputs lesen

```python
from robocorp.workitems import inputs

for item in inputs:
    payload = item.payload  # Dictionary mit den Daten
    print(payload)
```

### Outputs schreiben

```python
from robocorp.workitems import outputs

output_data = {
    "result": "success",
    "data": "meine daten"
}

output_item = outputs.create(output_data)
output_item.save()
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

logger.info("Informationsnachricht")
logger.warning("Warnung")
logger.error("Fehler", exc_info=True)
```

## Beispiel-Robots

### 1. Einfacher Echo Robot

```python
from robocorp.workitems import inputs, outputs

def main():
    for item in inputs:
        result = {
            "echo": item.payload,
            "processed": True
        }
        outputs.create(result).save()

if __name__ == "__main__":
    main()
```

### 2. Daten-Transformations Robot

```python
from robocorp.workitems import inputs, outputs
import json

def transform_data(data):
    """Transformiere Daten in Großbuchstaben."""
    return {
        "original": data,
        "transformed": {k: v.upper() if isinstance(v, str) else v
                        for k, v in data.items()}
    }

def main():
    for item in inputs:
        result = transform_data(item.payload)
        outputs.create(result).save()

if __name__ == "__main__":
    main()
```

### 3. Fehlerbehandlung Robot

```python
from robocorp.workitems import inputs, outputs
import logging

logger = logging.getLogger(__name__)

def main():
    for item in inputs:
        try:
            # Verarbeitung
            if "required_field" not in item.payload:
                raise ValueError("required_field fehlt")

            result = {
                "status": "success",
                "data": item.payload
            }
            outputs.create(result).save()

        except Exception as e:
            logger.error(f"Fehler: {e}")
            error_result = {
                "status": "error",
                "error": str(e)
            }
            outputs.create(error_result).save()

if __name__ == "__main__":
    main()
```

## Fehlerbehebung

### Problem: "main.py not found"
**Lösung:** Stelle sicher, dass `main.py` im Root-Verzeichnis liegt (nicht in einem Unterverzeichnis).

### Problem: "Failed to build example-python-robot"
**Lösung:** Entferne jede `[build-system]` Section aus `pyproject.toml`. Script-basierte Robots brauchen dies nicht.

### Problem: "AttributeError: 'Inputs' object has no attribute 'get'"
**Lösung:** Du verwendest die alte robocorp.workitems API. Nutze `for item in inputs:` statt `inputs.get()`.

### Problem: "ModuleNotFoundError: No module named 'xyz'"
**Lösung:** Füge die Abhängigkeit zu `pyproject.toml` hinzu und regeneriere `uv.lock`:
```bash
# Bearbeite pyproject.toml
uv lock --upgrade
```

### Problem: Robot lädt zu lange
**Lösung:** Überprüfe die Abhängigkeiten. Jede zusätzliche Abhängigkeit erhöht die Installationszeit. Entferne unnötige Dependencies.

## Best Practices

1. **Immer Logging verwenden** - Hilft bei der Fehlerbehebung
2. **Fehlerbehandlung implementieren** - Verwende try/except blocks
3. **Kleine, fokussierte Robots** - Ein Robot = eine Aufgabe
4. **Abhängigkeiten minimieren** - Nur notwendige Packages hinzufügen
5. **README.md dokumentieren** - Erkläre, was der Robot tut
6. **Lokal testen** - Bevor du in ProcessCube deployst
7. **Versionen aktualisieren** - Regelmäßig Dependencies updaten

## UV-spezifische Features nutzen

### Schnelle Installation
```bash
# UV ist 20-40x schneller als pip
uv pip install robocorp-workitems
```

### Deterministische Builds
```bash
# uv.lock garantiert, dass alle Umgebungen identisch sind
uv lock
```

### Optionale Dependencies
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "black>=22.0",
]
```

Dann installieren mit:
```bash
uv pip install -p .venv/bin/python ".[dev]"
```

## Nächste Schritte

1. Erstelle dein Robot-Verzeichnis
2. Schreibe `pyproject.toml` und `main.py`
3. Generiere `uv.lock`
4. Teste lokal
5. Verpacke den Robot
6. Deployiere in ProcessCube
7. Überwache die Logs

Viel Erfolg beim Erstellen deiner UV-basierten Robots!