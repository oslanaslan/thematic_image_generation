MADE Thematic Image Generation Project
==============================

Цель проекта - генерация стилизованных изображений на основе изображений, полученных от пользователя.
В результате исследований было разработано решение, состоящее из двух модулей

- Модуль генерации изображений без обучения кастомной модели
- [Модуль обучения](https://github.com/oslanaslan/thematic_image_generation/tree/main/src/custom_model_training) кастомной модели на основе изображений, полученных от пользователя

Модуль генерации без обучения не требует большого количества ресурсов для запуска, но результаты могут отличаться от того, что было подано на вход.
Модуль обучения кастомной модели лучше улавливает особенности черт лица пользователя, за счет чего позволяет генерировать более качественные изображения, но он также гораздо более требователен к вычислительным ресурсам.

Примеры сгенерированных изображений можно найти [тут](https://drive.google.com/drive/folders/11vkVXGQZGvtveEtN1_fw1C-u7xFyOa4n)

Project Organization
------------

Project organization based on [cookiecutter data science project template](https://drivendata.github.io/cookiecutter-data-science/).
All changes to this project are documented in the changelog.md file. Changelog format based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
This project adheres to [semantic versioning](https://semver.org/spec/v2.0.0.html).

Project Structure
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         the creator's initials, and a short `-` delimited description, e.g.
    │                         `1.0-jqp-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    └── src                <- Source code for use in this project.


--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
