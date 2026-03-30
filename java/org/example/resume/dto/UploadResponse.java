package org.example.resume.dto;


public class UploadResponse {
    private String taskId;
    private String status;
    private String message;

    public UploadResponse(String taskId, String status, String message) {
        this.taskId = taskId;
        this.status = status;
        this.message = message;
    }

    public String getTaskId() { return taskId; }
    public String getStatus() { return status; }
    public String getMessage() { return message; }
}
