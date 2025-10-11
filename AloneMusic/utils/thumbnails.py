# AloneMusic/utils/thumbnails.py
import logging
log = logging.getLogger(__name__)

def _noop(*args, **kwargs):
    return None

generate_thumbnail = _noop
create_thumbnail = _noop
make_thumbnail = _noop
get_thumbnail = _noop
build_thumbnail = _noop
generate_cover = _noop
get_cover = _noop

def thumbnails_enabled():
    return False
