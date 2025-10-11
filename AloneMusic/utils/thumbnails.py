# AloneMusic/utils/thumbnails.py
"""
Thumbnail generation DISABLED (performance mode).
This file preserves the public API used by the bot but does NO image processing.
All functions return None (meaning: no thumbnail generated).
If your code expects a path/bytes, update callers to handle None (examples below).
"""

import logging
log = logging.getLogger(__name__)

def _noop(*args, **kwargs):
    # Thumbnailing disabled intentionally to save CPU / I/O
    return None

# Common function names used by various forks — keep them to avoid ImportError
generate_thumbnail = _noop
create_thumbnail = _noop
make_thumbnail = _noop
get_thumbnail = _noop
build_thumbnail = _noop
generate_cover = _noop
get_cover = _noop

def thumbnails_enabled():
    """Return False to indicate feature is disabled."""
    return False
