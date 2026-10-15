# Disco Elysium — Ukrainian translation (installer & tools)

Інструменти й інсталятор українського перекладу **Disco Elysium — The Final Cut**.
Tools and installer for the Ukrainian translation of **Disco Elysium — The Final Cut**.

Переклад підміняє німецьку мову гри (у налаштуваннях гри обирається **Deutsch**).
The translation replaces the game's German language slot (choose **Deutsch** in the game settings).

## Для гравців / For players
Готові збірки інсталятора (Windows `.exe` і архів для Mac / Linux / Steam Deck) завантажуйте зі сторінки перекладу на Nexus Mods.
Download the ready-made installer builds (Windows `.exe`, and an archive for Mac / Linux / Steam Deck) from the translation's Nexus Mods page.

- [Інструкція українською](installer/README.uk.md)
- [Instructions in English](installer/README.en.md)

## Що в цьому репозиторії / What is in this repository
| Тека / Folder | Вміст / Contents |
|---|---|
| `installer/` | `installer.py` (вікно + текстовий режим, лише Python 3) та README / the installer (window + text mode, plain Python 3) and READMEs |
| `tools/` | Скрипти дослідження файлів гри, патчів, збірки пакета й тестів інсталятора / scripts for inspecting game files, patching, building the package and testing the installer |
| `docs/` | Нотатки: що де знайдено, рішення щодо інсталятора, глосарій / notes: findings, installer decisions, glossary |

**Файли гри й повний текст перекладу тут не публікуються.** Інсталятор розповсюджується разом з пакетом (`package/`): бінарні патчі (bsdiff)
до кількох файлів гри та файли самого перекладу; його збирає `tools/build_package.py` із локального знімка гри.
Game files and the full translated text are **not** published in this repository. The installer ships with a `package/` folder
(binary bsdiff patches for a few game files plus the translation bundles) built by `tools/build_package.py` from a local snapshot.

## Перевірено / Tested
Windows + Steam. Steam Deck / Linux (Proton), GOG, Xbox app, macOS: очікується, але ще не перевірено / expected but not tested yet.

Не афілійовано з ZA/UM. Disco Elysium — торгова марка Zaum Studio OU.
Not affiliated with ZA/UM. Disco Elysium is a trademark of Zaum Studio OU.
