package com.litagent.knowledge.service;

import com.litagent.knowledge.dto.AddPaperToTopicRequest;
import com.litagent.knowledge.dto.AddPaperToTopicResponse;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.litagent.knowledge.repository.*;
import com.litagent.knowledge.entity.*;


//用户：把这篇论文放到lidar树冠分割这个主题中，litagent已经知道topicid=1，然后把这篇论文和topic关联起来

@Service
public class PaperCollectionService {
     private final TopicRepository topicRepository;
        private final PaperRepository paperRepository;
        private final TopicPaperRepository topicPaperRepository;
        private final UserPaperRepository userPaperRepository;

        public PaperCollectionService(
            TopicRepository topicRepository, 
            PaperRepository paperRepository, 
            TopicPaperRepository topicPaperRepository, 
            UserPaperRepository userPaperRepository) {
            this.topicRepository = topicRepository;
            this.paperRepository = paperRepository;
            this.topicPaperRepository = topicPaperRepository;
            this.userPaperRepository = userPaperRepository;
        }

    @Transactional
    public AddPaperToTopicResponse addPaperToTopic(Long topicId, AddPaperToTopicRequest request) {//只负责往已有的Topic归档论文，不负责创建Topic

        Topic topic = topicRepository.findById(topicId)
                .orElseThrow(() -> new IllegalArgumentException("Topic not found"));

        User user = topic.getUser();

        Paper paper = paperRepository.findByDoi(request.getDoi())
                .orElseGet(() -> {
                    Paper newPaper = new Paper();
                    newPaper.setDoi(request.getDoi());
                    newPaper.setTitle(request.getTitle());
                    return paperRepository.save(newPaper);
                });
        
        // 如果请求提供了 PDF 路径，则更新论文记录
        String pdfPath = request.getPdfPath();

        if (pdfPath != null && !pdfPath.isBlank()
                && !pdfPath.equals(paper.getPdfPath())) {

            paper.setPdfPath(pdfPath);
            paperRepository.save(paper);
        }


        if (!userPaperRepository.existsByUser_IdAndPaper_Id(user.getId(), paper.getId())) {
            UserPaper userPaper = new UserPaper();
            userPaper.setUser(user);
            userPaper.setPaper(paper);
            userPaperRepository.save(userPaper);
        }

        if (!topicPaperRepository.existsByTopic_IdAndPaper_Id(topicId, paper.getId())) {
            TopicPaper topicPaper = new TopicPaper();
            topicPaper.setTopic(topic);
            topicPaper.setPaper(paper);
            topicPaperRepository.save(topicPaper);
        }
        return new AddPaperToTopicResponse(paper.getId(), topicId, user.getId(), paper.getDoi(), paper.getTitle());
    }
}