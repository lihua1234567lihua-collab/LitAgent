package com.litagent.knowledge.controller;
import com.litagent.knowledge.entity.Topic;
import com.litagent.knowledge.service.TopicService;
import org.springframework.web.bind.annotation.*;
import java.util.List;
@RestController
@RequestMapping("/topics")
public class TopicController {
    private final TopicService topicService;
    public TopicController(TopicService topicService){
        this.topicService=topicService;
    }

    @PostMapping
    public Topic createTopic(@RequestParam Long userId,@RequestParam String name){
        return topicService.createTopic(userId,name);
    }

}
