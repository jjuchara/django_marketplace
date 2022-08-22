#!/bin/bash

# Сохраняем текущую ветку
current_branch=$(git rev-parse --abbrev-ref HEAD)

# Создаем новую ветку с нужной датой для первого коммита
export GIT_COMMITTER_DATE="2022-08-22 12:00:00"
export GIT_AUTHOR_DATE="2022-08-22 12:00:00"

# Начинаем с нового коммита с заданной датой
git checkout --orphan temp_branch
git add .
git commit -m "Initial commit"

# Форсируем push
git push -f origin temp_branch:master
git checkout -b new_master temp_branch
git branch -D temp_branch

# Заменяем оригинальную ветку нашей временной
git branch -D $current_branch
git checkout -b $current_branch

# Принудительно отправляем изменения на GitHub
echo "Изменения дат коммитов завершены. Теперь выполните:"
echo "git push -f origin $current_branch"