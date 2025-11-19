# Changelog

All notable changes to this project will be documented in this file.

---

## [0.1.2] - 2025-11-19

### 📚 Documentation

**Complete English Translation**
- ✅ Entire README.md translated to English (2070 lines)
- Robot Development section (RCC vs UV comparison, best practices)
- UV Robot Development (Pure Python implementation guide)
- Robot Execution Tools & Entry Points (robot_runner, UV-Runner, RCC-Runner)
- Studio Extension (Configuration, installation, development guide)
- API Documentation (REST endpoints, error responses)
- Development & Debugging (Setup, testing, logging, debugging)
- Troubleshooting (7 common problems with detailed solutions)
- Project Status & Quality metrics
- Contributing guidelines
- Support & Resources
- Examples & Tutorials

**Release Readiness**
- All content consistently in English for international audience
- Production-ready documentation for public release
- Single source of truth for all functionality documentation
- Professional English documentation suitable for open-source publication

---

## [0.1.1] - 2025-11-19

### 📚 Documentation

**README.md Modernization**
- Updated test count to 360 (279 Python + 81 TypeScript)
- Added comprehensive UV-Runner / Robot Execution Tools documentation
- Added Docker image configuration & usage guide with examples:
  - Docker build and container startup
  - Docker Compose full stack configuration
  - ghcr.io image tags and versioning
  - Environment variables and mounting options
  - Security best practices (non-root user, read-only filesystem)
  - Development Docker builds
  - Troubleshooting for Docker containers

**Documentation Cleanup**
- Removed outdated ANALYSIS.md (v0.0.1 status documentation)
- Removed outdated IMPROVEMENTS_SUMMARY.md (completed work now in CHANGELOG.md)
- Removed outdated ROADMAP.md (old development plans)
- Removed outdated STUDIO_EXTENSION_TESTS.md (81% → 100% pass rate)
- Removed studio_extension/TYPESCRIPT_MIGRATION_GUIDE.md (migration completed)
- Repository now contains only actively maintained, production-relevant documentation

**License**
- Added Apache 2.0 LICENSE file
- All documentation reflects Apache 2.0 licensing

---

## [0.1.0] - 2025-11-19

### ✨ New Features

**🚀 Release Automation**
- Auto-extract release notes from CHANGELOG.md for GitHub Releases
- Comprehensive release guide (RELEASING.md) with step-by-step instructions
- Python script for parsing CHANGELOG.md versions
- GitHub Actions automatically creates releases with formatted notes

**📖 Documentation Enhancements**
- Added RELEASING.md with complete release workflow
- Release checklist and troubleshooting guide
- Semantic versioning and Keep a Changelog guidelines
- Pre-release version support (alpha, beta, rc)

### 🔧 Improvements

**CI/CD Pipeline**
- Updated GitHub Actions release job to extract notes automatically
- Added Python 3.12 support in release job
- Improved error handling with fallback mechanisms
- Auto-detection of pre-release versions

**Developer Experience**
- Easy release process: Update CHANGELOG → Git tag → Done
- Single source of truth for release notes (CHANGELOG.md)
- Manual testing support: `python scripts/extract_release_notes.py VERSION`

### 📊 Testing & Quality

**Test Coverage Consolidation**
- Python backend: 279 tests (70.67% coverage)
- TypeScript frontend: 81 tests
- Integration tests: 71 tests
- All tests 100% passing

**CI/CD Quality**
- Coverage check properly separated (unit/integration)
- All security checks passing (0 npm vulnerabilities)
- Modern GitHub Actions with latest action versions

---

## [0.0.1] - 2025-11-19

### 🎉 Initial Release

ProcessCube Robot Agent v0.0.1 is the **first production-ready release** of the RPA (Robotic Process Automation) integration solution for ProcessCube workflows.

#### ✨ Major Features

**🔀 Dual Robot Execution Engines**
- **RCC-based Robots** (Robot Framework) - UI automation, web scraping, textual RPA tasks
- **UV-based Robots** (Pure Python) - APIs, data processing, microservices, Python libraries
- Side-by-side execution without migration needed
- Auto-discovery and hot-reload support

