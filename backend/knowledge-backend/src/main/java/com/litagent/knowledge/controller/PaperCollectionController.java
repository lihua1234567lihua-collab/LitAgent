package com.litagent.knowledge.controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.litagent.knowledge.dto.AddPaperToTopicResponse;
import com.litagent.knowledge.dto.AddPaperToTopicRequest;
import com.litagent.knowledge.service.*;

import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;


import java.util.List;
@RestController
@RequestMapping("/topics")
public class PaperCollectionController {
    private final PaperCollectionService paperCollectionService;
    public PaperCollectionController(PaperCollectionService paperCollectionService) {
        this.paperCollectionService = paperCollectionService;
    }
    @PostMapping("/{topicId}/papers")
    public AddPaperToTopicResponse addPaperToTopic(
        @PathVariable Long topicId,
        @RequestBody AddPaperToTopicRequest request) {//@pathVariable表示从url中拿topicid, @requestbody表示从json请求体里拿doi、title
            return paperCollectionService.addPaperToTopic(topicId, request);
    }
}
