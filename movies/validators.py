import json
from datetime import date

REQUIRED_FIELDS = {"title", "director", "year", "genre"}

class InvalidMovieFile(ValueError):
    pass

def validate_movie(movie):
    if not isinstance(movie, dict):
        raise InvalidMovieFile("Каждый фильм должен быть объектом.")
    if set(movie.keys()) != REQUIRED_FIELDS:
        raise InvalidMovieFile(
            "У фильма должны быть поля: title, director, year, genre."
        )
    for key in ("title", "director", "genre"):
        if not isinstance(movie[key], str) or not movie[key].strip():
            raise InvalidMovieFile(f"Поле {key} должно содержать непустой текст.")
        if len(movie[key].strip()) > {"title": 150, "director": 100, "genre": 60}[key]:
            raise InvalidMovieFile(f"Слишком длинное значение поля {key}.")
    # bool является подклассом int в Python, поэтому проверяем отдельно.
    if isinstance(movie["year"], bool) or not isinstance(movie["year"], int):
        raise InvalidMovieFile("Год выпуска должен быть целым числом.")
    if not 1888 <= movie["year"] <= date.today().year + 5:
        raise InvalidMovieFile("Год выпуска находится вне допустимого диапазона.")
    return {
        "title": movie["title"].strip(),
        "director": movie["director"].strip(),
        "year": movie["year"],
        "genre": movie["genre"].strip(),
    }

def parse_json(raw):
    try:
        data = json.loads(raw.decode("utf-8-sig"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InvalidMovieFile("Файл не является корректным JSON в кодировке UTF-8.") from exc
    # Поддерживается один объект фильма или список фильмов.
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list) or not data:
        raise InvalidMovieFile("JSON должен содержать объект фильма или непустой список.")
    return [validate_movie(item) for item in data]

def parse_movie_file(path):
    raw = path.read_bytes()
    if path.suffix.lower() == ".json":
        return parse_json(raw)
    raise InvalidMovieFile("Разрешены только JSON-файлы.")
