DB_NAME="taskflow"
DB_USER="taskflow"
DB_HOST="localhost"
DB_PORT="5432"
BACKUP_DIR="./backups"

# Создаём папку
mkdir -p $BACKUP_DIR

# Генерируем имя файла с датой и временем
DATE=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="$BACKUP_DIR/db_backup_$DATE.sql"

# дамп
echo " Создаём бэкап: $BACKUP_FILE"
pg_dump -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_NAME -f $BACKUP_FILE

# Проверка
if [ $? -eq 0 ]; then
    echo "Бэкап успешно создан: $BACKUP_FILE"
else
    echo "Ошибка при создании бэкапа"
    exit 1
fi

# Удаляем старые бэкапы (старше 10 дней)
echo "Удаляем бэкапы старше 10 дней..."
find $BACKUP_DIR -name "db_backup_*.sql" -mtime +10 -delete
echo "Старые бэкапы удалены"