package com.litagent.knowledge.repository;
import com.litagent.knowledge.entity.User;
import com.litagent.knowledge.entity.Paper;
import com.litagent.knowledge.entity.UserPaper;
import org.springframework.data.jpa.repository.JpaRepository;

public interface UserRepository extends JpaRepository<User, Long> {
   
}   
