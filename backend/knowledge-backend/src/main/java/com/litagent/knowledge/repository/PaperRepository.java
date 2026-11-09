package com.litagent.knowledge.repository;
import com.litagent.knowledge.entity.Paper;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;
public interface PaperRepository  extends JpaRepository<Paper, Long>{
    boolean existsByDoi(String doi);
    Optional<Paper>findByDoi(String doi);
}
