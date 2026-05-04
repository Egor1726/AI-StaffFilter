package org.example.resume.model;

import java.util.List;

public class ResumeMatch {
    private final String fileName;
    private final int matchCount;
    private final String content;
    private final List<String> matchedKeywords;

    public ResumeMatch(String fileName, int matchCount,List<String> matchedKeywords, String content) {
        this.fileName = fileName;
        this.matchCount = matchCount;
        this.content = content;
        this.matchedKeywords = matchedKeywords;
    }

    public String getFileName() { return fileName; }
    public int getMatchCount() { return matchCount; }
    public String getContent() { return content; }
    public List<String> getMatchedKeywords() { return matchedKeywords; }
}