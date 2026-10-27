# Практическая работа: версионирование данных с DVC и ClearML

## Окружение

| Компонент | Версия |
|---|---|
| Python | 3.12 |
| pandas | 3.1.0 |
| scikit-learn | 1.9.1 |
| DVC | 3.67.1 |        
| ClearML | 2.1.12 |
| Poetry | 2.x (lock-файл зафиксирован) |

Установка через Poetry, зависимости зафиксированы в `pyproject.toml` и `poetry.lock`.

## Репозиторий

- Локальный Git-репозиторий: `mlops-data-gorskin`
- Основная ветка: `main`
- Ссылка на удалённый Git-репозиторий: https://github.com/c0ldblood3d/mlops-data-gorskin

---

# Часть 1. Подготовка таблиц

## Скрипты

- `prepare_data.py` — режимы `base`, `wine`, `iris_features`. Детерминизм: `sort_values(..., kind="mergesort")`, `index=False`, `float_format="%.10g"`, `lineterminator="\n"`.
- `check_data.py` — проверяет SHA-256, число строк/столбцов, отсутствие безымянного индекса, число NaN, корректность `sepal_area`/`petal_area` через `np.isclose(rtol=1e-9, atol=1e-12)`.

---

# Часть 2. DVC

## Git commits и tags

| Что | SHA / тег |
|---|---|
| `pin env` | `2805cd5` |
| `data-v1: base iris` | `5e18ff9` (tag: `data-v1`) |
| `configure local DVC remote` | `25690c4` (`main` до merge) |
| `feature/wine: add wine` | `178e0e5` (ветка `feature/wine`) |
| `feature/iris-features` | `5533a41` (ветка `feature/iris-features`) |
| Merge `feature/wine` → `feature/iris-features` | `6de62a6` (родители `5533a41`, `178e0e5`) |
| Merge `feature/iris-features` → `main` | `b6d5508407c677fcb4840d2543e4b0c3933c39ef` |

## Хэши `data.dvc` по версиям

| Версия | `.dir` md5 | size | nfiles |
|---|---|---:|---:|
| `data-v1` (`5e18ff9`) | `bf5656de288a783265cb7b85509abc8e.dir` | 2635 | 1 |
| `feature/wine` (`178e0e5`) | `f8fe844935c3e7d61c8736baacbf1018.dir` | 13938 | 2 |
| `feature/iris-features` (`5533a41`) | `c6a76d56d42022aa7753d44fd7e84d6a.dir` | 4230 | 1 |
| После merge (`957c42d7...`) | `957c42d7c9ecafed014287db892a5935.dir` | 15533 | 2 |

## SHA-256 итоговых CSV

| Файл | SHA-256 | Строк | Столбцов |
|---|---|---:|---:|
| `iris.csv` (база, `data-v1`) | `6d700503c9c2e2c71d187b889a87af8a8d3a6dd5bae1266d46f4ee4db5a6349f` | 150 | 5 |
| `iris.csv` (с `sepal_area`, `petal_area`) | `3e1ba63f55da2aabc432d00b1670140f5162bf9ef34b837598ec2fc176c9ff26` | 150 | 7 |
| `wine.csv` | `38860ba04ace4d402242340bcf40be4bd6f4ebde9144a3dc89dc12c20f7f8e60` | 178 | 14 |

## DVC remote

- Тип: локальная директория
- Путь: `/Users/coldblood3d/dvc-remote-mlops-data-gorskin` (вне репозитория)
- Настройка: `dvc remote add -d storage <путь>` (записана в `.dvc/config`, закоммичена)
- Объекты в remote видны: `ls ~/dvc-remote-mlops-data-gorskin/files/md5/` — присутствуют подкаталоги с объектами всех версий, включая объединённый `957c42d7c9ecafed014287db892a5935.dir`

## Слияние веток

