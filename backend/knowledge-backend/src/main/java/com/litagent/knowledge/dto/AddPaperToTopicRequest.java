package com.litagent.knowledge.dto;

public class AddPaperToTopicRequest {

    private String doi;
    private String title;
    private String pdfPath;

    public AddPaperToTopicRequest() {
    }

    public String getDoi() {
        return doi;
    }

    public void setDoi(String doi) {
        this.doi = doi;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public String getPdfPath() {
        return pdfPath;
    }

    public void setPdfPath(String pdfPath) {
        this.pdfPath = pdfPath;
    }
}