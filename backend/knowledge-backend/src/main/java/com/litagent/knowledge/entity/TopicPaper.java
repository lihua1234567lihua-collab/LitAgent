package com.litagent.knowledge.entity;
import jakarta.persistence.*;
@Entity 
@Table (name="topic_paper") 
public class TopicPaper {   
    @Id 
    @GeneratedValue (strategy=GenerationType.IDENTITY)
    private Long id;

    @ManyToOne 
    @JoinColumn (name="topic_id")
    private Topic topic;

    @ManyToOne 
    @JoinColumn (name="paper_id")
    private Paper paper;

    public void setTopic(Topic topic){
        this.topic=topic;
    }
    public void setPaper(Paper paper){
        this.paper=paper;
    }

    public Long getId(){
        return id;
    }
    public Topic getTopic(){
        return topic;
    }
    public Paper getPaper(){
        return paper;
    }

}
