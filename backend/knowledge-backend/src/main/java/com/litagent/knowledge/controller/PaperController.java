package com.litagent.knowledge.controller;

import com.litagent.knowledge.entity.Paper;
import com.litagent.knowledge.service.PaperService;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import com.litagent.knowledge.dto.PaperDetailResponse;

import java.util.List;

@RestController
@RequestMapping("/papers")
public class PaperController {

    private final PaperService paperService;

    public PaperController(PaperService paperService) {
        this.paperService = paperService;
    }

    @GetMapping
    public List<Paper> getAllUsers() {
        return paperService.findAll();
    }

    @GetMapping("/{id}")
    public PaperDetailResponse getPaperById(@PathVariable Long id) {
        Paper paper = paperService.findById(id);

        return new PaperDetailResponse(
                paper.getId(),
                paper.getDoi(),
                paper.getTitle(),
                paper.getPdfPath()
        );
    }

    @PostMapping
    public Paper createUser(@RequestBody Paper paper){
        return paperService.createPaper(paper);
    }


}



