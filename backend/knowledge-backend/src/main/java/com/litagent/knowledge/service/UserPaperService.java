package com.litagent.knowledge.service;

import com.litagent.knowledge.repository.UserRepository;
import com.litagent.knowledge.repository.PaperRepository;
import com.litagent.knowledge.repository.UserPaperRepository;
import org.springframework.stereotype.Service;
import com.litagent.knowledge.entity.User;
import com.litagent.knowledge.entity.Paper;
import com.litagent.knowledge.entity.UserPaper;
import java.util.List;

@Service
public class UserPaperService {

    private final UserRepository userRepository;
    private final PaperRepository paperRepository;
    private final UserPaperRepository userPaperRepository;

    public UserPaperService(
            UserRepository userRepository,
            PaperRepository paperRepository,
            UserPaperRepository userPaperRepository) {

        this.userRepository = userRepository;
        this.paperRepository = paperRepository;
        this.userPaperRepository = userPaperRepository;
    }

    public List<UserPaper> findAll(){
        return userPaperRepository.findAll();//查询user表里面的所有数据
    }

    public UserPaper addPaperToUser(Long userId, Long paperId) {

        User user = userRepository.findById(userId).orElseThrow();

        Paper paper = paperRepository.findById(paperId).orElseThrow();

        UserPaper userPaper = new UserPaper();

        userPaper.setUser(user);
        userPaper.setPaper(paper);

        return userPaperRepository.save(userPaper);
    }

    public List<Paper> getUserPapers(Long userId){
        //1. 确认用户存在
        userRepository.findById(userId).orElseThrow(() -> new IllegalArgumentException("User not found with id: " + userId));
        //2. 查询用户收藏的所有论文关系
        List<UserPaper> userPapers = userPaperRepository.findByUser_Id(userId);
        //3. 提取论文信息
        return userPapers.stream().map(UserPaper::getPaper).toList();
    }

}