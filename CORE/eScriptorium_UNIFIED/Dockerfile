# Frontend build stage
# Using GitHub Container Registry to bypass NetFree blocking
FROM ghcr.io/sumca1/escriptorium-project/node:18-alpine AS frontend

WORKDIR /build
COPY ./front /build
RUN npm install && npm run production

# Pull official base image
FROM registry.gitlab.com/scripta/escriptorium/base:dj-solo

# try to autodetect number of cpus available
# ENV NGINX_WORKER_PROCESSES auto

ARG VERSION_DATE="passthistobuildcmd"
ENV VERSION_DATE=$VERSION_DATE
# Updated to match new COPY location (escriptorium/static/dist)
ENV FRONTEND_DIR=/usr/src/app/escriptorium/static/dist
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

# ============================================
# TESSERACT INSTALLATION - BiblIA Enhancement
# Added: 2025-10-05 for OCR engine comparison
# ============================================

# Install Tesseract OCR and language packs
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-eng \
    tesseract-ocr-heb \
    tesseract-ocr-ara \
    tesseract-ocr-script-arab \
    tesseract-ocr-script-hebr \
    libtesseract-dev \
    libleptonica-dev \
    && rm -rf /var/lib/apt/lists/*

# Set Tesseract data directory
ENV TESSDATA_PREFIX=/usr/share/tesseract-ocr/4.00/tessdata

# Verify Tesseract installation
RUN echo "Tesseract version:" && tesseract --version && \
    echo "Available languages:" && tesseract --list-langs

# ============================================
# END TESSERACT INSTALLATION
# ============================================

# ============================================
# HUNSPELL SPELL CHECKER - BiblIA Error Detection
# Added: 2025-10-20 for automatic error detection
# ============================================

# Install Hunspell and Hebrew dictionaries
RUN apt-get update && apt-get install -y --no-install-recommends \
    hunspell \
    hunspell-he \
    libhunspell-dev \
    && rm -rf /var/lib/apt/lists/*

# Verify Hunspell installation and list available dictionaries
RUN echo "Hunspell version:" && hunspell -v || true && \
    echo "Installed dictionary files:" && ls -la /usr/share/hunspell/ || true

# ============================================
# END HUNSPELL INSTALLATION
# ============================================

# set work directory
# set work directory
WORKDIR /usr/src/app

# ============================================
# OPTIMIZATION: Copy requirements first (rarely changes)
# This enables Docker layer caching:
# If requirements.txt doesn't change, pip install layer is reused
# If only source code changes, Docker skips the pip install step
# This saves significant rebuild time for development
# Added: 2025-10-26
# ============================================
COPY ./app/requirements.txt /usr/src/app/requirements.txt

# ============================================
# INSTALL PYTHON DEPENDENCIES - CRITICAL FIX
# Added: 2025-10-24
# Install all requirements from requirements.txt
# The base image doesn't include all packages (reportlab, arabic-reshaper, etc.)
# Disable SSL verification for pip and git to avoid certificate errors
# ============================================
ENV GIT_SSL_NO_VERIFY=1
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host github.com \
    --no-cache-dir -r /usr/src/app/requirements.txt

# ============================================
# OPTIMIZATION: Copy configuration next (occasionally changes)
# After requirements are installed and cached
# ============================================
COPY ./app/entrypoint.sh /usr/src/app/entrypoint.sh
COPY ./app/manage.py /usr/src/app/manage.py
COPY ./app/uwsgi.ini /usr/src/app/uwsgi.ini

# ============================================
# OPTIMIZATION: Copy source code last (changes frequently)
# By putting this last, Docker reuses the pip layer
# Even if you change app code, pip install doesn't re-run
# This saves most rebuild time during development
# ============================================
COPY ./app/apps /usr/src/app/apps
COPY ./app/escriptorium /usr/src/app/escriptorium
COPY ./app/fastapi_app /usr/src/app/fastapi_app
# NOTE: biblia_templatetags already included in ./app/apps above - no need to copy again!
# REMOVED duplicate: COPY ./app/biblia_templatetags /usr/src/app/apps/biblia_templatetags
# REMOVED: passim_service.py (BiblIA dev tool, not needed in container)
COPY ./app/escriptorium_model_checker.py /usr/src/app/escriptorium_model_checker.py
COPY ./app/templates /usr/src/app/templates
# Copy static files (Django admin, rest_framework, etc.)
# Note: Frontend assets (JS/CSS/images from front/dist) are handled separately below
# Image assets from public/images are collected by Django's collectstatic
COPY ./app/static /usr/src/app/static
COPY ./app/locale /usr/src/app/locale
COPY ./app/homepage /usr/src/app/homepage
COPY ./app/contributors /usr/src/app/contributors

# REMOVED: tools/ directory (doesn't exist, BiblIA dev scripts not needed in container)

# Install gettext for compilemessages (msgfmt binary)
# Required for Django translation compilation (.po → .mo)
RUN apt-get update && apt-get install -y --no-install-recommends gettext && rm -rf /var/lib/apt/lists/*

# Create logs directory for Django logging
RUN mkdir -p /usr/src/app/escriptorium/logs

# Compile translations (generates .mo files from .po)
# This ensures fresh compilation without relying on pre-built .mo files from host
# *.mo files are excluded via .dockerignore to prevent stale copies
RUN python manage.py compilemessages

# Copy public images for collectstatic
# These images (logos, screenshots, favicons) are collected by Django's collectstatic command
# Directory contains 29 files (4.11 MB): almanach_txt.png, escriptorium_hd.png, logos, etc.
COPY ./public/images /usr/src/app/public/images

# Copy frontend assets directly to static/dist for collectstatic
# Changed from: /usr/src/app/front (not in STATICFILES_DIRS)
# To: /usr/src/app/escriptorium/static/dist (included in STATICFILES_DIRS)
# This ensures CSS/JS files are found by collectstatic automatically
COPY --from=frontend /build/dist /usr/src/app/escriptorium/static/dist

# run entrypoint.sh
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
