package com.litagent.knowledge.controller;

import com.litagent.knowledge.entity.UserPaper;
import com.litagent.knowledge.service.UserPaperService;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.HttpStatus;

import java.util.List;
@RestController
@RequestMapping("/user-papers")
public class UserPaperController {

    private final UserPaperService userPaperService;

    public UserPaperController(UserPaperService userPaperService) {
        this.userPaperService = userPaperService;
    }

    @GetMapping 
    public List<UserPaper> getAllUserPapers() {
        return userPaperService.findAll();
    }

    @PostMapping
    public UserPaper addPaperToUser(
            @RequestParam Long userId,
            @RequestParam Long paperId) {

        return userPaperService.addPaperToUser(userId, paperId);
    }
    
}