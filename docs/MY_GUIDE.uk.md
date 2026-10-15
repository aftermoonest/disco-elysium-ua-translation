# Мій короткий гайд: що де лежить і як це запускати

(Стан на 2026-10-15. Усе нижче відкривайте з теки проєкту `D:\Work files\disco elysium translation`.)

## 1. Які папки вам зараз потрібні

| Тека | Що це | Чіпати? |
|---|---|---|
| `dist_next\` | **Найсвіжіша збірка.** Тут два готові архіви для гравців | беріть звідси |
| `installer\` | Код інсталятора (`installer.py`) і README (UA/EN) | лише якщо міняєте інсталятор |
| `translation\` | `general.tsv`, `dialogues.tsv`: текст перекладу «ключ → текст» (експорт з гри) | читати/ділитись |
| `work\snapshot\2026-10-15\` | **Знімок усіх змінених файлів гри** (з нього збирається пакет) | не видаляти |
| `work\backup\` | **Оригінальні** файли гри до змін (з них роблять патчі) | не видаляти! |
| `work\testgame\`, `work\testgame_exe\` | Тестові копії гри для перевірки інсталятора | можна стерти, скрипт створить заново |
| `tools\` | Скрипти (збірка, тести, експорт) | запускає Claude/ви командами нижче |
| `docs\` | Нотатки: `findings.md` (що знайшли), `installer-spec.md` (рішення), цей гайд | читати |
| `dist\` | Старіша збірка (без README). **Застаріла**, дивіться `dist_next` | можна ігнорувати |
| `Disco Elysium ukr dumb\`, `Disco Elysium  Ukrainian translation\` | Старі дампи й старий реліз. **Застарілі** (правки тексту тепер лише в `translation\` і в `work\snapshot`) | не використовувати |

## 2. Що брати, щоб віддати гравцям
У теці `dist_next\`:
- `DiscoElysium_UA_installer_v1.0_windows.zip` (24,5 МБ): **Windows**. Усередині `.exe`, README, тека `package`.
- `DiscoElysium_UA_installer_v1.0_python.zip` (14,2 МБ): **Mac / Linux / Steam Deck**. Усередині `installer.py`, README, `package`.

Це дві «версії для завантаження» на Nexus. Тека `package` має завжди лежати поруч з `.exe` або `installer.py`.

## 3. Як запустити інсталятор самому

**Вікно (звичайний спосіб):** розпакуйте `windows.zip` і двічі клацніть `DiscoElysium_UA_installer.exe`. Або з теки проєкту (PowerShell):
```powershell
python installer\installer.py --game "work\testgame\Disco Elysium"
```
Це **тестова копія**. Справжню гру інсталятор поки не чіпайте таким чином:

**Справжня гра** (`D:\Games\SteamLibrary\steamapps\common\Disco Elysium`): там зараз переклад стоїть «вручну», без резервної копії, тому інсталятор відмовиться. Щоб поставити через нього:
1. У Steam: Disco Elysium → Властивості → Інстальовані файли → **Перевірити цілісність файлів**. Це поверне оригінали (і заодно прибере наш переклад).
2. Запустіть інсталятор (`.exe`) → «Знайти гру» → «Встановити / оновити». Він знову поставить усе, що зараз у грі.
3. У грі в налаштуваннях мови оберіть Deutsch.

Текстовий режим (для перевірки без вікна):
```powershell
python installer\installer.py --cli info --game "ШЛЯХ_ДО_ГРИ"
python installer\installer.py --cli install --dry-run --game "ШЛЯХ_ДО_ГРИ"
```

## 4. Як зробити нову версію після змін у грі

1. Внесли правки в гру (через UABEA/скрипти), перевірили, що все працює.
2. **Знімок поточного стану** (оновить `work\snapshot\<дата>` і `translation\*.tsv`):
   ```powershell
   python -I tools\export_snapshot.py 2026-10-20
   ```
3. **Збірка пакета й архівів** (замініть версію; `.exe` вже зібраний у `build\exe\`):
   ```powershell
   python -I tools\build_package.py --version 1.1 --dist dist_next --exe build\exe\DiscoElysium_UA_installer.exe
   ```
   Якщо змінювали `installer.py`, спершу перезберіть `.exe`:
   ```powershell
   python -m PyInstaller --onefile --noconsole --name DiscoElysium_UA_installer --distpath build\exe --workpath build\work --specpath build --noconfirm installer\installer.py
   ```
4. **Тест на копії гри** (22 перевірки, справжню гру не чіпає):
   ```powershell
   $env:UA_DIST="dist_next"; $env:UA_TESTGAME="testgame_exe"; $env:UA_EXE="$PWD\dist_next\unzipped\DiscoElysium_UA_installer\DiscoElysium_UA_installer.exe"; python -I tools\test_installer.py
   ```
   (перед цим розпакуйте свіжий `windows.zip` у `dist_next\unzipped`). Має закінчитись `RESULT: ALL PASSED`.
5. Заливайте на Nexus два архіви з `dist_next`.

## 5. Важливі застереження

- **Редагувати переклад у `translation\*.tsv` поки що марно:** збірка бере тексти зі **знімка бандлів гри**, а не з TSV. TSV зараз лише читабельний експорт. Правки тексту робимо в бандлі (як і раніше), потім робимо знімок (крок 2). Збирання бандла з TSV можна додати окремим кроком.
- Резервні копії в `work\backup\` потрібні, щоб робити патчі від справжніх оригіналів. Не видаляйте їх і не перезаписуйте.
- Тільки Windows + Steam перевірено. Mac, GOG, Xbox-застосунок: дивіться README та `docs\installer-spec.md`.
- Версії файлів гри в патчах прив'язані до **цієї** версії гри. Якщо Steam оновить гру, патчі треба буде перебудувати з нових оригіналів.

## 6. Що ще не зроблено
- Тест і набір патчів для Mac (у вас є Mac), перевірка GOG / Xbox.
- Публікація репозиторію на GitHub (поки не вирішили).
- Зі списку помилок: розміри шрифтів у назвах навичок, символи Є І Ї Ґ у шрифті `CoreSansES`, переповнення тексту, переклад картинок.
