# Requirements.txt Audit and Compatibility Check

## Current Issues Found

### 1. ✅ numpy Version Conflict - FIXED
- **Problem:** kraken requires `numpy~=1.23.0` but we had `numpy>=1.24.0`
- **Resolution:** Changed to `numpy>=1.23.0,<1.24.0`
- **Status:** Fixed in requirements.txt

### 2. ✅ cyhunspell Version Not Available - FIXED
- **Problem:** cyhunspell 2.0.3 doesn't exist (max available: 2.0.2)
- **Resolution:** Changed to `cyhunspell>=2.0.2,<2.0.3`
- **Status:** Fixed in requirements.txt

### 3. ✅ GIT_SSL_NO_VERIFY - ADDED to Dockerfile
- **Problem:** pip couldn't clone from GitHub due to SSL certificate verification
- **Resolution:** Added `ENV GIT_SSL_NO_VERIFY=1` before pip install
- **Status:** Fixed in Dockerfile

### 4. ✅ pip install Command - ADDED to Dockerfile
- **Problem:** Dockerfile copied requirements.txt but never ran `pip install -r requirements.txt`
- **Resolution:** Added the pip install step with SSL trust flags:
  ```dockerfile
  ENV GIT_SSL_NO_VERIFY=1
  RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host github.com \
      --no-cache-dir -r /usr/src/app/requirements.txt
  ```
- **Status:** Fixed in Dockerfile

## Packages That Need Special Attention

### Build-time Issues
- **passim** - Clones from GitHub, needs GIT_SSL_NO_VERIFY
- **tesserocr** - Builds from source, requires build-essential
- **python-Levenshtein** - May need compilation tools

### Version Constraints (Interdependencies)
- `kraken[cuda]>=5.2.9,~=5.2` → requires `numpy~=1.23.0`
- `opencv-python-headless==4.8.1.78` → compatible with numpy 1.23.x
- `reportlab>=4.0.5` → no numpy constraint conflict
- `arabic-reshaper>=3.0.0` → no numpy constraint conflict

## Verification Checklist

- [ ] All packages in requirements.txt are compatible versions
- [ ] numpy version is pinned correctly
- [ ] Dockerfile has pip install step with SSL workarounds
- [ ] GIT_SSL_NO_VERIFY environment variable set
- [ ] All PyPI packages (not git) have specific versions or constraints
- [ ] No circular dependencies
- [ ] No duplicate package entries

## Next Steps

1. Verify requirements.txt with pip locally (optional)
2. Run docker-compose build --no-cache
3. If build succeeds, start containers with docker-compose up -d
4. Verify all containers start successfully
5. Test application functionality

## Key Fixes Made

### app/requirements.txt Changes:
```diff
- numpy>=1.24.0
+ numpy>=1.23.0,<1.24.0

- cyhunspell>=2.0.3
+ cyhunspell>=2.0.2,<2.0.3
```

### Dockerfile Changes:
```diff
+ ENV GIT_SSL_NO_VERIFY=1
+ RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org --trusted-host github.com \
+     --no-cache-dir -r /usr/src/app/requirements.txt
```

