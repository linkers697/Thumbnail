import logging
log = logging.getLogger(__name__)

# Dummy no-op function
def _noop(*args, **kwargs):
    return None

# All thumbnail functions replaced with no-op
generate_thumbnail = _noop
create_thumbnail = _noop
make_thumbnail = _noop
get_thumbnail = _noop
build_thumbnail = _noop
generate_cover = _noop
get_cover = _noop

# ✅ CRUCIAL: this fixes call.py import error
def get_thumb(*args, **kwargs):
    return None

def thumbnails_enabled():
    return False
