# Mein Living-System-Arbeitsbereich

Das ist dein eigener Arbeitsbereich. Er wurde mit `tools/living.py init` erstellt. Er besteht aus einfachen Markdown-Dateien auf deinem Computer. Dieses System lädt nichts irgendwohin hoch.

**Die Idee:** Du entscheidest, was gilt. Dein KI-Agent liest diese Dateien, hilft dir bei der Arbeit und *schlägt* Änderungen vor. Deine Regeln ändert er nie von sich aus.

## Erste Schritte

1. Öffne diesen Ordner in Claude Code oder Codex. Der Agent liest zuerst `AGENTS.md`.
2. Lies `SYSTEM.md` und `PRINCIPLES.md`. Beide sind **Entwürfe**. Wenn eine Datei für dich passt, ändere `status: draft` selbst in `status: approved`.
3. Mach den Nutzen-Check (`value-check/README.md`), bevor du dich auf das System verlässt.
4. Prüfe die Struktur jederzeit mit `python3 tools/review.py check` (zeigt `ok`, wenn alles stimmt). Was auf dich wartet, zeigt `python3 <Living-System-Ordner>/tools/living.py status .`. Eine ausführlichere Prüfung in einfachen Worten macht `python3 <Living-System-Ordner>/tools/living.py doctor .`

Unter Windows schreibst du `py` statt `python3`.

## Was hier drin ist

| Ordner oder Datei | Was es ist |
| --- | --- |
| `AGENTS.md` | Regeln für den Agenten (auf Englisch, siehe unten). |
| `SYSTEM.md`, `PRINCIPLES.md` | Wer du bist und wofür du stehst. Entwurf, bis du zustimmst. |
| `decisions/` | Deine genehmigten Regeln. Eine Datei pro Regel. Nie bearbeitet, nur ersetzt. |
| `proposals/` | Änderungen, die der Agent vorschlägt. Keine Regeln, bis du sie genehmigst. |
| `projects/`, `knowledge/`, `workflows/` | Dein Arbeitskontext. |
| `handover/LATEST.md` | Wo die letzte Sitzung aufgehört hat. |
| `value-check/` | Dein eigener Test, ob das System dir hilft. |
| `.living/` | Deine Einstellungen und eine Liste der ursprünglichen Dateien. |

## Sprache

Deine Inhalte können in jeder Sprache sein. Ein paar Wörter müssen **Englisch** bleiben, weil die Werkzeuge sie lesen: die Schlüssel im Kopfbereich (`status`, `target`, `kind`, ...) und die Überschriften `## Rule`, `## Why`, `## Scope`, `## Proposed future state`, `## Why and open questions`, `# Proposal:`. Der Text darunter ist in deiner Sprache.

Diese Startdateien sind auf Deutsch, weil du `--language de` gewählt hast (mit `--language pl` wären sie auf Polnisch, sonst auf Englisch). Die Regeln für den Agenten (`AGENTS.md`, `CLAUDE.md`) bleiben auf Englisch, damit es nur einen geprüften Regelsatz gibt. Der Agent antwortet dir trotzdem auf Deutsch und schreibt neue Inhalte auf Deutsch.

## Aktualisieren

Wenn es eine neuere Version von Living System gibt, führe hier `python3 <Living-System-Ordner>/tools/living.py upgrade .` aus. Du siehst, was sich ändern würde; mit `--apply` wird es übernommen. Es werden nur Dateien aktualisiert, die du nie geändert hast. Bei Dateien, die du bearbeitet hast, bleibt deine Fassung; die neue landet zum Vergleich in `.living/upgrade/`. `decisions/`, `proposals/`, `projects/` und `me/` werden nie angefasst.

## Rückgängig machen

Lösche diesen Ordner. Sonst wurde auf deinem Computer nichts verändert.

## Grenzen

Experimentell. Das System prüft nicht, wer du bist, schützt Dateien nicht vor dem Lesen, und ein Agent kann Anweisungen trotzdem ignorieren. Nutze es nicht als Sicherheitswerkzeug.
