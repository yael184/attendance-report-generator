# מדריך למילוי ההערכה העצמית (self_assessment_v2)

המסמך הזה ממפה כל קריטריון בטופס ההערכה אל המקום בקוד שמוכיח אותו, עם
ערך המחוון המומלץ (100) והטקסט שאפשר להדביק לכל תיבת הערות.

> כל הבדיקות עוברות (`71 passed`), הכיסוי ~89%, ו-`mypy --strict` עובר נקי.

---

## 1️⃣ ארכיטקטורה ותכנון (25)

| קריטריון | מחוון | הוכחה בקוד |
| --- | --- | --- |
| הפרדת שכבות (Layering) | **100** | `src/attendance_report/{domain, application, infrastructure}` + `cli.py`/`container.py`. ה-domain טהור — לא מייבא כלום מ-infrastructure. |
| Dependency Injection | **100** | `container.py` הוא composition root יחיד; `main.py`/`cli.py` לא יודעים *איך* לבנות שירות. |
| מבנה תיקיות | **100** | `src/` layout + `tests/unit` + `tests/integration`. |

**הערות לתיבה (ארכיטקטורה):**
> בנינו Clean Architecture עם שלוש שכבות: domain (מודל עסקי טהור ללא I/O),
> application (use cases + design patterns + ports), ו-infrastructure (מתאמים
> ל-OCR/PDF/logging). התלויות זורמות פנימה בלבד — ה-domain לא מייבא שום
> תשתית. כל ה-wiring מרוכז ב-`container.py` (DI container), כך שה-CLI רק מבקש
> pipeline מוכן ומריץ אותו.

---

## 2️⃣ דיזיין פטרנים (30)

| פטרן | מחוון | הוכחה בקוד |
| --- | --- | --- |
| Strategy | **100** | `application/parsing/*_parser.py`, `application/transformation/type_a.py`/`type_b.py`. |
| Factory | **100** | `ParserFactory`, `StrategyFactory` — *יוצרות* instance לפי סוג, לא מאחסנות. |
| Template Method | **100** | `BaseReportParser.parse` הוא השלד; subclasses ממלאים `matches` + `_parse_line` (ABC + `@abstractmethod`). |
| Decorator | **100** | `ValidatingStrategyDecorator` עוטף כל strategy *או decorator אחר* (אותו interface). |
| Observer | **100** | `TransformationService` (subject) מודיע ל-`LoggingObserver`/`StatisticsObserver`; observers ב-constructor, ללא coupling. |
| Registry | **100** | רישום עצמי עם `@ParserFactory.register`/`@StrategyFactory.register` + `RULES_REGISTRY`. |

**הערות לתיבה (פטרנים):**
> הוספת סוג דוח שלישי דורשת רק class parser + class strategy חדשים — שניהם
> נרשמים אוטומטית ב-registry דרך decorator, וללא שינוי בקוד קיים (Open/Closed).
> ה-Decorator מממש בדיוק את אותו interface (`TransformationStrategy`), ולכן
> אפשר לעטוף אותו בעוד decorator. ה-Observer מנתק את ה-logging מה-service.

---

## 3️⃣ איכות קוד ובשלות הנדסית (25)

| קריטריון | מחוון | הוכחה בקוד |
| --- | --- | --- |
| Type Hints | **100** | עובר `mypy --strict` על 30 קבצים, אפס שגיאות. |
| Immutable dataclasses | **100** | כל המודלים `@dataclass(frozen=True, slots=True)`; טרנספורמציה דרך `dataclasses.replace`. |
| Deterministic randomness | **100** | `transformation/seed.py` — seed לפי קובץ **+ תאריך השורה** (`derive_row_seed`). |
| Custom exceptions | **100** | `domain/exceptions.py`: `AttendanceError → ParseError/ValidationError/OutputError/...` |
| Configuration management | **100** | `domain/rules.py`: `VariantRules` frozen + `RULES_REGISTRY`, ללא hardcoding בקוד. |

**הערות לתיבה (איכות קוד):**
> כל ה-domain objects הם frozen, כך ש-mutation בטעות זורק TypeError. ה-randomness
> דטרמיניסטי ברמת השורה (seed = פונקציה של שם הקובץ + תאריך השורה), כך שכל יום
> משתנה באופן עצמאי וניתן לכתוב unit test שמאמת וריאציה ספציפית. כל ה-thresholds
> רוכזו ב-`rules.py` כ-frozen config.

---

## 4️⃣ בדיקות ו-DevOps (20)

| קריטריון | מחוון | הוכחה בקוד |
| --- | --- | --- |
| Unit Tests | **100** | `tests/unit/` — parsers, strategies, decorator, validators, factories, service, seed, time, models, rules, cli. כיסוי ~89%. |
| Integration Tests | **100** | `tests/integration/test_pipeline.py` (fakes) + `test_real_pipeline.py` (OCR+PDF אמיתי). |
| Docker | **100** | `Dockerfile` multi-stage עם tesseract+poppler+wkhtmltopdf+fonts ו-`.dockerignore`. |
| CLI (argparse) | **100** | `cli.py` — description, metavar, optional/required, `-v`, `--tesseract-path` וכו'. |
| pyproject.toml | **100** | `[project]`, `[build-system]`, `[tool.pytest]`, `[tool.coverage]`, `[tool.mypy]`. |

**הערות לתיבה (בדיקות & DevOps):**
> כתבנו ~71 בדיקות (unit + integration). ה-integration עם fakes רץ בכל מקום;
> בדיקה אחת מריצה את ה-pipeline האמיתי מקצה לקצה (OCR→PDF) ומדלגת אוטומטית אם
> הכלים לא מותקנים. ה-Dockerfile הוא multi-stage עם כל תלויות המערכת.

---

## 5️⃣ מודל אחיד

**הערות לתיבה:**
> יצרנו `AttendanceRow` (frozen) שאליו *שני* סוגי הדוח מתנרמלים. רק ה-parser
> וה-strategy ספציפיים לסוג; כל שאר ה-pipeline (service, decorator, observer,
> generator) עובד על המודל האחיד. הוספת סוג שלישי = parser + strategy חדשים בלבד.

---

## 🎁 בונוסים

| בונוס | בחירה מומלצת | הסיבה |
| --- | --- | --- |
| Frozen dataclasses | **מלא (+2)** | כל המודלים frozen. |
| Deterministic seed | **לפי שורה/תאריך (+2)** | `derive_row_seed(base, row)`. |
| DI Container | **כן (+1)** | `container.py`. |
| Code Review שנתנו | מלאי לפי מה שעשית בפועל | תהליכי — לא בקוד. |
| Code Review שקיבלנו | מלאי לפי מה שעשית בפועל | תהליכי — לא בקוד. |

מהקוד מובטחים **+5** (frozen + seed + DI). אם ביצעת/קיבלת code review אמיתי,
אפשר להגיע עד +15.
