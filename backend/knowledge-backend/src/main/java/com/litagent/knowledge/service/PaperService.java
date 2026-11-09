package com.litagent.knowledge.service;
import com.litagent.knowledge.entity.Paper;
import com.litagent.knowledge.repository.PaperRepository;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.util.List;
@Service //告诉spring这是业务逻辑层
public class PaperService {
    private final PaperRepository paperRepository;
    public PaperService(PaperRepository paperRepository){
        this.paperRepository=paperRepository;
    }
    public List<Paper> findAll(){
        return paperRepository.findAll();//查询user表里面的所有数据
    }
    public Paper findById(Long id) {
        return paperRepository.findById(id)
                .orElseThrow(() -> new ResponseStatusException(
                        HttpStatus.NOT_FOUND, "Paper not found"
                ));
    }
    public Paper createPaper(Paper paper){
        if(paperRepository.existsByDoi(paper.getDoi())){
            throw new IllegalStateException("paper already assigned to topic");
        }
        return paperRepository.save(paper);
    }
    public void deletePaper(long id){
        paperRepository.deleteById(id);
    }
}
