# app\seed.py
from . import crud


def seed_data() -> None:
    # Если уже есть приглашения — не пересевать
    invites = crud.list_invitations()
    if invites:
        return

    # Создать тестовые приглашения
    sample = [
        ("Иван и Мария", "Будем рады видеть вас на свадьбе!"),
        ("Семья Петровых", "Приглашаем с большой радостью."),
        ("Сергей", "Будем рады вашему присутствию."),
    ]
    for name, text in sample:
        crud.create_invitation(name, text)

    # Добавить несколько пунктов программы
    program = [
        ("14:00", "Сбор гостей"),
        ("15:00", "Церемония"),
        ("16:00", "Банкет"),
        ("20:00", "Торт"),
        ("22:00", "Завершение вечера"),
    ]
    for idx, (t, title) in enumerate(program, start=1):
        crud.add_program_item(t, title, idx)

    # Не добавляем реальные файлы фотографий — лишь имитация записей
    # Это позволит фронтенду отображать заглушки, если нужно.
    for i in range(1, 5):
        crud.add_photo(f"sample_{i}.jpg", f"sample_{i}.jpg", i)
