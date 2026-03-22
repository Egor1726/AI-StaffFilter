package org.example.resume.service;

import org.example.resume.model.Task;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class TaskService {

    private final Map<String, Task> tasks = new HashMap<>();

    public Task createTask(String taskId) {
        Task task = new Task(taskId, "PROCESSING");
        tasks.put(taskId, task);
        return task;
    }

    public Task getTask(String taskId) {
        return tasks.get(taskId);
    }

    public void completeTask(String taskId, String resultFilePath) {
        Task task = tasks.get(taskId);
        if (task != null) {
            task.setStatus("COMPLETED");
            task.setResultFilePath(resultFilePath);
        }
    }
}