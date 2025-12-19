# MagikSwipe - AI-Powered Children's Learning App

MagikSwipe is an innovative web application designed for children's learning, powered by artificial intelligence. It allows educators and parents to create personalized thematic universes (animals, space, cars, etc.) and automatically generate multimedia content adapted for children.

## 🌟 Key Features

- **Universe Creation**: Customizable thematic spaces
- **AI Content Generation**: Automatic generation of images, videos, and music
- **Multilingual Support**: Content in French, English, Spanish, Italian, and German
- **Cloud Synchronization**: Backup and sharing via Supabase
- **Modern Web Interface**: Interactive viewer with slideshows
- **Asynchronous Processing**: Jobs system for long-running AI tasks

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Viewer        │────│   Backend       │────│   External      │
│   (Interface)   │    │   (FastAPI)     │    │   Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web UI        │    │   REST API      │    │   Replicate     │
│   (HTML/CSS/JS) │    │   Endpoints     │    │   (AI)          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌─────────────────┐               │
│   SQLite        │    │   Supabase      │◄──────────────┘
│   (Local)       │    │   (Cloud)       │
└─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
/MagikSwipe/
├── backend/                 # FastAPI backend
│   ├── main.py             # API entry point
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   ├── database/           # SQLite models
│   └── tests/              # Unit tests
├── viewer/                  # Web interface
│   ├── index.html          # Main viewer
│   ├── gallery.html        # Content gallery
│   └── js/                 # Frontend scripts
├── docker-compose.yml       # Local deployment
└── README.md               # This file
```

## 🚀 Quick Start

### With Docker (Recommended)

```bash
# Clone and start services
git clone <repository-url>
cd MagikSwipe
docker-compose up --build

# Access the app
open http://localhost:8000  # Backend API + Docs
open http://localhost:3000  # Viewer interface
```

### Local Development

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

#### Viewer Setup
```bash
cd viewer
# Serve with any static server (e.g., Python's built-in)
python -m http.server 3000
```

### Environment Configuration

Create a `.env` file in the backend directory:

```env
# AI Generation (Required for content creation)
REPLICATE_API_TOKEN=r8_xxxxxxxxxxxxxxxxxxxxx

# Cloud Sync (Optional)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJxxxxxxxxxxxxx
```

## 📚 API Endpoints

### Universes Management
- `GET /api/universes` - List universes
- `POST /api/universes` - Create universe
- `GET /api/universes/{slug}` - Get universe details
- `PATCH /api/universes/{slug}` - Update universe
- `DELETE /api/universes/{slug}` - Delete universe

### AI Generation
- `POST /api/generate/{slug}/concepts` - Generate AI concepts
- `POST /api/generate/{slug}/images` - Generate images (async)
- `POST /api/generate/{slug}/videos` - Generate videos (async)
- `POST /api/generate/{slug}/music` - Generate music (async)

### Synchronization
- `POST /api/sync/init` - Initialize from Supabase
- `POST /api/sync/pull/{slug}` - Pull universe from cloud
- `POST /api/sync/push/{slug}` - Push universe to cloud

## 🔧 Development

### Prerequisites
- Python 3.11+
- Node.js (for viewer development)
- Docker & Docker Compose
- Git

### Testing
```bash
cd backend
pytest
```

### Building
```bash
# Backend
cd backend
python -m build --sdist --wheel .

# Full app with Docker
docker-compose build
```

## 📋 Semantic Release Configuration

This project uses semantic-release for automated versioning and changelog generation based on conventional commits.

### Release Branches

- **main**: Produces stable releases
  - Format: v2.0.1, v2.1.0, v3.0.0
  - Triggered by merges from feature branches

### Configuration Details

- **Version Source**: Git tags on main branch
- **Commit Parsing**: Conventional commits
- **Changelog**: Automatically updated in CHANGELOG.md
- **Version Tracking**: Maintained in backend/pyproject.toml
- **Tag Format**: v{version} (e.g., v2.0.1)
- **Scope**: Full repository (backend + viewer)

### Conventional Commits

This project follows [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

#### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding/modifying tests
- `chore`: Maintenance tasks

#### Scopes
- `backend`: Backend-specific changes
- `viewer`: Viewer-specific changes
- `shared`: Cross-cutting changes
- `docs`: Documentation
- `test`: Testing
- `ci`: CI/CD changes

#### Examples
- `feat(backend): add music generation endpoint`
- `fix(viewer): resolve gallery loading issue`
- `chore(shared): update Docker configuration`
- `docs: update API documentation`

### CI/CD Pipeline

The pipeline automates versioning, changelog generation, and releases based on conventional commit messages.

```{mermaid}
flowchart TD
    A[Developer Commits] -->|Push/Merge to main| B[CI Build]
    B --> C[Test Suite]
    C --> D{Tests Pass?}
    D -->|Yes| E[Semantic Release Analysis]
    D -->|No| F[Fail Build]
    E --> G[Version Bump]
    G --> H[Update CHANGELOG.md]
    H --> I[Update pyproject.toml]
    I --> J[Create Git Tag]
    J --> K[GitHub Release]
    K --> L[Deploy to Staging/Prod]
```

### Pipeline Steps

1. **Commit Detection**: Pipeline triggers on pushes/merges to main
2. **Build & Test**: Run tests for backend and viewer
3. **Semantic Analysis**: Analyze commit messages for version bump
4. **Version Determination**: Calculate new version (major.minor.patch)
5. **Changelog Generation**: Update CHANGELOG.md with commit details
6. **Version Update**: Update version in backend/pyproject.toml
7. **Tagging**: Create Git tag (v2.0.1)
8. **Release**: Create GitHub release with changelog
9. **Deployment**: Deploy updated version

## 📖 Documentation

- [Backend API Documentation](backend/README.md)
- [Semantic Release Manual](SEMANTIC_RELEASE_MANUAL.md)
- [Agent Instructions](AGENTS.md)
- [Testing Guide](backend/TESTING_GUIDE.md)

## 🤝 Contributing

1. Create a feature branch from `main`
2. Make changes following conventional commits
3. Test your changes
4. Create a pull request to `main`
5. CI/CD will handle versioning and release on merge

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋 Support

For questions or issues:
- Check the [Semantic Release Manual](SEMANTIC_RELEASE_MANUAL.md)
- Review existing issues on GitHub
- Create a new issue with detailed information