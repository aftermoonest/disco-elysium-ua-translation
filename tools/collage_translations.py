"""Ukrainian translation of the Collage-mode lockit (German column of CollageModeLockit, collage/shared).

Source texts: English column (primary) + Russian (reference). Terminology follows the existing mod lockit:
Ревашоль, Мартінез, Еврарт, Куно, Головомір, «Танці в лахмітті», Фріссель, Сюзеренітет, комунари.
Formal "ви" as in the rest of the mod. Rich-text tags (<b>, <i>, <align>) are kept; *emphasis* from English
is written as <i>..</i> like the German column does.

Run: python -I tools/collage_translations.py  -> writes work/collage_ua.json
"""
import json
from pathlib import Path

T = {
    "Collage/ACHIEVEMENT/ALL_HIDDEN": "Відновіть усі приховані фото",
    "Collage/ACHIEVEMENT/FACADE": "Безцінний фасад",
    "Collage/ACHIEVEMENT/FIRE": "Його ж точно можна знищити вогнем",
    "Collage/ACHIEVEMENT/GENTRIFICATION": "Гладенькі від грошей вулиці джентрифікації",
    "Collage/ACHIEVEMENT/GLIMPSE": "Глянь, поки є нагода",
    "Collage/ACHIEVEMENT/OLD_FLAME": "Давнє кохання",
    "Collage/ACHIEVEMENT/PROGRESS": "Схоже на прогрес",
    "Collage/ACHIEVEMENT/PROVENANCE": "А тепер — складне походження",
    "Collage/ACHIEVEMENT/SPECTRES": "Примари надії",
    "Collage/ACHIEVEMENT/WHEELS": "Буксує на місці",
    "Collage/Actors/BABE1": "Дівчина Головоміра 1",
    "Collage/Actors/BABE2": "Дівчина Головоміра 2",
    "Collage/Actors/BABE3": "Дівчина Головоміра 3",
    "Collage/Actors/DRUNK_WORKER": "П’яний робітник",
    "Collage/Actors/HARRIER_DU_BOIS": "Гар’єр Дюбуа",
    "Collage/Actors/LANDLADY": "Домовласниця",
    "Collage/Actors/MONEY_MAN": "Грошовитий чолов’яга",
    "Collage/Actors/SAKE_SUNRISE": "Sake Sunrise",
    "Collage/Actors/SCAB1": "Штрейкбрехер 1",
    "Collage/Actors/SCAB2": "Штрейкбрехер 2",
    "Collage/Actors/SPONSOR": "Спонсор",
    "Collage/Actors/TARE_DRUNKESS": "П’яничка з порожніми пляшками",
    "Collage/BUTTON/ACCEPT": "Прийняти",
    "Collage/BUTTON/APPLY": "Застосувати",
    "Collage/BUTTON/CHANGE": "Змінити",
    "Collage/BUTTON/CHANGE_POSE": "Змінити позу",
    "Collage/BUTTON/CLOSE": "Закрити",
    "Collage/BUTTON/COLLAGE": "Колаж",
    "Collage/BUTTON/CONFIRM_EXIT": "Ви впевнені, що хочете вийти?",
    "Collage/BUTTON/CREATE": "Створити",
    "Collage/BUTTON/DELETE": "Видалити",
    "Collage/BUTTON/DELETE_CHARACTER": "Видалити персонажа",
    "Collage/BUTTON/DELETE_STICKER": "Видалити наліпку",
    "Collage/BUTTON/DELETE_TEXT": "Видалити текст",
    "Collage/BUTTON/DONE": "Готово",
    "Collage/BUTTON/EDIT": "Редагувати",
    "Collage/BUTTON/EXIT": "Вийти",
    "Collage/BUTTON/FAVOURITE": "В обране",
    "Collage/BUTTON/FAVOURITE_TOGGLE": "Перекл. обране",
    "Collage/BUTTON/LOADING": "Завантаження",
    "Collage/BUTTON/MOVE": "Пересунути",
    "Collage/BUTTON/NEW_SAVE": "Нове збереження",
    "Collage/BUTTON/NONE": "Немає",
    "Collage/BUTTON/OK": "ОК",
    "Collage/BUTTON/OPEN": "Відкрити",
    "Collage/BUTTON/PLACE": "Розмістити",
    "Collage/BUTTON/PLACE_CHARACTER": "Розмістити персонажа",
    "Collage/BUTTON/PLACE_FRAGMENT": "Розмістити фрагмент",
    "Collage/BUTTON/PLACE_STICKER": "Розмістити наліпку",
    "Collage/BUTTON/PLACE_TEXT": "Розмістити текст",
    "Collage/BUTTON/REJECT": "Відхилити",
    "Collage/BUTTON/REMOVE": "Прибрати",
    "Collage/BUTTON/REMOVE_FRAGMENT": "Прибрати фрагмент",
    "Collage/BUTTON/RESET": "Скинути",
    "Collage/BUTTON/ROTATE": "Повернути",
    "Collage/BUTTON/SAVED_PATH_FORMAT": "Збережено в «{0}»",
    "Collage/BUTTON/SAVED_PATH_SCREENSHOTS": "Збережено в «Знімки екрана»",
    "Collage/BUTTON/SCALE": "Масштабувати",
    "Collage/BUTTON/SELECT": "Вибрати",
    "Collage/BUTTON/SET": "Встановити",
    "Collage/BUTTON/SET_LOCATION": "Вибрати місце",
    "Collage/BUTTON/SET_TIME": "Встановити час",
    "Collage/BUTTON/ZOOM": "Збільшити",
    "Collage/CONTENT_POLICY": (
        "<b><align=center>DISCO ELYSIUM\n"
        "ПОЛІТИКА ЩОДО ВМІСТУ COLLAGE\n"
        "</align></b>\n"
        "\n"
        "Видана компанією Zaum Studio Limited («ZA/UM», «ми» або «нас»).\n"
        "Останнє оновлення: вересень 2022 року\n"
        "\n"
        "<b>1. Вступ\n"
        "</b>\n"
        "1.1 Ця Політика щодо вмісту поширюється на всіх осіб, які користуються режимом «Колаж» у грі Disco Elysium (далі — «Гра»).\n"
        "1.2 Будь ласка, уважно прочитайте цю Політику щодо вмісту, перш ніж користуватися режимом «Колаж». Ми можемо час від часу змінювати або оновлювати цю Політику щодо вмісту.\n"
        "1.3 Ця Політика щодо вмісту є частиною нашої Ліцензійної угоди з кінцевим користувачем («EULA») і має розглядатися разом із нею. Ознайомитися з нашою EULA можна тут: https://discoelysium.com/end-user-licence-agreement.\n"
        "1.4 Якщо цю Політику щодо вмісту перекладено будь-якою мовою, окрім англійської, переклад подано лише для зручності, а переважну силу має англомовна версія.\n"
        "\n"
        "<b>2. Правила щодо користувацького вмісту\n"
        "</b>\n"
        "2.1 Ми раді, що ви створюєте та поширюєте власний вміст, створений у режимі «Колаж» («Вміст»), за таких умов:\n"
        "2.1.1 Ви не повинні видаляти водяний знак «Колажу» зі свого Вмісту або іншим чином публічно демонструвати свій Вміст так, щоб водяний знак був прихований.\n"
        "2.1.2 Якщо ви не маєте прав на використання чужої ІВ (визначення наведено нижче) у своєму Вмісті, ви не повинні її використовувати. Якщо ми дізнаємося, що ваш Вміст містить чужу ІВ без дозволу, ми можемо вимагати від вас його видалити.\n"
        "2.1.3 Ми маємо право в будь-який час і з будь-якої причини, яку вважаємо доречною на власний розсуд, зупинити або обмежити використання вами ІВ компанії ZA/UM, зокрема, але не виключно, якщо вважатимемо таке використання недоречним, образливим, шкідливим або принизливим. У такому разі ви зобов’язані негайно видалити свій Вміст.\n"
        "2.2 Ви також погоджуєтеся не публікувати, не повідомляти, не передавати та не робити доступним жодний Вміст, який:\n"
        "2.2.1 є образливим, підбурювальним, порнографічним, гомофобним, наклепницьким, ганебним, ворожим, дискримінаційним, непристойним, провокаційним або расистським;\n"
        "2.2.2 переслідує, цькує чи залякує будь-яку особу;\n"
        "2.2.3 передбачає надсилання небажаної чи несанкціонованої реклами, рекламних матеріалів або спаму;\n"
        "2.2.4 є протиправним, зловмисним, оманливим або тягне цивільну чи кримінальну відповідальність, порушує норми чи чинні кодекси поведінки або, на нашу думку, може зашкодити репутації нашій чи нашої Гри;\n"
        "2.2.5 порушує або може порушувати права на ІВ, договірні права, права на конфіденційність чи інші права наші або будь-якої третьої сторони в будь-якій точці світу, або сприяє такому порушенню чи заохочує його;\n"
        "2.2.6 становить або пропагує будь-яку незаконну діяльність чи будь-яку діяльність, що іншим чином призводить до порушення чинних норм або кодексів поведінки;\n"
        "2.2.7 містить будь-які матеріали з обмеженим доступом, зокрема, але не виключно, паролі, медичну інформацію чи конфіденційну інформацію будь-якої особи; або\n"
        "2.2.8 спонукає, запрошує, заохочує, обстоює, підбурює чи провокує до будь-чого з наведеного вище або іншим чином не відповідає духу та букві попередніх умов.\n"
        "\n"
        "<b>3. Інтелектуальна власність\n"
        "</b>\n"
        "3.1 Створюючи свій Вміст і ділячись ним, ви надаєте нам невиключне, всесвітнє право та ліцензію з правом сублікування на відтворення, копіювання, розповсюдження, надання доступу, публікацію, виконання, постачання, використання, маркетинг, рекламу, просування й іншу демонстрацію Вмісту, а також на використання будь-якої та всієї ІВ у Вмісті для таких цілей. «ІВ» означає авторські права, права на дизайн, права на бази даних, патенти та будь-які права на винаходи, ноу-хау, торговельні та ділові назви, комерційні таємниці й торговельні марки (зареєстровані чи незареєстровані), а також будь-які заявки або продовження щодо них і всі інші права інтелектуальної власності подібного чи рівнозначного типу на будь-якій території світу.\n"
        "3.2 Ми надаємо вам обмежене, невиключне право та ліцензію на використання вмісту Гри та ІВ у ній, доступних вам у режимі «Колаж», для вашого особистого некомерційного використання відповідно до умов EULA та цієї Політики щодо вмісту (і в разі будь-яких суперечностей між цією Політикою щодо вмісту та EULA переважну силу мають умови EULA).\n"
        "3.3 Усі права на ІВ, пов’язані з Грою та кожною її частиною, належать нам і нашим ліцензіарам відповідно до EULA. Ліцензія, надана вам пунктом 3.2, не надає жодного права власності на Гру чи будь-яку ІВ у ній. Гра призначена виключно для особистого некомерційного використання кінцевими користувачами відповідно до умов цієї Політики щодо вмісту та EULA. Будь-яке використання, відтворення чи повторне розповсюдження Гри всупереч умовам цієї Політики щодо вмісту та EULA прямо заборонено.\n"
        "3.4 Ви несете повну відповідальність за свій Вміст і за те, щоб він відповідав усім чинним законам, нормам, політикам і настановам (зокрема, але не виключно, політикам чи настановам сторонніх платформ). Ми не несемо і не будемо нести відповідальності, повної чи часткової, за жодні претензії, позови чи спори, висунуті проти нас або вас у зв’язку з будь-яким вашим Вмістом."
    ),
    "Collage/FELD/SKILL": "Навичка",
    "Collage/FELD/SPEAKER": "Мовець",
    "Collage/FILTER/AMBROTYPE": "Амбротипія",
    "Collage/FILTER/ANODIC": "Анодний",
    "Collage/FILTER/BASIN": "Басейнова культура",
    "Collage/FILTER/BREEZE": "Вітерець",
    "Collage/FILTER/CALCULUS": "Візуальний аналіз",
    "Collage/FILTER/CHEMIGRAM": "Хемограма",
    "Collage/FILTER/CYANOTYPE": "Ціанотипія",
    "Collage/FILTER/DAGUERREOTYPE": "Дагеротипія",
    "Collage/FILTER/ETERNITE": "Етерніт",
    "Collage/FILTER/EXPRESSIONIZM": "Експресіонізм",
    "Collage/FILTER/HANGOVER": "Пекельне похмілля",
    "Collage/FILTER/KOPFSCHERZEN": "Копфшмерцен",
    "Collage/FILTER/LATITUDE": "Компресор широти",
    "Collage/FILTER/LILY": "Легка жовтизна",
    "Collage/FILTER/MAGNEOSTATIC": "Магнітостатика",
    "Collage/FILTER/MOURNING": "Білий траур",
    "Collage/FILTER/MULLEN": "Модус Маллена",
    "Collage/FILTER/NORMAL": "Звичайний",
    "Collage/FILTER/OIL": "Мазут",
    "Collage/FILTER/PALE_AGED": "Вицвілий від часу",
    "Collage/FILTER/PYRHOLIDON": "Пірролідон",
    "Collage/FILTER/SMOKE": "Льодовиковий дим",
    "Collage/FILTER/STAIN": "Пляма думки",
    "Collage/FILTER/STELLA": "Стелла Маріс",
    "Collage/FILTER/TEQUILA": "Текіла Сансет",
    "Collage/FILTER/TROIKA": "Трійка",
    "Collage/FRAGMENT/ACE": "Привіт від аса",
    "Collage/FRAGMENT/CHEERS": "Вітання комунарів",
    "Collage/FRAGMENT/CITY": "Силует міста",
    "Collage/FRAGMENT/COMING": "Скоро відкриття",
    "Collage/FRAGMENT/COMMISSARS": "Майбутні подвійні комісари",
    "Collage/FRAGMENT/FRISSEL": "За Фрісселя!",
    "Collage/FRAGMENT/FRITTE": "Максимум «Фріттте»",
    "Collage/FRAGMENT/GOOD": "Заради вищого блага",
    "Collage/FRAGMENT/MIRACLE": "Нечестиве диво",
    "Collage/FRAGMENT/MONEY": "Грошова машина",
    "Collage/FRAGMENT/PROGRESS": "Безперечно прогрес",
    "Collage/FRAGMENT/REVACHOL": "Ласкаво просимо до Ревашолю",
    "Collage/FRAGMENT/SHADOW": "Нерухома тінь",
    "Collage/FRAGMENT/TERROR": "Державний терор",
    "Collage/FRAGMENT/WHIRLING": "«Танці у склі»",
    "Collage/FRAGMENT/WORKERS": "Хай живуть робітники",
    "Collage/FRAME/CALCULUS": "Візуальний аналіз",
    "Collage/FRAME/CATS": "Цікаві коти",
    "Collage/FRAME/COMMUNISM": "Будівництво комунізму",
    "Collage/FRAME/DETECTIVE": "Детектив прибуває на місце події",
    "Collage/FRAME/DISCO": "Диско",
    "Collage/FRAME/FRIENDS": "Найкращі друзі",
    "Collage/FRAME/FUCK": "На хер цей світ",
    "Collage/FRAME/GULLS": "Чайки",
    "Collage/FRAME/LOVE": "Вічне кохання",
    "Collage/FRAME/LOVER": "Кінець кохання",
    "Collage/FRAME/METAL": "Метал",
    "Collage/FRAME/MULLEN": "Дік Маллен",
    "Collage/FRAME/NECKTIE": "Жахлива краватка",
    "Collage/FRAME/NEVER": "Ніколи не зв’язуйся з ним",
    "Collage/FRAME/OFFICER": "Вітаю, офіцере",
    "Collage/FRAME/POSTCARD": "Листівка",
    "Collage/FRAME/PRIDE": "Гордість",
    "Collage/FRAME/SNOW": "Снігова куля",
    "Collage/FRAME/SUNRISE": "Прокидайся, Parabellum",
    "Collage/FRAME/WOOD": "Дерево",
    "Collage/FRAME/WORK": "Час працювати",
    "Collage/HIDDEN/COMMUNIST": (
        "7 березня 02 року.\n"
        "Прості чоловіки й жінки взялися за зброю проти занепаду та розпусти Старих Грошей і вигнали Сюзеренітет у море.\n"
        "Герої-комунари сидять на спинах зморених, пошматованих кулями машин;\n"
        "святковий парад, що допомагає забути рани та втрачених близьких.\n"
        "У цій короткочасній перемозі, здається, не гріх дозволити собі бути <i>трішечки</i> щасливим."
    ),
    "Collage/HIDDEN/FASCIST": (
        "Відчайдушно прагнучи вгамувати чернь і бунтівників комунарського повстання,\n"
        "Фріссель Перший вдався до свого найгіршого й найдраматичнішого кроку.\n"
        "Він послав королівських драгунів верхи <i>угамувати</i> розлючений натовп,\n"
        "більшість якого навіть не були партизанами.\n"
        "Вони обмінюються поглядами жаху, жалю та облуди з тими, кого підпалюють.\n"
        "Але цієї ночі вони розпалюють у людях куди більше, ніж просто полум’я."
    ),
    "Collage/HIDDEN/MORALIST": (
        "Ти стаєш свідком моменту між епохами — пологових мук перетворення.\n"
        "Бульдозери дрімають там, де колись стояли рибальські хатини, повні справжніх людей.\n"
        "Але тепер усе служить новому комплексу, що повільно виринає з багнюки —\n"
        "«Центру юнацтва й освіти Клер».\n"
        "Гіркий смак солі та кремнієвого пилу важко висить у повітрі."
    ),
    "Collage/HIDDEN/ULTRALIBERAL": (
        "Це завтра. Післязавтра.\n"
        "Весілля скінчилося, гості розійшлися, а прибиральники ще не прийшли.\n"
        "Вони вже запізнюються років на 17.\n"
        "Це не покинутість і навіть не апокаліпсис — хоча дехто скаже, що так.\n"
        "Мартінез тепер — пам’ятник, безлика картина безмежної соціопатії,\n"
        "де існують лише бренди та гарне життя.\n"
        "Заплатіть за пакет і не забудьте чек."
    ),
    "Collage/MAP/APARTMENTS": "Апартаменти «Кейпсайд»",
    "Collage/MAP/CHURCH": "Долоріанська церква",
    "Collage/MAP/CINDY": "Притулок Сінді",
    "Collage/MAP/CONTAINER": "Портовий контейнер",
    "Collage/MAP/CUNO": "Халупа Куно",
    "Collage/MAP/DEFAULT": "За замовчуванням",
    "Collage/MAP/DOOMED_B1": "Приречена зона — цоколь",
    "Collage/MAP/DOOMED_F1": "Приречена зона — 1-й поверх",
    "Collage/MAP/DOOMED_F2": "Приречена зона — 2-й поверх",
    "Collage/MAP/EVRANT_OFFICE": "Кабінет Еврарта",
    "Collage/MAP/FELD_B1": "Підвал «Фельда»",
    "Collage/MAP/FISHING_HOME": "Хата в рибальському селі",
    "Collage/MAP/FORTRESS_EXT": "Острів із морською фортецею",
    "Collage/MAP/FORTRESS_INT": "Нутрощі морської фортеці",
    "Collage/MAP/FRITTE": "Кіоск «Фріттте»",
    "Collage/MAP/GARY": "Квартира Гері",
    "Collage/MAP/HANGED_DREAM": "Сон повішеного",
    "Collage/MAP/INSTIGATOR_LAIR": "Лігво призвідниці",
    "Collage/MAP/LILIENNE": "Дім Лілієнн",
    "Collage/MAP/MARTINAISE": "Мартінез",
    "Collage/MAP/MARTINAISE_EAST": "Східний Мартінез",
    "Collage/MAP/MARTINAISE_SOUTH": "Південний Мартінез",
    "Collage/MAP/MARTINAISE_WEST": "Західний Мартінез",
    "Collage/MAP/PAWNSHOP": "Ломбард",
    "Collage/MAP/REVACHOL_DREAM": "Сон у «Відео Ревашоль»",
    "Collage/MAP/SHACK": "Покинута халупа",
    "Collage/MAP/SMOKER_APT": "Квартира курця",
    "Collage/MAP/TENT": "Намет спідфріка",
    "Collage/MAP/UNDERGROUND": "Підпільна читальня",
    "Collage/MAP/UNION_OFFICE": "Офіс профспілки",
    "Collage/MAP/WHIRLING_1F": "«Танці в лахмітті» — 2-й поверх",
    "Collage/MAP/WHIRLING_2F": "«Танці в лахмітті» — 3-й поверх",
    "Collage/MAP/WHIRLING_GF": "«Танці в лахмітті» — 1-й поверх",
    "Collage/MAP/WORKING_APT": "Квартира робітничого класу",
    "Collage/ORB": "Сфера № {0}",
    "Collage/POPUP/SPOILERS": "Увага! У цьому режимі є спойлери.",
    "Collage/SHARE/CANCEL": "Скасувати",
    "Collage/SHARE/IMPORT": "Імпортувати",
    "Collage/SHARE/IMPORTED_SCENE": "Імпортована сцена",
    "Collage/SHARE/IMPORT_LOAD": "Імпортувати й завантажити",
    "Collage/SHARE/IMPORT_SCENE": "Імпортувати сцену",
    "Collage/TAB/CHARACTERS": "Персонажі",
    "Collage/TAB/DELETE": "Видалити",
    "Collage/TAB/DUPLICATE": "Дублювати",
    "Collage/TAB/EFFECTS": "Ефекти",
    "Collage/TAB/FILTERS": "Фільтри",
    "Collage/TAB/FRAGMENTS": "Фрагменти",
    "Collage/TAB/FRAMES": "Рамки",
    "Collage/TAB/IMPORT": "Імпорт",
    "Collage/TAB/LOCATION": "Місце",
    "Collage/TAB/NEW": "Нове",
    "Collage/TAB/OBJECTS": "Предмети",
    "Collage/TAB/OPEN": "Відкрити",
    "Collage/TAB/SCENERY": "Краєвид",
    "Collage/TAB/SCENES": "Сцени",
    "Collage/TAB/SETTING": "Обстановка",
    "Collage/TAB/SHADERS": "Шейдери",
    "Collage/TAB/SHARE": "Поділитися",
    "Collage/TAB/STICKERS": "Наліпки",
    "Collage/TAB/TEXT": "Текст",
    "Collage/TAB/TIME_OF_DAY": "Час доби",
    "Collage/TAB/TINTS": "Відтінки",
    "Collage/TAB/WEATHER": "Погода",
    "Collage/TEXT_PLACEHOLDER": "Текст",
    "Collage/TOOLTIP/BIG": "Вел.",
    "Collage/TOOLTIP/BOLD": "Жирн.",
    "Collage/TOOLTIP/BORDER_COLOR": "Колір межі",
    "Collage/TOOLTIP/DRAG_CHARACTER": "Вибрати / перетягнути персонажа",
    "Collage/TOOLTIP/DRAG_FRAGMENT": "Вибрати / перетягнути фрагмент",
    "Collage/TOOLTIP/DRAG_STICKER": "Вибрати / перетягнути наліпку",
    "Collage/TOOLTIP/DRAG_TEXT": "Вибрати / перетягнути текст",
    "Collage/TOOLTIP/FONT": "Шрифт",
    "Collage/TOOLTIP/MEDIUM": "Серед.",
    "Collage/TOOLTIP/SELECT_CHARACTER": "Вибрати персонажа",
    "Collage/TOOLTIP/SELECT_FILTER": "Вибрати фільтр для зміни",
    "Collage/TOOLTIP/SELECT_FRAGMENT": "Вибрати фрагмент",
    "Collage/TOOLTIP/SELECT_FRAME": "Вибрати рамку для зміни",
    "Collage/TOOLTIP/SELECT_SCENE": "Вибрати сцену для завантаження",
    "Collage/TOOLTIP/SELECT_SETTING": "Вибрати обстановку для зміни",
    "Collage/TOOLTIP/SELECT_STICKER": "Вибрати наліпку",
    "Collage/TOOLTIP/SELECT_TEXT": "Вибрати текст",
    "Collage/TOOLTIP/SELECT_TIME": "Вибрати час доби для зміни",
    "Collage/TOOLTIP/SELECT_WEATHER": "Вибрати погоду для зміни",
    "Collage/TOOLTIP/SIZE": "Розмір",
    "Collage/TOOLTIP/SMALL": "Мал.",
    "Collage/TOOLTIP/STICKER": "Наліпка",
    "Collage/TOOLTIP/TEXT_COLOR": "Колір тексту",
    "Collage/TOOLTIP/THIN": "Тонк.",
    "Collage/TOOLTIP/WEIGHT": "Товщина",
    "Collage/VISCAL": "Віз. аналіз № {0}",
    "Collage/WEATHER/CLEAR": "Ясно",
    "Collage/WEATHER/FOG": "Туман",
    "Collage/WEATHER/HEAVY_RAIN": "Злива",
    "Collage/WEATHER/HEAVY_SNOW": "Сильний сніг",
    "Collage/WEATHER/LIGHT_SNOW": "Легкий сніг",
    "Collage/WEATHER/RAIN": "Дощ",
    "Collage/WEATHER/SNOW": "Сніг",
    "Collage/WEATHER/WET_FOG": "Вологий туман",
}

if __name__ == "__main__":
    out = Path(__file__).resolve().parent.parent / "work" / "collage_ua.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(T, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(T), "translations ->", out)