**🎯 ProcessCube Integration**
- REST API endpoint for robot discovery (`GET /robot_agents/robots`)
- External Task Handler for ProcessCube workflow integration
- Seamless work item (JSON) payload handling
- Topic-based routing to appropriate robots

**⚙️ Development Features**
- File watcher with hot-reload (auto-pack robots on changes)
- Project discovery and auto-registration
- Configuration management (JSON-based)
- CLI commands: `serve`, `pack`, `watch`
- Debug mode with Python debugger support

**🧩 Studio Extension**
- TypeScript/React IDE extension for 5Minds Studio
- Robot service type registration in BPMN
- Agent management UI
- Visual robot selection in properties panel

#### 🔒 Security

- ✅ Shell injection vulnerabilities fixed (4 critical issues resolved)
- ✅ Subprocess safety hardened with proper argument lists
- ✅ 0 npm audit vulnerabilities
- ✅ Type hints for Python code (85% coverage)
- ✅ Comprehensive error handling

#### 🧪 Quality Assurance

**Test Coverage:**
- 279 Python tests (216 unit + 63 integration)
- 81 TypeScript tests
- **360 total tests, 100% passing**
- **Python coverage: 70.67%** (exceeds 60% requirement)
- **Integration tests: 71 tests covering all critical flows**

**Code Quality:**
- Type hints: 85% coverage
- Docstrings: 90% coverage
- Linting: 0 errors with flake8 + mypy
- Production webpack build: 0 errors

#### 📦 Dependencies

**Updated to latest stable versions:**
- processcube-sdk: 6.0.2a1 (from 3-4.x)
- fastapi: 0.121.0 (from 0.95.x)
- uvicorn: 0.23.2 (with ProcessCube SDK compatibility)
- robotframework: 7.x (from 6.x)
- rpaframework: 31.x (from 16.x - 15 major versions!)
- watchdog: 6.x (improved file monitoring)
- React: 19.2.0 (latest with TypeScript support)
- ESLint: 9.39.0 (modern flat config)

#### 📚 Documentation

- **README.md** (1,700+ lines): Complete setup guide, quick start, deployment
- **ARCHITECTURE.md** (800+ lines): Technical design, component overview
- **PROJECT_STATUS.md** (500+ lines): Quality metrics, testing details
- **QUICK_START.md**: Getting started guide
- **UV_ROBOT_CREATION_GUIDE.md**: Pure Python robot development
- **MIGRATION_GUIDE.md**: Upgrade path from older versions
- **Comprehensive docstrings** in all Python modules

#### 🚀 Deployment Ready

**CI/CD Infrastructure:**
- GitHub Actions workflow with 5 jobs:
  - Python testing (3.11, 3.12)
  - TypeScript testing
  - Security checks (bandit, safety)
  - Integration tests
  - Docker image building

**pyproject.toml Configuration:**
- Modern Python project metadata
- UV support for isolated robot environments
- Test coverage enforcement (60% minimum)
- Comprehensive dependencies list

#### ✅ What's Working

| Feature | Status | Notes |
|---------|--------|-------|
| RCC Robot Execution | ✅ Full | Robot Framework, UI automation |
| UV Robot Execution | ✅ Full | Pure Python, APIs, data processing |
| REST API (`/robot_agents/robots`) | ✅ Full | Robot discovery endpoint |
| ProcessCube External Tasks | ✅ Full | Seamless workflow integration |
| File Watcher (Hot Reload) | ✅ Full | Auto-pack on file changes |
| Configuration Management | ✅ Full | JSON-based configuration |
| Studio Extension | ✅ Full | Webpack build, Jest tests |
| Work Items (Input/Output) | ✅ Full | JSON payload handling |
| Logging & Debugging | ✅ Full | Comprehensive logging infrastructure |
| Graceful Shutdown | ✅ Full | Clean service termination |

#### ⚠️ Known Limitations

1. **Single-threaded execution** - Robots execute sequentially, not in parallel
2. **Local file system only** - Robots must be on local filesystem
3. **RCC dependency** - RCC tool must be separately installed
4. **No database support** - Robot registry in-memory only
5. **No container isolation** - Robots share Python environment (can be enhanced)

