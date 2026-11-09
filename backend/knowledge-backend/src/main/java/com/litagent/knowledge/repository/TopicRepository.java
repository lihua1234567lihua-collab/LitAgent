package com.litagent.knowledge.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.litagent.knowledge.entity.Topic;
import java.util.List;

public interface TopicRepository extends JpaRepository<Topic, Long>{
    List<Topic> findByUser_Id(Long userId);
}
