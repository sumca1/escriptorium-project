#!/usr/bin/env python3
"""
🔍 Get ALL Django URLs from Running Container
==============================================
This script uses Django's URL resolver to get EVERY URL pattern.

Usage:
    docker exec escriptorium_clean-web-1 python /usr/src/app/get_all_django_urls.py
"""

import os
import sys
import json

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'escriptorium.settings')

# Setup Django
import django
django.setup()

from django.urls import get_resolver
from django.urls.resolvers import URLPattern, URLResolver

def get_all_urls(resolver=None, prefix=''):
    """Recursively extract all URL patterns"""
    if resolver is None:
        resolver = get_resolver()
    
    urls = []
    
    for pattern in resolver.url_patterns:
        if isinstance(pattern, URLResolver):
            # It's an include() - recurse into it
            new_prefix = prefix + str(pattern.pattern)
            urls.extend(get_all_urls(pattern, new_prefix))
        elif isinstance(pattern, URLPattern):
            # It's an actual URL pattern
            url = prefix + str(pattern.pattern)
            
            # Clean up the URL
            url = url.replace('^', '').replace('$', '')
            
            # Skip regex patterns that need parameters
            if '<' not in url and '(' not in url:
                # Add leading slash if missing
                if not url.startswith('/'):
                    url = '/' + url
                
                # Skip empty and admin URLs
                if url and url != '/' and not url.startswith('/admin'):
                    urls.append(url)
    
    return urls

def main():
    print("🔍 Extracting all URLs from Django...\n", file=sys.stderr)
    
    all_urls = get_all_urls()
    
    # Deduplicate and sort
    all_urls = sorted(set(all_urls))
    
    print(f"✅ Found {len(all_urls)} unique URLs:\n", file=sys.stderr)
    
    # Categorize
    public = ['/']  # Homepage
    authenticated = []
    
    for url in all_urls:
        if any(keyword in url for keyword in ['login', 'logout', 'signup', 'password', 'register']):
            public.append(url)
        else:
            authenticated.append(url)
    
    print("🌐 PUBLIC PAGES:", file=sys.stderr)
    for url in public:
        print(f"   {url}", file=sys.stderr)
    
    print(f"\n🔒 AUTHENTICATED PAGES:", file=sys.stderr)
    for url in authenticated[:30]:  # First 30
        print(f"   {url}", file=sys.stderr)
    
    if len(authenticated) > 30:
        print(f"   ... and {len(authenticated) - 30} more", file=sys.stderr)
    
    # Output JSON to stdout (for easy capture)
    data = {
        'public': public,
        'authenticated': authenticated,
        'all': all_urls
    }
    
    print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
