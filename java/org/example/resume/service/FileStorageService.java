package org.example.resume.service;

import org.example.resume.model.Task;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.Arrays;
import java.util.LinkedHashSet;
import java.util.Set;
import java.util.UUID;
import java.util.stream.Collectors;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

@Service
public class FileStorageService {

    private final String uploadPath = "uploads";
    private final TaskService taskService;

    public FileStorageService(TaskService taskService) {
        this.taskService = taskService;
    }

    public String processResumes(MultipartFile archive, MultipartFile requirements) throws IOException {
        // 1. Создаём задачу с ID
        String taskId = UUID.randomUUID().toString();
        taskService.createTask(taskId);

        // 2. Создаём папку для задачи
        Path taskDir = Paths.get(uploadPath, taskId).toAbsolutePath().normalize();
        Files.createDirectories(taskDir);

        // 3. Сохраняем архив
        Path archivePath = taskDir.resolve("archive.zip");
        archive.transferTo(archivePath);

        // 4. Сохраняем требования
        Path requirementsPath = taskDir.resolve("requirements.txt");
        requirements.transferTo(requirementsPath);

        // 5. Создаём отдельную папку для резюме
        Path resumesDir = taskDir.resolve("resumes");
        Files.createDirectories(resumesDir);

        // 6. Распаковываем архив
        unzipArchive(archivePath, resumesDir);

        // 7. Читаем и парсим требования
        String requirementsRawText = readRequirements(requirementsPath);
        Set<String> keywords = parseRequirements(requirementsRawText);

        // 8. Подготовка результата
        Path resultPath = taskDir.resolve("result.txt");
        Files.writeString(
                resultPath,
                "Ключевые слова успешно считаны: " + keywords,
                StandardCharsets.UTF_8
        );

        taskService.completeTask(taskId, resultPath.toString());

        return taskId;
    }

    private Set<String> parseRequirements(String requirementsText) {
        if (requirementsText == null || requirementsText.isBlank()) {
            return new LinkedHashSet<>();
        }

        String normalizedText = requirementsText.toLowerCase()
                .replaceAll("[^\\p{L}\\p{N}\\s]+", " ");

        return Arrays.stream(normalizedText.split("\\s+"))
                .map(String::trim)
                .filter(word -> !word.isEmpty())
                .collect(Collectors.toCollection(LinkedHashSet::new));
    }

    private void unzipArchive(Path archivePath, Path targetDir) throws IOException {
        Charset charset = Charset.forName("CP866");

        try (ZipInputStream zipInputStream = new ZipInputStream(Files.newInputStream(archivePath), charset)) {
            ZipEntry entry;

            while ((entry = zipInputStream.getNextEntry()) != null) {
                Path entryPath = targetDir.resolve(entry.getName()).normalize();

                if (!entryPath.startsWith(targetDir)) {
                    throw new IOException("Элемент ZIP-архива находится вне целевой директории");
                }

                if (entry.isDirectory()) {
                    Files.createDirectories(entryPath);
                } else {
                    Path parent = entryPath.getParent();
                    if (parent != null) {
                        Files.createDirectories(parent);
                    }

                    Files.copy(zipInputStream, entryPath, StandardCopyOption.REPLACE_EXISTING);
                }

                zipInputStream.closeEntry();
            }
        }
    }

    private String readRequirements(Path requirementsPath) throws IOException {
        return Files.readString(requirementsPath, StandardCharsets.UTF_8);
    }

    public Task getTask(String taskId) {
        return taskService.getTask(taskId);
    }
}