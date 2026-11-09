package com.litagent.knowledge.repository;

import com.litagent.knowledge.entity.UserPaper;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
public interface UserPaperRepository extends JpaRepository<UserPaper, Long> {
   //判断用户是否已经收藏了指定论文
   boolean existsByUser_IdAndPaper_Id(Long userId,Long paperId);
   //查询用户收藏的所有论文关系
   List<UserPaper> findByUser_Id(Long userId);
}