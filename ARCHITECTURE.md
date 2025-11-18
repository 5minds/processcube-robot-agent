# ProcessCube Robot Agent - Architecture

> Technische Architektur und Systemdesign

---

## 🏛️ System-Übersicht

```
┌─────────────────────────────────────────────────────────────────┐
│                     ProcessCube Engine (BPMN)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                   External Task Events
                             │
┌────────────────────────────▼────────────────────────────────────┐
│              Robot Agent Service (Python)                       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ REST API (FastAPI)                                       │  │
│  │ - GET /robot_agents/robots                               │  │
│  │ - Health checks & status                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ External Task Handler                                    │  │
│  │ - Subscribes to ProcessCube topics                       │  │
│  │ - Routes tasks to appropriate robots                     │  │
│  │ - Handles task results                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Robot Task Handler Factory                               │  │
│  │ - Discovers available robots (.zip packages)             │  │
│  │ - Creates topic → robot mappings                         │  │
│  │ - Auto-updates on file changes (watch mode)              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Robot Execution Engines                                  │  │
│  │ ├─ RCC Engine (Robot Framework)                         │  │
│  │ │  ├─ Unpacks robot.zip                                 │  │
│  │ │  ├─ Executes via 'rcc run' command                    │  │
│  │ │  └─ Best for: UI Automation, Web-Scraping             │  │
│  │ │                                                        │  │
│  │ └─ UV Engine (Pure Python)                              │  │
│  │    ├─ Unpacks robot.zip                                 │  │
│  │    ├─ Executes via 'uv run python main.py'              │  │
│  │    └─ Best for: APIs, Data Processing, Microservices    │  │
│  │                                                          │  │
│  │ Common:                                                 │  │
│  │ - Prepares work items (JSON)                            │  │
│  │ - Extracts output/results                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Project Watcher & Packer                                 │  │
│  │ - Monitors robots/src/rcc/ and robots/src/uv/            │  │
│  │ - Auto-packs modified robots (both RCC & UV)            │  │
│  │ - Re-registers topics on change                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
         ▼                   ▼                   ▼
    ┌─────────────┐  ┌──────────────┐  ┌──────────┐
    │ RCC/UV CLI  │  │ Work Items   │  │ Env Mgmt │
    │ (Pack, Run) │  │ (JSON)       │  │(Conda/UV)│
    └─────────────┘  └──────────────┘  └──────────┘
```

---

## 📦 Komponenten-Architektur

### 1. Entry Point: `processcube_robot_agent/__main__.py`

**Verantwortung:** CLI-Interface und Service-Start

```python
# Kommandos:
# - serve: Startet REST API + External Task Handler
# - pack: Packt alle Robots
# - watch: Überwacht robot directory für Änderungen
```

**Initialisierung:**
1. Config laden
2. Logging einrichten
3. Python Debugger starten (optional)
4. CLI-Kommando ausführen

---

### 2. REST API: `rest_api_command.py` & `rest_api/`

**Port:** 42042 (konfigurierbar)
**Framework:** FastAPI + uvicorn

#### Endpoints

```python
# GET /robot_agents/robots
# Returns: {"topics": [{"name": "...", "topic": "..."}]}
```

**Architektur:**
```
FastAPI App
    ├── /robot_agents/robots (GET)
    │   └── RobotTaskHandlerFactoryCreator.get_all_robots()
    │       └── Scans robots/installed/rcc/*.zip
    │           └── Returns registered topics
    │
    └── Health Checks
        └── Service status
```

**Flow:**
```
HTTP Request
    ↓
FastAPI Route Handler
    ↓
Builder Factory
    ↓
Scan zip packages
    ↓
Return topic mappings
    ↓
JSON Response
```

---

### 3. External Task Handler: `external_task/`

**Verantwortung:** ProcessCube Integration

**Flow:**
```
ProcessCube Task Event
    ↓
External Task Handler
    ├── Lookup Robot (by topic)
    ├── Load Robot Package
    └── Execute via RobotAgent
        ├── Prepare Input
        ├── Run Robot
        └── Extract Output
    ↓
Return Result to ProcessCube
```

**Implementation:**
```python
class RobotTaskHandler(BaseHandler):
    def execute(self, payload, task):
        # 1. Get robot from topic
        robot_agent = RobotAgent(topic=task['topic'])

        # 2. Execute robot
        result = robot_agent.execute(payload, task)

        # 3. Return result
        return result
```

---

### 4. Robot Execution Engine: `robot_agent/rcc/`

**Zentrale Komponente:** `RobotAgent`

#### Execution Flow

