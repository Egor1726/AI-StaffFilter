package org.example.resume.model;

public class Task {
    private String id;
    private String status;
    private String resultFilePath;

    public Task(String id, String status) {
        this.id = id;
        this.status = status;
    }

    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getStatus() { return status; }
    public void setStatus(String status) { this.status = status; }

    public String getResultFilePath() { return resultFilePath; }
    public void setResultFilePath(String resultFilePath) { this.resultFilePath = resultFilePath; }
}