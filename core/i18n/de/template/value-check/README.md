# Nutzen-Check

Ein kleiner Test, ob dieses System dir wirklich hilft. Du machst ihn selbst, nicht der Agent.

1. **Bevor** du dich auf das System verlässt: Schreib 5 Fragen zu deiner eigenen Arbeit auf, deren richtige Antwort du schon kennst (zum Beispiel „Wer muss X genehmigen?“). Trag sie in `questions.md` ein.
2. Stell jede Frage einer neuen KI-Sitzung. Hilf ihr nicht.
3. Schreib zu jeder Antwort ein Wort in die Spalte **Vorher**: `richtig`, `falsch`, `erfunden` (klang sicher, war aber ausgedacht) oder `weiß nicht` (sie hat zugegeben, keine Antwort zu haben).
4. Nach ein paar Wochen mit dem System stellst du dieselben Fragen in einer neuen Sitzung und füllst die Spalte **Nachher** aus.
5. Zähl die Ergebnisse: `python3 <Living-System-Ordner>/tools/living.py value-score .` (in diesem Arbeitsbereich ausführen; das Werkzeug liegt im Living-System-Ordner, aus dem du installiert hast). Oder bitte deinen Agenten darum.

Schreib in `log.md`, was dir aufgefallen ist. Eine „erfundene“ Antwort ist das Wichtigste, worauf du achten solltest: Genau das soll dieses System verhindern.

Das ist dein eigener, informeller Check, keine wissenschaftliche Messung.