```
RobotAgent.execute(payload, task)
    │
    ├─► Step 1: create_input_data(payload)
    │   └─ Convert dict → JSON work items
    │
    ├─► Step 2: unwrap(robot_zip)
    │   └─ Extract zip to temp directory
    │       └─ Validate robot.yaml exists
    │
    ├─► Step 3: run_robot(unwrapped_dir)
    │   └─ Execute: rcc run -c <dir>
    │       └─ Wait for completion
    │       └─ Capture stdout/stderr
    │
    ├─► Step 4: read_output_data(output_dir)
    │   └─ Parse output.xml
    │   └─ Extract work item results
    │
    └─► Return result dict
        └─ Success or error
```

#### Key Methods

```python
class RobotAgent(RobotAgentBase):
    def execute(payload, task) -> Dict
        """Main entry point"""

    def create_input_data(payload) -> Path
        """Prepare JSON work items"""

    def unwrap(robot_path) -> Path
        """Unpack robot.zip using RCC"""

    def run_robot(unwrapped_path) -> Process
        """Execute via 'rcc run'"""

    def read_output_data(output_dir) -> Dict
        """Extract results from output.xml"""
```

---

### 5. Robot Discovery & Registration: `robot_agent/rcc/robot_task_handler_factory.py`

**Verantwortung:** Mapping Topics → Robot Packages

#### Factory Pattern Implementierung

```
RobotTaskHandlerFactoryCreator
    │
    ├─► Scan robots/installed/rcc/*.zip
    │   └─ For each zip:
    │       └─ Create Factory instance
    │
    ├─► Build topic names
    │   └─ "rcc/webui"
    │   └─ "rcc/windows/ui"
    │
    └─► Register with external task client
        └─ Topics → Handler mapping
```

**Topic Building:**
```python
# Example path: robots/installed/rcc/webui.zip
# Topic prefix: "rcc"
# Result topic: "rcc/webui"

# Example path: robots/installed/rcc/windows/ui.zip
# Result topic: "rcc/windows/ui"
```

#### Class Diagram

```
RobotTaskHandlerFactoryCreator
    ├─ _factory_builder: FactoryBuilder
    ├─ _factories: Dict[str, Factory]
    │
    ├─ __init__(wrap_dir, topic_prefix)
    ├─ get_factories() → List[Factory]
    ├─ get_all_topics() → List[str]
    └─ build_external_task_handlers()

Factory
    ├─ robot_path: Path
    ├─ topic: str
    └─ create_handler() → RobotTaskHandler

FactoryBuilder
    └─ build(robot_path) → Factory
```

---

### 6. Project Packing: `robot_agent/rcc/project_packer.py`

**Verantwortung:** Robot-Projektierung und Packaging

```
Input: robots/src/rcc/<project>/
    ├─ robot.yaml
    ├─ tasks.robot
    ├─ conda.yaml
    └─ locators.json

    ↓ (rcc robot wrap)

Output: robots/installed/rcc/<project>.zip
    └─ Complete packaged robot
       ready for execution
```

#### Execution

```python
ProjectPacker:
    ├─ pack_folder(robot_path)
    │   └─ Find robot.yaml
    │   └─ Execute: rcc robot wrap
    │   └─ Output to wrap_dir
    │
    └─ pack_all(source_dir)
        └─ Recursively find all robot.yaml
        └─ Pack each one
```

---

### 7. Hot-Reload Watcher: `robot_agent/rcc/project_watcher.py`

**Verantwortung:** Automatische Neu-Paketierung

```
File System Event (watchdog)
    │
    ├─ File changed in robots/src/rcc/
    │
    ├─► RobotsFileSystemEventHandler.on_any_event()
    │   │
    │   ├─ Find parent robot.yaml
    │   ├─ Pack robot
    │   └─ Register with factory creator
    │
    └─► Factory discovers new/updated robot
        └─ Topics updated automatically
```

**Implementation:**
```python
class RobotsFileSystemEventHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        changed_path = Path(event.src_path)
        robot_yaml_path = find_robot_yaml(changed_path)
        if robot_yaml_path:
            pack_folder(robot_yaml_path)
            factory_creator.reload()  # Re-register topics
```

**Watch Process:**
```
1. Service start mit watch_dir monitoring
2. Datei ändert sich → Watchdog erkennt Event
3. Event → auf robot.yaml prüfen
4. Gefunden → mit RCC packen
5. Neu gepackt → Factory aktualisieren
6. Topics re-registrieren
```

---

### 8. Configuration Management

**Dateiformat:** JSON

