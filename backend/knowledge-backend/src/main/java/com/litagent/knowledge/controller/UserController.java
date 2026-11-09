package com.litagent.knowledge.controller;

import com.litagent.knowledge.entity.Topic;
import com.litagent.knowledge.entity.User;
import com.litagent.knowledge.service.UserService;
import com.litagent.knowledge.service.UserPaperService;
import com.litagent.knowledge.service.TopicService;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;

import java.util.List;

@RestController
@RequestMapping("/users")
public class UserController {

    private final UserService userService;
    private final TopicService topicService;
    private final UserPaperService userPaperService;

    public UserController(UserService userService, TopicService topicService, UserPaperService userPaperService) {
        this.userService = userService;
        this.topicService = topicService;
        this.userPaperService = userPaperService;
    }

    @GetMapping
    public List<User> getAllUsers() {
        return userService.findAll();
    }

    @PostMapping
    public User createUser(@RequestBody User user){//表示前端发来的JSON直接被Jackson转成了User的Entity
        return userService.createUser(user);
    }

    @DeleteMapping("/{id}")
    public void deleteUser(@PathVariable long id){
        userService.deleteUser(id);
    }

    @PutMapping ("/{id}")
    public User updateUser(@PathVariable long id, @RequestBody User newUser){
        return userService.updateUser(id, newUser);
    }

    @GetMapping ("/{userId}/papers")
    public List<com.litagent.knowledge.entity.Paper> getUserPapers(@PathVariable Long userId){
        return userPaperService.getUserPapers(userId);
    }

    @GetMapping("/{userId}/topics")
    public List<Topic> getTopicsByUserId(@PathVariable Long userId){
        return topicService.getTopicsByUserId(userId);
    }
}

