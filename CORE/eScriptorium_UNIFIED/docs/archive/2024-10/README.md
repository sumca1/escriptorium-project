# eScriptorium BiblIA Edition

> **🎯 Quick Start:** See [**EXECUTIVE_SUMMARY.md**](./EXECUTIVE_SUMMARY.md) for project status  
> **📚 Complete Documentation:** See [**DOCUMENTATION_INDEX.md**](./DOCUMENTATION_INDEX.md) - 93 organized files  
> **�️ All Projects:** Browse [**docs/**](./docs/) folder - organized by category

---

## 🚀 What's New in BiblIA Edition?

This is a **customized version** of eScriptorium focused on:
- 🌍 **Full Hebrew Translation** (100%)
- 🔤 **Tesseract OCR Integration** for comparison research
- ⚡ **FastAPI Microservice** for high-performance processing
- 📊 **Analytics Dashboard** for model performance tracking
- 🔍 **Elasticsearch Integration** for advanced search
- 🏗️ **GPU Support** for faster training

**Project Status:** ✅ 53% Complete (8/15 features) | [See Details](./סיכום_סטטוס_22_אוקטובר.md)

---

## 📖 Essential Documentation

### 🎯 Start Here:
- **[📚 Documentation Index](./DOCUMENTATION_INDEX.md)** - Complete list of all 93 documentation files
- **[🗂️ docs/ Folder](./docs/)** - Browse by project category

### 📂 Documentation by Project:
| Project | Files | Quick Link |
|---------|-------|------------|
| � Translation System | 25 | [docs/translation/](./docs/translation/) |
| 🔤 TABA (Hebrew Analysis) | 14 | [docs/taba/](./docs/taba/) |
| ⚡ FastAPI Integration | 12 | [docs/fastapi/](./docs/fastapi/) |
| 🛠️ External OCR Tools | 11 | [docs/external_tools/](./docs/external_tools/) |
| 🎛️ Command Center | 8 | [docs/command_center/](./docs/command_center/) |
| 📊 CERberus (CER Analysis) | 6 | [docs/cerberus/](./docs/cerberus/) |
| 🏗️ Build Manager | 5 | [docs/build_manager/](./docs/build_manager/) |
| 🔌 API Improvements | 5 | [docs/api/](./docs/api/) |
| 📐 SegmOnto Extension | 4 | [docs/segmonto/](./docs/segmonto/) |
| 🔍 Passim + Elasticsearch | 2 | [docs/passim/](./docs/passim/) |

### � Quick Start Guides:
- **[QUICK_START_GUIDE.md](./QUICK_START_GUIDE.md)** - Get running in 2 minutes
- **[BIBLIA_FEATURES_GUIDE.md](./docs/external_tools/BIBLIA_FEATURES_GUIDE.md)** - Unique BiblIA features
- **[FastAPI Quick Start](./docs/fastapi/FASTAPI_QUICK_START.md)** - High-performance API
- **[Translation 5 Layers Guide](./docs/translation/TRANSLATION_5_LAYERS_GUIDE.md)** - Translation system

### �️ For Developers:
- **[DEVELOPMENT_GUIDE.md](./DEVELOPMENT_GUIDE.md)** - Development setup
- **[Build Manager System](./docs/build_manager/BUILD_MANAGER_README.md)** - Automated builds
- **[Command Center](./docs/command_center/CM_README.md)** - Category management
- **[Automation Scripts](./scripts/README.md)** - Build & deployment scripts

---

## 🌟 About eScriptorium

eScriptorium is part of the [Scripta](https://www.psl.eu/en/scripta), [RESILIENCE](https://www.resilience-ri.eu) and [Biblissima+](https://projet.biblissima.fr/) projects, and has received funding from Université PSL and from The European Union's [Horizon 2020 Research and Innovation Programme](https://ec.europa.eu/programmes/horizon2020/en/what-horizon-2020) under Grant Agreement no. 871127, from the Programme d'investissements d'avenir of the [Agence Nationale de Recheche](https://anr.fr/fr/france-2030/france-2030/) under Grant Reference no. ANR-21-ESRE-0005, as well as from other contributors listed below. Its goal is provide researchers in the humanities with an integrated set of tools to transcribe, annotate, translate and publish historical documents.

The eScriptorium app itself is at the 'center'. It is a work in progress but will implement at least automatic transcriptions through kraken, indexation for complex search and filtering, annotation and some simple forms of collaborative working such as sharing and versioning.

## The stack
- nginx
- uwsgi
- [django](https://www.djangoproject.com/)
- [daphne](https://github.com/django/daphne) (channel server for websockets)
- [celery](http://www.celeryproject.org/)
- postgres
- [elasticsearch](https://www.elastic.co/)
- redis (cache, celery broker, other disposable data)
- [kraken](http://kraken.re)
- [docker](https://www.docker.com/) (deployment)


## Install
Two options,
- [install with Docker](https://gitlab.com/scripta/escriptorium/-/wikis/docker-install), or a
- [full local install](https://gitlab.com/scripta/escriptorium/-/wikis/full-install).

eScriptorium needs either Linux, macOS or Windows (with WSL).


## Contributing
See [Contributing to eScriptorium](https://gitlab.com/scripta/escriptorium/-/wikis/contributing).

## Steering Committee

- Daniel Stoekl Ben Ezra (EPHE-PSL, UMR AOROC 8546)
- Peter Stokes (EPHE-PSL, UMR AOROC 8546)
- Benjamin Kiessling (EPHE-PSL, UMR AOROC 8546)
- Robin Tissot (EPHE-PSL, UMR AOROC 8546)
- Mathew Barber (Aga Khan University, Institute for the Study of Muslim Civilisations)
- David Smith (Northeastern University)
- Thibault Clérice (Inria)
- Hassen Aguili (Inria)

## Current financial and technical contributors include:
- [École Pratique des Hautes Études (EPHE)](https://www.ephe.psl.eu)
- [Biblissima+](https://projet.biblissima.fr/)
- [Resilience](https://www.resilience-ri.eu/)
- [PSL Scripta](https://scripta.psl.eu/en/)
- [Institut national de recherche en sciences et technologies du numérique (INRIA)](https://inria.fr/en)
- [Archives nationales de France](https://www.archives-nationales.culture.gouv.fr/)
- [L’Institut de recherche et d’histoire des textes](https://www.irht.cnrs.fr/)
- [Open Islamicate Texts Initiative (OpenITI)](https://openiti.org/)
- [The Andrew W. Mellon Foundation](https://mellon.org/grants/)
