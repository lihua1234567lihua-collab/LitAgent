package com.litagent.knowledge.dto;

public class AddPaperToTopicResponse {

    private Long paperId;
    private Long topicId;
    private Long userId;
    private String doi;
    private String title;

    public AddPaperToTopicResponse(
            Long paperId,
            Long topicId,
            Long userId,
            String doi,
            String title) {
        this.paperId = paperId;
        this.topicId = topicId;
        this.userId = userId;
        this.doi = doi;
        this.title = title;
    }

    public Long getPaperId() {
        return paperId;
    }

    public Long getTopicId() {
        return topicId;
    }

    public Long getUserId() {
        return userId;
    }

    public String getDoi() {
        return doi;
    }

    public String getTitle() {
        return title;
    }
}