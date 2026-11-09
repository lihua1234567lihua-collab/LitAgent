package com.litagent.knowledge.service;
import com.litagent.knowledge.repository.TopicPaperRepository;
import com.litagent.knowledge.repository.PaperRepository;
import com.litagent.knowledge.repository.TopicRepository;
import com.litagent.knowledge.repository.UserPaperRepository;
import com.litagent.knowledge.entity.TopicPaper;
import com.litagent.knowledge.entity.Paper;
import com.litagent.knowledge.entity.Topic;
import com.litagent.knowledge.entity.User;
import com.litagent.knowledge.entity.UserPaper;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;//这个方法的数据库操作属于同一个事务，要么同时成功，要么同时失败
import java.util.List;
import java.util.stream.Collectors;
@Service 
public class TopicPaperService {
    private final TopicPaperRepository topicPaperRepository;
    private final PaperRepository paperRepository;
    private final TopicRepository topicRepository;
    private final UserPaperRepository userPaperRepository;
    public TopicPaperService(TopicPaperRepository topicPaperRepository,PaperRepository paperRepository,TopicRepository topicRepository,UserPaperRepository userPaperRepository){
        this.topicPaperRepository=topicPaperRepository;
        this.paperRepository=paperRepository;
        this.topicRepository=topicRepository;
        this.userPaperRepository=userPaperRepository;
    }
 @Transactional 
    public TopicPaper addTopicPaper(Long PaperId,Long TopicId){
       
        if(topicPaperRepository.existsByTopic_IdAndPaper_Id(TopicId,PaperId)){
        throw new IllegalStateException("paper already assigned to topic");
    }
        TopicPaper topicPaper=new TopicPaper();
        Paper paper=paperRepository.findById(PaperId).orElseThrow();
        Topic topic=topicRepository.findById(TopicId).orElseThrow();
        User user=topic.getUser();
        if(!userPaperRepository.existsByUser_IdAndPaper_Id(user.getId(),paper.getId())){//判断用户是否已经收藏过该paper，没有的话，就要收藏这篇论文
            UserPaper userpaper=new UserPaper();
            userpaper.setUser(user);
            userpaper.setPaper(paper);
            userPaperRepository.save(userpaper);
            throw new RuntimeException("Test transaction rollback");
        }
        topicPaper.setTopic(topic);
        topicPaper.setPaper(paper);
        return topicPaperRepository.save(topicPaper);
    }
    
    public List<Paper> getTopicPapers(Long topicId) {

        topicRepository.findById(topicId)
                .orElseThrow(() -> new IllegalArgumentException("Topic not found"));

        List<TopicPaper> relations =
                topicPaperRepository.findByTopic_Id(topicId);

        return relations.stream()
                .map(TopicPaper::getPaper)
                .toList();
    }
    
}
