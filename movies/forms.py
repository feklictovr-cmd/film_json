from datetime import date
from django import forms

class MovieForm(forms.Form):
    title = forms.CharField(
        label="Название фильма", max_length=150,
        widget=forms.TextInput(attrs={"placeholder": "Например, Интерстеллар"})
    )
    director = forms.CharField(
        label="Режиссёр", max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Имя режиссёра"})
    )
    year = forms.IntegerField(
        label="Год выпуска", min_value=1888, max_value=date.today().year + 5,
        widget=forms.NumberInput(attrs={"placeholder": "Например, 2014"})
    )
    genre = forms.CharField(
        label="Жанр", max_length=60,
        widget=forms.TextInput(attrs={"placeholder": "Фантастика"})
    )
    export_format = forms.ChoiceField(
        label="Формат файла",
        choices=(("json", "JSON"),)
    )

    def clean_title(self):
        value = self.cleaned_data["title"].strip()
        if not value:
            raise forms.ValidationError("Укажите название фильма.")
        return value

    def clean_director(self):
        value = self.cleaned_data["director"].strip()
        if not value:
            raise forms.ValidationError("Укажите режиссёра.")
        return value

    def clean_genre(self):
        value = self.cleaned_data["genre"].strip()
        if not value:
            raise forms.ValidationError("Укажите жанр.")
        return value


class MovieUploadForm(forms.Form):
    file = forms.FileField(label="Файл JSON")

    def clean_file(self):
        uploaded = self.cleaned_data["file"]
        if uploaded.size > 2 * 1024 * 1024:
            raise forms.ValidationError("Размер файла не должен превышать 2 МБ.")
        name = uploaded.name.lower()
        if not name.endswith(".json"):
            raise forms.ValidationError("Разрешены только файлы .json.")
        return uploaded
