package com.litagent.knowledge.entity;
import jakarta.persistence.*;
@Entity 
@Table(name="papers")
public class Paper {
    @Id 
    @GeneratedValue (strategy=GenerationType.IDENTITY)
    private Long id;
    private String doi;
    private String title;
    @Column(name = "pdf_path", length = 1024)
    private String pdfPath;

    public Long getId() {
        return id;
    }

    public String getDoi() {
        return doi;
    }

    public String getTitle() {
        return title;
    }

    public String getPdfPath() {
        return pdfPath;
    }

    public void setDoi(String doi) {
    this.doi = doi;
}

    public void setTitle(String title) {
        this.title = title;
    }

    public void setPdfPath(String pdfPath) {
        this.pdfPath = pdfPath;
    }

}