- Слияние `feature/wine` в `feature/iris-features` прошло **автоматически** через DVC merge driver (`*.dvc merge=dvc` в `.gitattributes`, установленный через `dvc install`).
- Конфликтов в `data.dvc` не было: `grep '<<<<<<<\|=======\|>>>>>>>' data.dvc` → пусто.
- Merge-коммит `6de62a6` содержит только изменённый `data.dvc` (+3/−3).
- После слияния `dvc checkout` восстановил в workspace оба файла (`iris.csv` с признаками + `wine.csv`), `check_data.py` прошёл без ошибок.

## Чистое восстановление

- Клон: `git clone ./mlops-data-gorskin clean_check`
- Перед `dvc pull` удалён `.dvc/cache` (доказательство скачивания из remote)
- `dvc pull` → `3 files fetched and 2 files added`
- До `dvc pull`: `ls data/` пусто, `git ls-files | grep -i '\.csv$'` — пусто
- После `dvc pull`: оба CSV, `check_data.py` прошёл без ошибок
- SHA-256 в чистом clone совпадают с исходным репозиторием: `3e1ba63f...9ff26` и `38860ba0...f8e60`

---

# Часть 3. ClearML Dataset

## Имена

- project: `MIIT/MLOps/practice_3/gorskin`
- dataset name: `sklearn-tabular-gorskin`

## Dataset IDs

| Версия | ID | Parent |
|---|---|---|
| `1.0.0` | `43860cde07db46708b445c5099029dd8` | — |
| `1.1.0` | `86cee555f29c49029010359490ab86be` | `43860cde...` |
| `2.0.0` | `abcf4e51fcc74954925db169efb9c6aa` | `43860cde...` (не `WINE_ID`) |

## Dependency graph

Согласно веб-интерфейсу ClearML, версия `1.1.0` (Wine) и версия `2.0.0` (iris_features) образуют две независимые ветви, берущие начало от базовой версии `1.0.0` (base). Связи `1.1.0 -> 2.0.0` не существует. Все три версии имеют статус Final.

## Состав скачанных версий

### 1.0.0 (`BASE_ID`)
- Полный список файлов: `iris.csv`
- Added относительно parent: —
- Modified / Removed: —
- SHA-256: `iris.csv` = `6d700503c9c2e2c71d187b889a87af8a8d3a6dd5bae1266d46f4ee4db5a6349f`
- shape и columns: `(150, 5)`, columns = `[sepal length (cm), sepal width (cm), petal length (cm), petal width (cm), target]`

### 1.1.0 (`WINE_ID`)
- Полный список файлов: `iris.csv`, `wine.csv`
- Added относительно `BASE_ID`: `wine.csv`
- Modified / Removed: —
- SHA-256: `iris.csv` = `6d700503c9c2e2c71d187b889a87af8a8d3a6dd5bae1266d46f4ee4db5a6349f`, `wine.csv` = `38860ba04ace4d402242340bcf40be4bd6f4ebde9144a3dc89dc12c20f7f8e60`
- shape и columns: `iris.csv` = `(150, 5)`, `wine.csv` = `(178, 14)`

### 2.0.0 (`IRIS_FEATURES_ID`)
- Полный список файлов: `iris.csv`
- Added относительно `BASE_ID`: —
- Modified: `iris.csv`
- Removed: —
- SHA-256: `iris.csv` = `3e1ba63f55da2aabc432d00b1670140f5162bf9ef34b837598ec2fc176c9ff26`
- shape и columns: `(150, 7)`, columns = `[sepal length (cm), sepal width (cm), petal length (cm), petal width (cm), target, sepal_area, petal_area]`

---

# Часть 4. Сравнение

## Сравнительная таблица

