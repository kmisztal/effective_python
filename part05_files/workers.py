"""Importowalne funkcje dla przykładów procesów z part05 (Python >= 3.10)."""


def count_row(row, minimum=4, maximum=8):
    """Policz elementy z domkniętego przedziału [minimum, maximum]."""
    return sum(minimum <= value <= maximum for value in row)


def count_batch(rows):
    return [count_row(row) for row in rows]


def sum_squares(limit):
    """Celowo obliczenia w Pythonie, bez wzoru zamkniętego."""
    return sum(value * value for value in range(limit))


def reciprocal(value):
    return 1 / value


def append_and_return(items, value):
    """Zmień otrzymaną listę i zwróć ją jawnie do wywołującego."""
    items.append(value)
    return items
