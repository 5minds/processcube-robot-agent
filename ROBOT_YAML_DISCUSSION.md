# robot.yaml Parsing - Diskussion & Empfehlung

## Die Frage

**Warum sollte man `robot.yaml` parsen wenn man die Wrapper-Funktionalität bereits hat?**

Das ist eine sehr gute Frage! Die Antwort ist: **Man braucht es nicht unbedingt.**

## Hintergrund: robot.yaml

`robot.yaml` ist ein **RCC-Konzept**. Es wird von Robocorp RCC verwendet, um:

```yaml
# Beispiel robot.yaml (RCC-Stil)
tasks:
  - name: Task 1
    robot: tests/task1.robot
    variables:
      USERNAME: user123
      PASSWORD: pass456
  
  - name: Task 2
    robot: tests/task2.robot
    variables:
      URL: https://example.com
```

## Zwei Ansätze für Phase 2

### Ansatz A: Ohne robot.yaml Parsing (EMPFOHLEN)
**Einfacher, direkter, weniger Overhead**

```
Input Work Item:
{
  "robot_file": "tests/task1.robot",
  "variables": {"USERNAME": "user123"}
}
  ↓
UV Robot Framework Wrapper
  ↓
Output Work Item
```

**Vorteile:**
- ✅ Einfacher zu implementieren
- ✅ Weniger Code (keine YAML-Parser)
- ✅ Direkter: Input → Execute → Output
- ✅ Vollständige Kontrolle im ProcessCube
- ✅ Bessere Fehlerbehandlung (Python statt YAML)

**Nachteil:**
- ⚠️ Keine direkte RCC-Kompatibilität (aber auch nicht nötig)

### Ansatz B: Mit robot.yaml Parsing
**Komplexer, für RCC-Migration hilfreich**

```
robot.yaml vorhanden?
  ↓
Parser liest Task-Definition
  ↓
Extrahiert: robot_file, variables, etc.
  ↓
Ruft Wrapper auf
```

**Vorteile:**
- ✅ RCC-Kompatibilität
- ✅ Existierende robot.yaml können reused werden

**Nachteile:**
- ⚠️ Zusätzlicher Code & Komplexität
- ⚠️ YAML-Parser nötig
- ⚠️ Zwei Input-Formate (Work Items + robot.yaml)
- ⚠️ Weniger klar wer responsible ist

## Meine Empfehlung

### Phase 2: **Nur Ansatz A implementieren** (ohne robot.yaml)

**Begründung:**

1. **Wrapper ist der "Single Source of Truth"**
   - Work Items enthalten alle Infos
   - Keine versteckte Konfiguration in robot.yaml
   - Besser zu debuggen

2. **ProcessCube ist nicht RCC**
   - ProcessCube hat sein eigenes Task-System
   - robot.yaml ist RCC-spezifisch
   - Wir sollten nicht RCC nachahmen

3. **Einfachheit gewinnt**
   - Weniger Code = weniger Bugs
   - Phase 2 kann in 2-3 Tagen abgeschlossen sein
   - Mit robot.yaml wären es 4-5 Tage

4. **Migration funktioniert auch ohne**
   ```
   RCC robot.yaml:
   - name: Task 1
     robot: tests/task1.robot
     variables: {...}
   
   Wird zu:
   
   ProcessCube Work Item:
   {
     "robot_file": "tests/task1.robot",
     "variables": {...}
   }
   ```

## Phase 2 Plan (überarbeitet)

### Vereinfacht:

1. **Create `UVRobotFrameworkEngine` class**
   - Wrapper aufrufen
   - Error handling

2. **Implement topic routing**
   - Erkenne `uv-rf.*` Topics
   - Route zu Engine

3. **Add tests**
   - Unit tests
   - Integration tests

**Keine robot.yaml Parser nötig!**

## Optional: Phase 3 Enhancement

Wenn sich später rausstellt, dass robot.yaml nützlich wäre:

```python
class UVRobotFrameworkEngine:
    def execute(self, payload):
        # Check if robot.yaml-style config
        if "robot_yaml_path" in payload:
            # Parse robot.yaml and extract variables
            config = self.parse_robot_yaml(payload["robot_yaml_path"])
            payload.update(config)
        
        # Execute wrapper with consolidated payload
        return self.execute_wrapper(payload)
```

Aber das ist **optional für später**, nicht notwendig für Phase 2.

## Zusammenfassung

| Aspekt | Mit robot.yaml | Ohne robot.yaml |
|--------|----------------|-----------------|
| Komplexität | Hoch | Niedrig |
| Implementierungszeit | 4-5 Tage | 2-3 Tage |
| Code-Zeilen | 200+ | 50-80 |
| Debugging | Schwieriger | Einfacher |
| RCC-Kompatibilität | Ja | Nein |
| Notwendig? | Nein | Ja |
| Recommendation | Später (Phase 3) | **Jetzt (Phase 2)** ✅ |

## Aktion

**Für Phase 2: robot.yaml Parsing von der Liste streichen**

Neue Phase 2 Checklist:
- [ ] Create `UVRobotFrameworkEngine` class
- [ ] Implement robot file discovery (simple glob)
- [x] ~~Implement robot.yaml parsing~~ (entfernt)
- [ ] Add topic routing in ProcessCubeRobotAgent
- [ ] Write unit tests for new engine
- [ ] Write integration tests
- [ ] Update ARCHITECTURE.md
- [ ] Create engine documentation

Das reduziert Phase 2 von 2-3 Tagen auf **1-2 Tage** und macht den Code viel sauberer! 🎯