| Критерий | DVC | ClearML Dataset |
|---|---|---|
| Идентификатор версии | `.dir` md5 в `data.dvc` (например, `957c42d7...`) | Dataset ID (например, `BASE_ID`) + version |
| Метаданные | `data.dvc` + `.dvc/config` в Git | На сервере ClearML |
| Расположение файлов | DVC cache + remote (`~/dvc-remote-mlops-data-gorskin`) | Storage сервера ClearML |
| Создание дочерней версии | `dvc add data` → commit `data.dvc` | `Dataset.create(parent_datasets=[parent_id])` |
| Переключение версии | `git switch <branch>` + `dvc checkout` (или `dvc pull`) | `Dataset.get(dataset_id=...)` + `get_mutable_local_copy(...)` |
| Восстановление на чистой машине | `git clone` + `dvc pull` (проверено: `3 files fetched and 2 files added`) | `Dataset.get(dataset_id=...)` + `get_mutable_local_copy(...)` |
| Поведение при ветвлении | Git-ветки + разные `.dvc` (проверено: 4 разных `.dir` md5) | Разные `parent_datasets` (две ветви от `BASE_ID`) |
| Поведение при слиянии | DVC merge driver объединил `.dvc` автоматически (`6de62a6`, без конфликтов) | Автоматического слияния нет; нужно создавать новую версию с несколькими parents или вручную |
| Связь версии данных с Git | Жёсткая: `.dvc`-файл коммитится, `git switch` меняет `.dvc` | Слабая: Dataset ID фиксируется в коде/отчёте, с конкретным коммитом не связан |
| Доступность через UI | Нет встроенного UI | Веб-интерфейс ClearML |

---

# Часть 5. Ответы на вопросы (раздел 15)

1. **Что однозначно определяет версию данных в DVC?**
   Хэш содержимого директории (`.dir` md5), записанный в `data.dvc`. Например, `957c42d7c9ecafed014287db892a5935.dir`. Именно этот хэш указывает на конкретный объект в DVC cache/remote.

2. **Почему одного Git-коммита недостаточно без DVC remote?**
   Git-коммит содержит только `.dvc`-файл с хэшем, но не сами данные. Восстановить CSV из этого хэша можно только из cache или remote. Если remote нет, а cache удалён (как при чистом клоне), — данные невосстановимы. Проверено: в чистом clone до `dvc pull` в `data/` пусто; после `dvc pull` данные пришли именно из remote.

3. **Чем Dataset version отличается от Dataset ID в ClearML?**
   Dataset ID — идентификатор конкретной версии-объекта в ClearML (то, что возвращает `Dataset.create()`). Понятие «version» (`1.0.0`, `1.1.0`, `2.0.0`) — это человекочитаемая метка внутри одного именованного датасета. Один и тот же `dataset_name` содержит несколько version, каждая со своим ID.

4. **Почему `finalize()` нельзя считать созданием следующей версии?**
   `finalize()` переводит текущую версию в статус Completed и делает её неизменяемой. Новая версия создаётся только через `Dataset.create()` с указанием `parent_datasets`. В работе это явно видно: `BASE_ID` финализирован, но `WINE_ID` и `IRIS_FEATURES_ID` — отдельные объекты, созданные через отдельные `Dataset.create`.

5. **Как доказать, что ClearML version `2.0.0` создана от базы, а не от `1.1.0`?**
   Через визуализацию Dependency graph в веб-интерфейсе ClearML (в SDK 2.1.12 метод `ds.parents` отсутствует, поэтому lineage проверялся через UI). На графе четко видно, что узлы `1.1.0` и `2.0.0` являются прямыми потомками `1.0.0` и не имеют связи между собой. Также в `list_modified_files()` у `2.0.0` есть `iris.csv`, а в `list_removed_files()` — пусто (если бы parent был `WINE_ID`, там бы оказался `wine.csv` в removed).

6. **Что произойдёт, если после `git switch` не выполнить DVC checkout?**
   Workspace останется с данными предыдущей ветки, а `data.dvc` будет указывать на новую версию. `dvc status` покажет расхождение (`modified: data`). Проверено: после `git switch main` и без `dvc checkout` в `data/` остался `wine.csv`, и `dvc status` показывал `modified: data`.

7. **В каком сценарии удобнее DVC, а в каком ClearML Dataset?**
   DVC — когда данные привязаны к Git-коммитам, важна воспроизводимость кода+данных и автоматическое слияние при мерже веток (проверено: merge driver сработал без конфликтов). ClearML — когда нужен lineage с ветвлением, веб-UI, доступ по ID с любой машины без Git-клонирования, а также наследование неизменённых файлов от parent без повторной загрузки.