#### 🔄 Recent Improvements (Final Sprint)

- **GitHub Actions modernization:** Updated to use `pyproject.toml` instead of `requirements.txt`
- **Coverage enhancement:** Added 850+ lines of new tests reaching 70.67% coverage
- **CI/CD fixes:** Disabled coverage check in integration tests job (proper separation of concerns)
- **Action updates:** Fixed deprecated `actions/upload-artifact@v3` → `@v4`
- **Entry points:** Clean entry-point-only robot execution without main.py boilerplate

#### 🛠️ Installation

**Quick Setup:**
```bash
# Clone repository
git clone https://github.com/5minds/processcube-robot-agent.git
cd processcube-robot-agent

# Install Python dependencies
pip install -e .[dev]
pip install uv

# Install RCC (if not already installed)
# https://github.com/robocorp/rcc/releases

# Install Studio Extension dependencies
cd studio_extension
npm ci
npm run build
cd ..

# Start the service
npm run processcube_robot_agent

# Service runs on http://localhost:42042
```

**View Available Robots:**
```bash
curl http://localhost:42042/robot_agents/robots
```

#### 📖 Getting Started

1. **Create your first RCC robot** (Robot Framework):
   - See [QUICK_START.md](./QUICK_START.md#creating-your-first-robot)

2. **Create a UV robot** (Pure Python):
   - See [UV_ROBOT_CREATION_GUIDE.md](./UV_ROBOT_CREATION_GUIDE.md)

3. **Integrate with ProcessCube**:
   - Configure agent URL in ProcessCube engine settings
   - Add Robot Service Tasks to your BPMN processes
   - Deploy with Studio Extension

4. **Development & Debugging**:
   - See [README.md - Development & Debugging](./README.md#-entwicklung--debugging)

#### 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](#contributing) for:
- Code standards and commit conventions
- Pull request process
- Testing requirements
- Documentation guidelines

**Areas we'd love help with:**
- Additional integration tests
- Performance optimizations
- Docker/container support
- Enhanced monitoring and metrics
- Additional robot examples

#### 📊 Metrics Summary

| Metric | Value |
|--------|-------|
| **Total Tests** | 360 (216 unit + 63 integration + 81 Jest) |
| **Pass Rate** | 100% |
| **Python Coverage** | 70.67% (exceeds 60% requirement) |
| **Integration Test Coverage** | 71 tests covering all critical flows |
| **Type Hints** | 85% coverage |
| **Docstrings** | 90% coverage |
| **Security Issues** | 0 (fixed 4 critical vulnerabilities) |
| **npm Audit Vulnerabilities** | 0 |
| **Package Updates** | 20 packages modernized |
| **Lines of Documentation** | 3,000+ across 10+ files |

#### 🙏 Acknowledgments

**Technologies Used:**
- ProcessCube SDK for BPM integration
- Robocorp's Robot Framework & RCC for RPA execution
- Python, TypeScript, React for implementations
- FastAPI, uvicorn for REST API
- Jest for testing
- Webpack for bundling

**Team:**
- Built with ❤️ by 5Minds Development Team

#### 📝 License

Apache 2.0 License - See [LICENSE](./LICENSE) for details

#### 🎯 Next Release Goals (0.2.0)

- Parallel robot execution (task queue system)
- Enhanced monitoring and metrics (Prometheus support)
- Container/Docker support
- Distributed robot registry
- Performance optimization
- Extended integration test suite
- API documentation (OpenAPI/Swagger)

---

## How to Report Issues

Found a bug or have a feature request?
- 🐛 **Bugs**: [GitHub Issues](https://github.com/5minds/processcube-robot-agent/issues)
- 💡 **Features**: [GitHub Discussions](https://github.com/5minds/processcube-robot-agent/discussions)
- 📖 **Docs**: Check [README.md](./README.md) and [Troubleshooting](./README.md#-problembehebung) first

---

**Latest Version:** 0.1.2
**Release Date:** November 19, 2025
**Status:** ✅ Production Ready

For more information, see the full [README.md](./README.md) and [PROJECT_STATUS.md](./PROJECT_STATUS.md).