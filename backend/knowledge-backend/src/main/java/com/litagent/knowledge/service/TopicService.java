package com.litagent.knowledge.service;
import com.litagent.knowledge.entity.Topic;
import com.litagent.knowledge.entity.User;
import com.litagent.knowledge.repository.TopicRepository;
import com.litagent.knowledge.repository.UserRepository;
import org.springframework.stereotype.Service;
import java.util.List;
@Service 
public class TopicService {
    private final TopicRepository topicRepository;
    private final UserRepository userRepository;
    public TopicService(TopicRepository topicRepository,UserRepository userRepository){
        this.topicRepository=topicRepository;
        this.userRepository=userRepository;
    }
    public Topic createTopic(Long userId,String name){
        User user=userRepository.findById(userId).orElseThrow();
        Topic topic=new Topic();
        topic.setUser(user);
        topic.setName(name);
        return topicRepository.save(topic);
    }
    public List<Topic> getTopicsByUserId(Long userId) {

    userRepository.findById(userId)//返回所有的userid
            .orElseThrow(() -> new IllegalArgumentException("User not found"));

    return topicRepository.findByUser_Id(userId);//返回这个userid下的所有topic
}

}
