package com.litagent.knowledge.controller;
import com.litagent.knowledge.service.TopicPaperService;
import com.litagent.knowledge.entity.TopicPaper;
import com.litagent.knowledge.entity.Paper;
import org.springframework.web.bind.annotation.*;
import java.util.List;
@RestController
@RequestMapping("/topicpaper")
public class TopicPaperController {
    private final TopicPaperService topicPaperService;
    public TopicPaperController(TopicPaperService topicPaperService){
        this.topicPaperService=topicPaperService;
    }
    @PostMapping
    public TopicPaper addTopicPaper(@RequestParam Long PaperId,@RequestParam Long TopicId){
        return topicPaperService.addTopicPaper(PaperId,TopicId);
    }

    @GetMapping("/{topicId}/papers")
    public List<Paper> getTopicPapers(@PathVariable Long topicId) {
        return topicPaperService.getTopicPapers(topicId);
    }

}
