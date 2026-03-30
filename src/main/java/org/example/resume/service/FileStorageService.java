package org.example.resume.service;

import org.example.resume.model.Task;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;
import java.util.stream.Collectors;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;
import org.example.resume.model.ResumeMatch;

@Service
public class FileStorageService {

    private final String uploadPath = "uploads";
    private final TaskService taskService;
    private final PdfParserService pdfParserService;

    public FileStorageService(TaskService taskService, PdfParserService pdfParserService) {
        this.taskService = taskService;
        this.pdfParserService = pdfParserService;
    }

    public String processResumes(MultipartFile archive, MultipartFile requirements) throws IOException {
        String taskId = UUID.randomUUID().toString();
        taskService.createTask(taskId);

        Path taskDir = Paths.get(uploadPath, taskId).toAbsolutePath().normalize();
        Files.createDirectories(taskDir);

        Path archivePath = taskDir.resolve("archive.zip");
        archive.transferTo(archivePath);

        Path requirementsPath = taskDir.resolve("requirements.txt");
        requirements.transferTo(requirementsPath);

        Path resumesDir = taskDir.resolve("resumes");
        Files.createDirectories(resumesDir);

        unzipArchive(archivePath, resumesDir);

        String requirementsRawText = readRequirements(requirementsPath);
        Set<String> keywords = parseRequirements(requirementsRawText);

        List<ResumeMatch> suitableResumes = pdfParserService.filterResumesByKeywords(resumesDir, keywords);

        Path resultPath = taskDir.resolve("result.txt");
        StringBuilder resultContent = new StringBuilder();

        resultContent.append("═══════════════════════════════════════════════════════════\n");
        resultContent.append("           ОТЧЁТ ПО ОБРАБОТКЕ РЕЗЮМЕ\n");
        resultContent.append("═══════════════════════════════════════════════════════════\n\n");

        resultContent.append("КЛЮЧЕВЫЕ СЛОВА ДЛЯ ПОИСКА:\n");
        resultContent.append("   ").append(keywords).append("\n\n");


        resultContent.append("НАЙДЕНО ПОДХОДЯЩИХ РЕЗЮМЕ: ").append(suitableResumes.size()).append("\n\n");

        if (suitableResumes.isEmpty()) {
            resultContent.append("Подходящих резюме не найдено.\n");
        } else {
            resultContent.append("═══════════════════════════════════════════════════════════\n");
            resultContent.append("                    СПИСОК РЕЗЮМЕ\n");
            resultContent.append("═══════════════════════════════════════════════════════════\n\n");

            int rank = 1;
            for (ResumeMatch match : suitableResumes) {
                resultContent.append("───────────────────────────────────────────────────────────\n");
                resultContent.append("№ ").append(rank).append(" | Файл: ").append(match.getFileName()).append("\n");
                resultContent.append("Совпадений с требованиями: ").append(match.getMatchCount()).append("\n");
                if (!match.getMatchedKeywords().isEmpty()) {
                    String skillsList = String.join(", ", match.getMatchedKeywords());
                    resultContent.append("Найдено совпадений: ").append(skillsList).append("\n");
                }

                resultContent.append("───────────────────────────────────────────────────────────\n\n");

                resultContent.append("СОДЕРЖИМОЕ РЕЗЮМЕ:\n\n");
                resultContent.append(match.getContent()).append("\n\n");

                rank++;
            }
        }

        Files.writeString(resultPath, resultContent.toString(), StandardCharsets.UTF_8);

        taskService.completeTask(taskId, resultPath.toString());

        return taskId;
    }

    private Set<String> parseRequirements(String requirementsText) {
        if (requirementsText == null || requirementsText.isBlank()) {
            return new LinkedHashSet<>();
        }

        String text = requirementsText.toLowerCase();

        String normalizedText = text
                .replaceAll("\\.", " ")
                .replaceAll(",", " ")
                .replaceAll("[()\\[\\]{}]", " ")
                .replaceAll("\\s+", " ");

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