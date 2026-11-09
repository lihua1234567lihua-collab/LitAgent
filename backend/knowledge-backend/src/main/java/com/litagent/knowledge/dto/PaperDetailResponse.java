package com.litagent.knowledge.dto;

public record PaperDetailResponse(
        Long id,
        String doi,
        String title,
        String pdfPath
) {}
