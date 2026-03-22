# StaffFIlter_Backend


-----------------------
http://localhost:8080/swagger-ui/index.html#/%D0%A0%D0%B5%D0%B7%D1%8E%D0%BC%D0%B5/uploadAndProcess
для просмотра после запуска ResumeApplication.java

Описание файлов

ResumeApplication.java - Точка входа. Запускает Spring Boot приложение

ResumeController.java - Обрабатывает HTTP-запросы: загрузка файлов (эндпоинт /upload) и скачивание результата (эндпоинт /result)

FileStorageService.java -  Работа с файлами: сохранение, распаковка ZIP, чтение TXT, создание отчета

TaskService.java - Управление задачами: хранение статусов обработки в памяти с помощью хэш мапы

Task.java - Модель задачи: хранит ID, статус (PROCESSING/COMPLETED) и путь к файлу

UploadResponse.java - Формат ответа сервера при загрузке: { taskId, status, message }

Каждая загрузка архива и требований по своей сути представляет отдельную задачу, их мы и сохраняем в мапе. Файлы пользователя скачиваются в папку uploads, в папке uploads содержится подпапка с именем задачи
