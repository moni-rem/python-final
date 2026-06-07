import mimetypes
from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.http import FileResponse, Http404


def _safe_file_response(base_dir: Path, path: str) -> FileResponse | None:
    file_path = (base_dir / path).resolve()
    try:
        file_path.relative_to(base_dir.resolve())
    except ValueError:
        return None
    if not file_path.is_file():
        return None
    content_type, _ = mimetypes.guess_type(file_path)
    return FileResponse(
        file_path.open('rb'),
        content_type=content_type or 'application/octet-stream',
    )


def serve_static(request, path):
    """Serve static assets directly from disk when collectstatic did not run."""
    for root in (Path(settings.STATIC_ROOT), Path(settings.BASE_DIR) / 'static'):
        response = _safe_file_response(root, path)
        if response is not None:
            return response

    found = finders.find(path)
    if found:
        found_path = Path(found)
        content_type, _ = mimetypes.guess_type(found_path)
        return FileResponse(
            found_path.open('rb'),
            content_type=content_type or 'application/octet-stream',
        )

    raise Http404('Static file not found')
