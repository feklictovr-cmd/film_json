import json
import uuid
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import MovieForm, MovieUploadForm
from .validators import InvalidMovieFile, parse_movie_file, validate_movie

DATA_DIR = Path(settings.MOVIE_FILES_DIR)

def safe_filename(extension):
    # Имя генерируется сервером: имя пользователя никогда не используется как путь.
    return f"{uuid.uuid4().hex}.{extension}"

def write_movie_file(movie, extension="json"):
    filename = safe_filename("json")
    destination = DATA_DIR / filename
    destination.write_text(
        json.dumps(movie, ensure_ascii=False, indent=4),
        encoding="utf-8"
    )
    return filename

def index(request):
    if request.method == "POST":
        form = MovieForm(request.POST)
        if form.is_valid():
            movie = {
                "title": form.cleaned_data["title"],
                "director": form.cleaned_data["director"],
                "year": form.cleaned_data["year"],
                "genre": form.cleaned_data["genre"],
            }
            filename = write_movie_file(movie)
            messages.success(request, f"Фильм сохранён в файл {filename}.")
            return redirect("index")
    else:
        form = MovieForm()
    upload_form = MovieUploadForm()
    movies, file_errors, file_names = [], [], []
    files = sorted(
        [p for p in DATA_DIR.iterdir() if p.is_file() and p.suffix.lower() == ".json"],
        key=lambda p: p.name
    )
    for path in files:
        file_names.append(path.name)
        try:
            movies.extend(parse_movie_file(path))
        except (InvalidMovieFile, OSError) as exc:
            file_errors.append(f"{path.name}: {exc}")
    return render(request, "movies/index.html", {
        "form": form,
        "upload_form": upload_form,
        "movies": movies,
        "file_names": file_names,
        "file_errors": file_errors,
        "files_exist": bool(file_names),
    })

@require_http_methods(["POST"])
def upload_movie_file(request):
    form = MovieUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        for error in form.errors.get("file", []):
            messages.error(request, error)
        return redirect("index")

    uploaded = form.cleaned_data["file"]
    destination = DATA_DIR / safe_filename("json")
    try:
        raw = uploaded.read()
        # Сначала проверяем содержимое, до сохранения на диск.
        from .validators import parse_json
        parse_json(raw)
        destination.write_bytes(raw)
    except (InvalidMovieFile, OSError) as exc:
        # Если файл успел появиться, удаляем его при любой ошибке.
        try:
            destination.unlink(missing_ok=True)
        except OSError:
            pass
        messages.error(request, f"Файл не загружен: {exc}")
    else:
        messages.success(request, "Файл проверен и успешно загружен.")
    return redirect("index")

def download_example(request, extension):
    if extension != "json":
        return redirect("index")
    movie = {
        "title": "Интерстеллар",
        "director": "Кристофер Нолан",
        "year": 2014,
        "genre": "Фантастика",
    }
    content = json.dumps(movie, ensure_ascii=False, indent=4)
    response = HttpResponse(content, content_type="application/json; charset=utf-8")
    response["Content-Disposition"] = 'attachment; filename="example.json"'
    return response
