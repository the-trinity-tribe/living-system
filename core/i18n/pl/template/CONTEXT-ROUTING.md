# CONTEXT-ROUTING.md

**Zacznij od najkrótszej drogi. Wczytuj więcej kontekstu tylko wtedy, gdy wymaga tego zadanie.**

| Potrzeba | Czytaj |
| --- | --- |
| Kto jest właścicielką lub właścicielem, role | `SYSTEM.md` (wiążące tylko ze `status: approved`) |
| Zasady przewodnie | `PRINCIPLES.md` (wiążące tylko ze `status: approved`) |
| Zatwierdzone ustalenie (kto co zatwierdza, jak coś ma być zrobione) | Właściwy **aktualny** plik w `decisions/` (pomiń każdą decyzję, którą inna zatwierdzona decyzja wymienia w `supersedes:`; `python3 tools/review.py current` je wypisuje) |
| Wiedza do ponownego użycia | Właściwy plik w `knowledge/` |
| Bieżący projekt | Właściwy plik w `projects/` |
| Powtarzalna praca z przebiegiem etapowym | Właściwy folder w `workflows/` |
| Proponowane zmiany czekające na przegląd (jeszcze nieobowiązujące) | `proposals/`: czytaj, gdy pytanie dotyczy tego, co czeka, albo zanim powstanie nowa propozycja |
| Gdzie skończyła się ostatnia sesja (niewiążące) | `handover/LATEST.md` |
| Czy system pomaga? (własny test właścicielki lub właściciela) | `value-check/README.md` |
| Moduły opcjonalne, które można dodać (niezainstalowane) | `.living/catalog.md` |
<!-- profile:append -->

Wskazówki:

- Przy zadaniu projektowym zacznij od pliku projektu. Wskazuje on decyzje, które obowiązują.
- Wszystko, co dotyczy zatwierdzania, to pytanie do decyzji. Zajrzyj do `decisions/`, a nie do opisów ról. Jeśli pytanie dotyczy konkretnego projektu, przeczytaj też jego plik: notatki robocze mogą zawierać nowsze twierdzenia sprzeczne z decyzją (zobacz `AGENTS.md`, sekcja 5). Notatki nigdy nie mają pierwszeństwa przed decyzją.