**Struktur:**
```json
{
  "debugging": {
    "enabled": boolean,
    "hostname": string,
    "port": integer
  },
  "engine": {
    "url": string
  },
  "rcc": {
    "topic_prefix": string,
    "wrap_dir": string,
    "unwrap_dir": string,
    "start_watch_project_dir": boolean,
    "project_dir": string
  },
  "rest_api": {
    "port": integer,
    "host": string
  }
}
```

**Laden:**
```python
import json
import os

config_file = os.getenv('CONFIG_FILE')
with open(config_file) as f:
    config = json.load(f)
```

---

## 🎨 Data Structures

### Work Items (Input/Output)

**Robot Framework RPA Work Items:**

```python
# Input (from ProcessCube)
{
    "order_id": "ORD-12345",
    "customer": "Acme Corp",
    "items": [
        {"sku": "ITEM-001", "qty": 5}
    ]
}

# In Robot Framework Access:
${order_id}=    Get Work Item Variable    order_id
${customer}=    Get Work Item Variable    customer

# Robot Output:
Set Work Item Variable    status    completed
Set Work Item Variable    result    ${result}

# Output (back to ProcessCube)
{
    "status": "completed",
    "result": {...},
    "error": null
}
```

### Topic Format

```
<topic_prefix>/<robot_path>

Examples:
- rcc/webui
- rcc/windows/ui
- rcc/windows-example-calculator
```

---

## 🔄 Request Flow Example

### Scenario: User startet Robot Task in ProcessCube

```
1. USER ACTION
   └─ Klick "Start Task" in ProcessCube UI

2. PROCESSCUBE
   └─ Event: External Task mit topic="rcc/webui"
       Payload: {"url": "https://example.com"}

3. ROBOT AGENT - External Task Handler
   └─ Listen auf topic="rcc/webui"
   └─ RobotTaskHandler.execute() aufgerufen
       ├─ Payload: {"url": "..."}
       └─ Task: {"id": "task-123", "topic": "rcc/webui"}

4. ROBOT AGENT - RobotAgent
   └─ execute(payload, task)
       ├─ create_input_data(payload)
       │   └─ JSON: {url: "..."}
       ├─ Find robot_path for topic "rcc/webui"
       │   └─ robots/installed/rcc/webui.zip
       ├─ unwrap(webui.zip)
       │   └─ temp/robots/rcc/unwrapped/webui/
       ├─ run_robot(unwrapped_dir)
       │   └─ Execute: rcc run -c temp/robots/rcc/unwrapped/webui/
       │   └─ Robot Framework runs tasks.robot
       │   └─ Output: temp/robots/rcc/unwrapped/webui/output/
       └─ read_output_data(output_dir)
           └─ Parse output.xml
           └─ Extract results

5. RESULT
   └─ {
        "status": "completed",
        "result": {"screenshot": "..."},
        "error": null
      }

6. PROCESSCUBE
   └─ Update Task status
   └─ Continue BPMN process
```

---

## 📊 Design Patterns Used

### 1. Factory Pattern
**Location:** `robot_task_handler_factory.py`
```python
# FactoryBuilder creates Factory instances
# RobotTaskHandlerFactoryCreator manages all factories
factory = factory_builder.build(robot_path)  # Create handler for specific robot
```

### 2. Observer Pattern
**Location:** `project_watcher.py`
```python
# watchdog monitors file system
# FileSystemEventHandler observes changes
# Auto-triggers robot re-packing
observer = Observer()
observer.schedule(event_handler, path)
```

### 3. Adapter Pattern
**Location:** `external_task/robot_task_handler.py`
```python
# Adapts RobotAgent to ProcessCube's BaseHandler interface
class RobotTaskHandler(BaseHandler):
    def execute(self, payload, task):
        return self._robot_agent.execute(payload, task)
```

### 4. Strategy Pattern
**Location:** `robot_agent/base_agent.py`
```python
# Different agent strategies (RCC, direct execution, etc)
class BaseAgent(ABC):
    @abstractmethod
    def execute(self, payload, task): ...

class RobotAgent(BaseAgent):
    def execute(self, payload, task): ...
```

---

## 🔌 Integration Points

### 1. ProcessCube SDK
```python
from processcube_sdk.external_task import ExternalTaskClient
from processcube_sdk.external_task import BaseHandler

# Connects to ProcessCube engine
external_task_client = ExternalTaskClient(
    base_url="http://localhost:56100",
    auth_type="NONE"
)

# Subscribe to topics
external_task_client.subscribe(
    topic="rcc/webui",
    handler=RobotTaskHandler()
)
```

### 2. RCC CLI
```python
import subprocess

# Unwrap robot
subprocess.run([
    "rcc", "robot", "unwrap",
    "-z", robot_path,
    "-d", unwrap_dir,
    "--force"
])

# Run robot
subprocess.run([
    "rcc", "run",
    "-c", unwrapped_dir
])
```

