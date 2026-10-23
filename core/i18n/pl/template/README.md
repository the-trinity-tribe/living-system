# Moja przestrzeń robocza Living System

To jest twoja własna przestrzeń robocza. Została utworzona poleceniem `tools/living.py init`. Składa się ze zwykłych plików Markdown na twoim komputerze. Ten system niczego nigdzie nie wysyła.

**Idea:** to ty decydujesz, co obowiązuje. Twój agent AI czyta te pliki, pomaga ci w pracy i *proponuje* zmiany. Nigdy sam nie zmienia twoich zasad.

## Pierwsze kroki

1. Otwórz ten folder w Claude Code albo Codex. Agent najpierw czyta `AGENTS.md`.
2. Przeczytaj `SYSTEM.md` i `PRINCIPLES.md`. Oba pliki są **szkicami**. Gdy plik ci odpowiada, sama lub sam zmień `status: draft` na `status: approved`.
3. Zrób test użyteczności (`value-check/README.md`), zanim zaczniesz polegać na systemie.
4. Strukturę sprawdzisz w każdej chwili poleceniem `python3 tools/review.py check` (pokazuje `ok`, gdy wszystko się zgadza). To, co czeka na ciebie, pokazuje `python3 <folder Living System>/tools/living.py status .`. Dokładniejsze sprawdzenie prostymi słowami robi `python3 <folder Living System>/tools/living.py doctor .`

W systemie Windows wpisz `py` zamiast `python3`.

## Co tu jest

| Folder lub plik | Co to jest |
| --- | --- |
| `AGENTS.md` | Zasady dla agenta (po angielsku, zobacz niżej). |
| `SYSTEM.md`, `PRINCIPLES.md` | Kim jesteś i czym się kierujesz. Szkic, dopóki nie zatwierdzisz. |
| `decisions/` | Twoje zatwierdzone zasady. Jeden plik na zasadę. Nigdy nie są edytowane, tylko zastępowane. |
| `proposals/` | Zmiany proponowane przez agenta. Nie są zasadami, dopóki ich nie zatwierdzisz. |
| `projects/`, `knowledge/`, `workflows/` | Twój kontekst pracy. |
| `handover/LATEST.md` | Gdzie skończyła się ostatnia sesja. |
| `value-check/` | Twój własny test, czy system ci pomaga. |
| `.living/` | Twoje ustawienia i lista pierwotnych plików. |

## Język

Twoje treści mogą być w dowolnym języku. Kilka słów musi zostać **po angielsku**, bo czytają je narzędzia: klucze w nagłówku pliku (`status`, `target`, `kind`, ...) i nagłówki `## Rule`, `## Why`, `## Scope`, `## Proposed future state`, `## Why and open questions`, `# Proposal:`. Tekst pod nimi jest w twoim języku.

Te pliki startowe są po polsku, bo wybrano `--language pl` (z `--language de` byłyby po niemiecku, w innych przypadkach po angielsku). Zasady dla agenta (`AGENTS.md`, `CLAUDE.md`) zostają po angielsku, żeby był tylko jeden sprawdzony zestaw zasad. Agent i tak odpowiada ci po polsku i po polsku pisze nowe treści.

## Aktualizacja

Gdy pojawi się nowsza wersja Living System, uruchom tutaj `python3 <folder Living System>/tools/living.py upgrade .`. Zobaczysz, co by się zmieniło; z `--apply` zmiany zostaną wprowadzone. Aktualizowane są tylko pliki, których nigdy nie zmieniałaś ani nie zmieniałeś. W plikach, które edytowałaś lub edytowałeś, zostaje twoja wersja; nowa trafia do porównania do `.living/upgrade/`. `decisions/`, `proposals/`, `projects/` i `me/` nigdy nie są ruszane.

## Cofnięcie

Usuń ten folder. Nic innego na twoim komputerze nie zostało zmienione.

## Ograniczenia

Wersja eksperymentalna. System nie sprawdza, kim jesteś, nie chroni plików przed odczytem, a agent wciąż może zignorować instrukcje. Nie traktuj go jak narzędzia bezpieczeństwa.
