package org.example.resume.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.example.resume.dto.UploadResponse;
import org.example.resume.model.Task;
import org.example.resume.service.FileStorageService;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.HttpHeaders;
import java.io.File;

import java.io.IOException;

@RestController
@RequestMapping("/api/v1/resumes")
@CrossOrigin(origins = "*")
@Tag(name = "Резюме", description = "API для загрузки и обработки резюме")
public class ResumeController {

    private final FileStorageService fileStorageService;

    public ResumeController(FileStorageService fileStorageService) {
        this.fileStorageService = fileStorageService;
    }

    //Первый эндпоинт
    @PostMapping(value = "/upload", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @Operation(summary = "Загрузить и обработать резюме", description = "Принимает архив и требования, возвращает taskId")
    public ResponseEntity<UploadResponse> uploadAndProcess(
            @Parameter(description = "Архив с резюме (.zip)")
            @RequestParam("archive") MultipartFile archive,

            @Parameter(description = "Файл с требованиями (.txt)")
            @RequestParam("requirements") MultipartFile requirements
    ) throws IOException {
        if (archive.isEmpty() || requirements.isEmpty()) {
            return ResponseEntity.badRequest()
                    .body(new UploadResponse(null, "error", "Файлы не могут быть пустыми"));
        }

        if (!requirements.getOriginalFilename().endsWith(".txt")) {
            return ResponseEntity.badRequest()
                    .body(new UploadResponse(null, "error", "Требования должны быть в .txt файле"));
        }

        String taskId = fileStorageService.processResumes(archive, requirements);

        return ResponseEntity.ok(new UploadResponse(taskId, "COMPLETED", "Файлы обработаны"));
    }

    //Второй эндпоинт
    @GetMapping("/result/{taskId}")
    @Operation(summary = "Скачать результат", description = "Возвращает файл с отфильтрованными резюме")
    public ResponseEntity<?> downloadResult(@PathVariable String taskId) {

        Task task = fileStorageService.getTask(taskId);

        if (task == null) {
            return ResponseEntity
                    .status(404)
                    .body("Ошибка: Задача с ID '" + taskId + "' не найдена. Проверьте правильность ID.");
        }

        if (!"COMPLETED".equals(task.getStatus())) {
            return ResponseEntity
                    .status(400)
                    .body("Ошибка: Результат ещё не готов. Статус задачи: " + task.getStatus() + ". Пожалуйста, подождите.");
        }

        File file = new File(task.getResultFilePath());
        if (!file.exists()) {
            return ResponseEntity
                    .status(404)
                    .body("Ошибка: Файл результата был удален или поврежден на сервере.");
        }

        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"result.txt\"")
                .body(new FileSystemResource(file));
    }
}