### 3. FastAPI Server
```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/robot_agents/robots")
async def get_robots():
    return factory_creator.get_all_robots()

# Run with uvicorn
uvicorn.run(app, host="0.0.0.0", port=42042)
```

---

## 🧵 Threading & Async

### Async Architecture
```
Main Event Loop (uvicorn/asyncio)
    │
    ├─► HTTP Requests (FastAPI)
    │   └─ Async handlers
    │
    ├─► External Task Processing
    │   └─ Background threads
    │   └─ RobotAgent.execute() blocking
    │
    └─► File Watcher (watchdog)
        └─ Separate observer thread
        └─ Non-blocking events
```

**Note:** RobotAgent.execute() ist **blockierend** (wartet auf rcc run).
Dies ist in Ordnung, da External Task Handler im Thread-Pool läuft.

---

## 🔒 Security Architecture

### Current State
- ⚠️ Shell injection vulnerability in subprocess.run() with shell=True
- ⚠️ No input validation on work items
- ✅ Robot execution isolated in temp directories
- ✅ File permissions restricted by OS

### Recommended Improvements
1. Use subprocess with argument list (no shell=True)
2. Validate work item schema
3. Sandbox robot execution (containers)
4. Secure config management (.env)
5. Input sanitization

---

## 📈 Scalability Considerations

### Current Design
- Single-threaded robot execution (sequential)
- In-memory robot registry
- Local file system for robots

### Scaling Options
1. **Multiple Agent Instances**
   ```bash
   # Run multiple agents on different ports
   CONFIG_FILE=config1.json npm run processcube_robot_agent  # Port 42042
   CONFIG_FILE=config2.json npm run processcube_robot_agent  # Port 42043
   CONFIG_FILE=config3.json npm run processcube_robot_agent  # Port 42044

   # Load balancer in front
   ```

2. **Distributed Robot Registry**
   - Central database for robot metadata
   - Redis/memcached for caching topics
   - API-based discovery

3. **Containerization**
   - Docker container per agent
   - Kubernetes orchestration
   - Resource limits per robot

---

## 🏗️ Extension Points

### Adding New Features

#### 1. Custom Robot Types
```python
# Currently: RCC-based robots
# Could add: Direct Python execution, Docker containers, etc

class CustomAgent(BaseAgent):
    def execute(self, payload, task):
        # Custom logic
        pass
```

#### 2. Alternative Work Item Formats
```python
# Currently: JSON
# Could add: XML, CSV, custom formats

class WorkItemAdapter:
    def convert_from(self, payload): ...
    def convert_to(self, result): ...
```

#### 3. Custom Topic Builders
```python
# Currently: File path based
# Could add: Database lookup, API-based, regex patterns

class TopicBuilder:
    def build_topic(self, robot_path) -> str:
        # Custom logic
        pass
```

---

## 🧪 Testing Architecture

### Current State
- ❌ No unit tests
- ❌ No integration tests
- ❌ No e2e tests

### Recommended Structure
```
tests/
├── unit/
│   ├── test_robot_agent.py
│   ├── test_project_packer.py
│   ├── test_robot_task_handler_factory.py
│   └── test_external_task_handler.py
│
├── integration/
│   ├── test_rcc_integration.py
│   └── test_processcube_integration.py
│
└── e2e/
    ├── test_full_flow.py
    └── test_webui_robot.py
```

---

## 📝 API Contracts

### Input Schema (ProcessCube → Agent)
```python
{
    "taskId": str,
    "topic": str,
    "workItemId": str,
    "variables": {
        # Dynamic payload from ProcessCube
        "key": "value"
    }
}
```

### Output Schema (Agent → ProcessCube)
```python
{
    "success": bool,
    "data": {
        # Robot output
    },
    "error": Optional[str]
}
```

### REST API Schema
```python
# GET /robot_agents/robots
{
    "topics": [
        {
            "name": str,      # Short name
            "topic": str      # Full topic
        }
    ]
}
```

---

## 🎯 Key Architectural Decisions

| Decision | Rationale | Trade-off |
|----------|-----------|-----------|
| RCC for packaging | Robocorp standard, multi-OS | Dependency on RCC |
| Sequential execution | Simplicity | No parallelization |
| JSON config | Human readable | No schema validation |
| File watcher | Hot reload | Complexity |
| FastAPI | Async capable | Extra dependency |
| Subprocess for RCC | Direct execution | Shell injection risk |

---

**Dokumentation Version:** 1.0
**Zuletzt aktualisiert:** November 2025
