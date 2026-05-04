package org.example.resume.service;

import org.apache.pdfbox.pdmodel.PDDocument;
import org.apache.pdfbox.text.PDFTextStripper;
import org.example.resume.model.ResumeMatch;
import org.springframework.stereotype.Service;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.*;
import java.util.regex.Pattern;

@Service
public class PdfParserService {
    public List<ResumeMatch> filterResumesByKeywords(Path resumesDir, Set<String> keywords) {

        List<ResumeMatch> filteredResumes = new ArrayList<>();

        try {
            List<Path> pdfFiles = Files.walk(resumesDir)
                    .filter(Files::isRegularFile)
                    .filter(path -> path.toString().toLowerCase().endsWith(".pdf"))
                    .toList();

            for (Path pdfPath : pdfFiles) {
                String text = extractTextFromPdf(pdfPath.toFile());
                List<String> foundKeywords = findMatchingKeywords(text, keywords);

                if (!foundKeywords.isEmpty()) {
                    filteredResumes.add(new ResumeMatch(
                            pdfPath.getFileName().toString(),
                            foundKeywords.size(),
                            foundKeywords,
                            text
                    ));
                }
            }

        } catch (IOException e) {
            System.err.println("Error with filter");
        }

        filteredResumes.sort((a, b) -> Integer.compare(b.getMatchCount(), a.getMatchCount()));

        return filteredResumes;
    }


    private boolean matchesWholeWord(String text, String word) {
        Pattern pattern = Pattern.compile("\\b" + Pattern.quote(word) + "\\b");
        return pattern.matcher(text).find();
    }


    private String extractTextFromPdf(File pdfFile) throws IOException {
        try (PDDocument document = PDDocument.load(pdfFile)) {
            PDFTextStripper stripper = new PDFTextStripper();
            return stripper.getText(document);
        }
    }

    private List<String> findMatchingKeywords(String text, Set<String> keywords) {
        List<String> found = new ArrayList<>();

        if (text == null || text.isEmpty() || keywords.isEmpty()) {
            return found;
        }

        String normalizedText = text.toLowerCase();

        for (String keyword : keywords) {
            if (matchesWholeWord(normalizedText, keyword.toLowerCase())) {
                found.add(keyword);
            }
        }

        return found;
    }
}