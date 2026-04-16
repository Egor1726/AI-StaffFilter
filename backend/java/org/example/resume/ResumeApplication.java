package org.example.resume;

import jakarta.servlet.MultipartConfigElement;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.web.servlet.MultipartConfigFactory;
import org.springframework.context.annotation.Bean;
import org.springframework.util.unit.DataSize;

@SpringBootApplication
public class ResumeApplication {

    public static void main(String[] args) {
        SpringApplication.run(ResumeApplication.class, args);
    }

    @Bean
    public MultipartConfigElement multipartConfigElement() {
        MultipartConfigFactory factory = new MultipartConfigFactory();

        //лимит 500 МБ для файла
        factory.setMaxFileSize(DataSize.ofMegabytes(500));

        //лимит 500 МБ для всего запроса
        factory.setMaxRequestSize(DataSize.ofMegabytes(500));

        return factory.createMultipartConfig();
    }
}