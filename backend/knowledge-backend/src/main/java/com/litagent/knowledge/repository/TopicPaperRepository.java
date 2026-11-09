package com.litagent.knowledge.repository;
import com.litagent.knowledge.entity.TopicPaper;
import com.litagent.knowledge.entity.Paper;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;
public interface TopicPaperRepository extends JpaRepository<TopicPaper,Long>{
    boolean existsByTopic_IdAndPaper_Id(Long topicId, Long paperId);
    List<TopicPaper> findByTopic_Id(Long topicId);
}
